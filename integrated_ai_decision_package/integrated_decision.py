"""One-day historical replay for the integrated retail decision dashboard."""
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

ROOT = Path(__file__).resolve().parent


def _action_labels(env, action):
    oi, source_code, ti, mi, si, expedited = map(int, action)
    source = env.stores[source_code - 1] if source_code > 0 else "None"
    supplier = env.SUPPLIERS[si]
    return {
        "Order quantity": int(env.ORDER_LEVELS[oi]),
        "Transfer source": source,
        "Transfer quantity": int(env.TRANSFER_LEVELS[ti]),
        "Markdown": f"{env.MARKDOWNS[mi] * 100:.0f}%",
        "Supplier": supplier["name"],
        "Supplier lead time": f"{max(1, int(supplier['lead_time'] - (1 if expedited else 0)))} day(s)",
        "Expedited shipping": "Yes" if expedited else "No",
    }


def _run_env(env, action):
    _, reward, terminated, truncated, info = env.step(np.asarray(action, dtype=np.int64))
    info = dict(info)
    info["operating_profit"] = (
        info["revenue"] - info["cost_of_goods_sold"] - info["holding_cost"]
        - info["wastage_cost"] - info["transfer_cost"] - info["expedite_cost"]
    )
    info["environment_reward"] = float(reward)
    return info


def run_comparison(store_id: str, date_value, root: Path = ROOT):
    """Run PPO and revised baseline from matched, fresh one-day historical states."""
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
    from retail_rl_env import RetailInventoryEnv
    from baseline_policy import BaselineConfig, baseline_action

    date_value = pd.Timestamp(date_value).normalize()
    data_path = root / "data/m5/m5_retail_env_ready.csv"
    model_path = root / "models/retail_ppo_M5_HOLDOUT.zip"
    norm_path = root / "models/retail_vecnormalize_M5_HOLDOUT.pkl"
    for path in (data_path, model_path, norm_path):
        if not path.exists():
            raise FileNotFoundError(f"Required project file not found: {path.relative_to(root)}")

    # A single-date allowed range makes reset deterministic without changing the env.
    def make_env():
        return RetailInventoryEnv(
            product_id="FOODS_3_090", data_path=data_path, episode_days=1,
            seed=2026, allowed_start_min=date_value, allowed_start_max=date_value,
        )

    # Load the exact VecNormalize statistics used during PPO holdout evaluation.
    raw_env = make_env()
    raw_obs, _ = raw_env.reset(seed=2026, options={"start_date": date_value})
    vec_env = DummyVecEnv([make_env])
    normalized_env = VecNormalize.load(str(norm_path), vec_env)
    normalized_env.training = False
    normalized_env.norm_reward = False
    normalized_env.seed(2026)
    model = PPO.load(str(model_path), env=normalized_env, device="cpu")
    normalized_obs = normalized_env.reset()

    ppo_rows = []
    for _ in range(raw_env.n_stores):
        ppo_action, _state = model.predict(normalized_obs, deterministic=True)
        ppo_action = np.asarray(ppo_action).reshape(-1).astype(np.int64)
        ppo_forecast_input = float(raw_obs[2 * raw_env.n_stores])
        raw_obs, _reward_raw, terminated, _truncated, info = raw_env.step(ppo_action)
        normalized_obs, _reward_vec, _dones, _infos = normalized_env.step(ppo_action.reshape(1, -1))
        row = dict(info)
        row["operating_profit"] = (
            row["revenue"] - row["cost_of_goods_sold"] - row["holding_cost"]
            - row["wastage_cost"] - row["transfer_cost"] - row["expedite_cost"]
        )
        row["ppo_internal_forecast_input_7d_mean"] = ppo_forecast_input
        row["action"] = ppo_action.copy()
        ppo_rows.append(row)
        if terminated:
            break

    # Separate fresh environment, same date and seed: matched initial inventory and delay draw.
    baseline_env = make_env()
    baseline_obs, _ = baseline_env.reset(seed=2026, options={"start_date": date_value})
    cfg = BaselineConfig(store_safety_days=(2.0, 2.0, 1.5), expedite_cover_days=1.0)
    baseline_rows = []
    for _ in range(baseline_env.n_stores):
        action = baseline_action(baseline_env, baseline_obs, cfg)
        baseline_obs, reward, terminated, _, info = baseline_env.step(action)
        row = dict(info)
        row["operating_profit"] = (
            row["revenue"] - row["cost_of_goods_sold"] - row["holding_cost"]
            - row["wastage_cost"] - row["transfer_cost"] - row["expedite_cost"]
        )
        row["environment_reward"] = float(reward)
        row["action"] = action.copy()
        baseline_rows.append(row)
        if terminated:
            break

    # Close vectorized resources.
    normalized_env.close()
    raw_env.close()
    baseline_env.close()
    ppo_row = next((r for r in ppo_rows if r["focus_store"] == store_id), None)
    baseline_row = next((r for r in baseline_rows if r["focus_store"] == store_id), None)
    if ppo_row is None or baseline_row is None:
        raise ValueError(f"Selected store {store_id} was not present in the simulation.")
    labels_env = make_env()
    ppo_labels = _action_labels(labels_env, ppo_row.pop("action"))
    baseline_labels = _action_labels(labels_env, baseline_row.pop("action"))
    labels_env.close()

    return {
        "date": date_value,
        "store": store_id,
        "ppo_action": ppo_labels,
        "baseline_action": baseline_labels,
        "ppo": ppo_row,
        "baseline": baseline_row,
    }
