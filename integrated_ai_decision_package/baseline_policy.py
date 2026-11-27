"""Transparent rule-based retail inventory policy with store-specific safety stock."""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class BaselineConfig:
    # Fallback used when store_safety_days is None.
    safety_days: float = 1.0
    # Values are indexed by the store's position in env's inventory vector.
    # Example for three stores: (2.5, 2.5, 3.0).
    store_safety_days: tuple | None = None
    festival_safety_days: float = 0.5
    transfer_trigger_cover: float = 1.25
    source_buffer_days: float = 2.0
    expedite_cover_days: float = 1.0
    markdown_short_shelf_days: int = 2
    markdown_long_shelf_days: int = 4


def _nearest_level(value, levels):
    return int(np.argmin(np.abs(np.asarray(levels, dtype=float) - float(value))))


def baseline_action(env, observation, config=None):
    """Return a feasible MultiDiscrete action.

    Action: [order_level, transfer_source_code, transfer_level,
             markdown_level, supplier_index, expedited_flag].
    """
    cfg = config or BaselineConfig()
    obs = np.asarray(observation, dtype=float)
    n = env.n_stores
    inventories = obs[:n]
    store_flags = obs[n:2*n]
    target = int(np.argmax(store_flags))
    forecast = max(1.0, float(obs[2*n]))
    remaining_shelf_life = max(1.0, float(obs[2*n + 1]))
    festival = float(obs[2*n + 5])
    current_stock = float(inventories[target])
    pipeline_units = max(0.0, float(obs[2*n + 6]))
    inventory_position = current_stock + pipeline_units

    suppliers = env.SUPPLIERS
    typical_lead = max(1.0, float(obs[2*n + 3]))
    urgent = inventory_position < forecast * (typical_lead + 0.5)
    supplier_index = min(
        range(len(suppliers)),
        key=lambda j: suppliers[j]["lead_time"] if urgent
        else suppliers[j]["cost_factor"],
    )
    supplier = suppliers[supplier_index]
    effective_lead = max(1, int(supplier["lead_time"]))

    if cfg.store_safety_days is not None:
        if len(cfg.store_safety_days) != n:
            raise ValueError(
                f"store_safety_days must contain {n} values; "
                f"received {len(cfg.store_safety_days)}"
            )
        base_safety_days = float(cfg.store_safety_days[target])
    else:
        base_safety_days = float(cfg.safety_days)

    safety_days = base_safety_days + (
        cfg.festival_safety_days if festival else 0.0
    )
    target_stock = forecast * (effective_lead + safety_days)
    desired_order = max(0.0, target_stock - inventory_position)
    order_idx = _nearest_level(desired_order, env.ORDER_LEVELS)
    order_qty = int(env.ORDER_LEVELS[order_idx])

    source_code = 0
    transfer_idx = 0
    if current_stock < forecast * cfg.transfer_trigger_cover:
        candidates = []
        for i in range(n):
            if i == target:
                continue
            source_surplus = float(inventories[i]) - forecast * cfg.source_buffer_days
            if source_surplus >= min(env.TRANSFER_LEVELS[1:]):
                candidates.append((source_surplus, i))
        if candidates:
            surplus, source = max(candidates)
            requested = min(surplus, float(env.TRANSFER_LEVELS[-1]))
            transfer_idx = _nearest_level(requested, env.TRANSFER_LEVELS)
            if env.TRANSFER_LEVELS[transfer_idx] > 0:
                source_code = source + 1

    stock_cover = current_stock / forecast
    if remaining_shelf_life <= cfg.markdown_short_shelf_days and stock_cover > 1.0:
        markdown_idx = 2
    elif remaining_shelf_life <= cfg.markdown_long_shelf_days and stock_cover > 2.0:
        markdown_idx = 1
    else:
        markdown_idx = 0

    expedited = int(order_qty > 0 and current_stock < forecast * effective_lead)

    return np.asarray(
        [order_idx, source_code, transfer_idx, markdown_idx, supplier_index, expedited],
        dtype=np.int64,
    )
