"""M5-capable retail inventory environment with chronological date controls."""
from pathlib import Path
import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces

DATA_PATH = Path(__file__).parent / "data" / "retail_demand.csv"

class RetailInventoryEnv(gym.Env):
    metadata = {"render_modes": ["human"]}
    ORDER_LEVELS = np.array([0, 10, 20, 30, 50], dtype=int)
    TRANSFER_LEVELS = np.array([0, 5, 10, 20], dtype=int)
    MARKDOWNS = np.array([0.0, 0.10, 0.20, 0.30, 0.40])
    SUPPLIERS = [
        {"name": "Supplier_A", "cost_factor": 1.00, "lead_time": 2, "reliability": 0.95},
        {"name": "Supplier_B", "cost_factor": 0.94, "lead_time": 4, "reliability": 0.88},
        {"name": "Supplier_C", "cost_factor": 1.08, "lead_time": 1, "reliability": 0.97},
    ]
    TRANSFER_COST_PER_UNIT = 1.5
    EXPEDITE_COST_PER_UNIT = 2.0
    STOCKOUT_PENALTY_FACTOR = 0.5
    SERVICE_REWARD = 10.0

    def __init__(self, product_id="FOODS_3_090",
                 data_path=Path(__file__).parent/"data"/"m5"/"m5_retail_env_ready.csv",
                 episode_days=60, seed=None, reward_config=None,
                 min_episode_demand=0, allowed_start_min=None,
                 allowed_start_max=None):
        super().__init__()
        self.data_path = Path(data_path)
        if not self.data_path.exists():
            raise FileNotFoundError(f"M5 data not found: {self.data_path}")
        self.data = pd.read_csv(self.data_path, parse_dates=["date"])
        self.data = self.data[self.data.product_id == product_id].copy()
        if self.data.empty:
            raise ValueError(f"Product {product_id!r} not found.")
        self.data.sort_values(["date","store_id"], inplace=True)
        self.dates = list(pd.to_datetime(sorted(self.data.date.unique())))
        self.stores = sorted(self.data.store_id.unique())
        self.n_stores = len(self.stores)
        self.product_id = product_id
        self.episode_days = min(int(episode_days), len(self.dates))
        if self.episode_days < 1: raise ValueError("episode_days must be >= 1")
        self.min_episode_demand = int(min_episode_demand)
        self.allowed_start_min = pd.Timestamp(allowed_start_min) if allowed_start_min else self.dates[0]
        self.allowed_start_max = pd.Timestamp(allowed_start_max) if allowed_start_max else self.dates[-1]
        max_start = len(self.dates) - self.episode_days
        valid = []
        daily = self.data.groupby("date").demand_units.sum().reindex(self.dates, fill_value=0).to_numpy()
        rolling = np.convolve(daily, np.ones(self.episode_days, dtype=np.int64), mode="valid")
        for i in range(max_start + 1):
            start_date = self.dates[i]
            end_date = self.dates[i + self.episode_days - 1]
            if start_date >= self.allowed_start_min and end_date <= self.allowed_start_max and rolling[i] >= self.min_episode_demand:
                valid.append(i)
        self.episode_start_candidates = np.asarray(valid, dtype=int)
        if not len(valid):
            raise ValueError("No valid episode starts in the configured date range. Check dates, episode_days and min_episode_demand.")
        self.rng = np.random.default_rng(seed)
        self.reward_config = {"stockout_penalty_factor": self.STOCKOUT_PENALTY_FACTOR, "service_reward": self.SERVICE_REWARD}
        if reward_config: self.reward_config.update(reward_config)
        def validate(v, name):
            vals = v if isinstance(v,(list,tuple,np.ndarray)) else [v]
            if any(float(x)<0 for x in vals): raise ValueError(f"{name} must be non-negative")
            if len(vals)>1 and len(vals)!=self.n_stores: raise ValueError(f"{name} must be scalar or have {self.n_stores} values")
        validate(self.reward_config["stockout_penalty_factor"], "stockout_penalty_factor")
        validate(self.reward_config["service_reward"], "service_reward")
        def weight(name, i):
            v=self.reward_config[name]
            return float(v[i] if isinstance(v,(list,tuple,np.ndarray)) else v)
        self._weight_for_store=weight
        obs_len=2*self.n_stores+7
        self.observation_space=spaces.Box(0,1e6,shape=(obs_len,),dtype=np.float32)
        self.action_space=spaces.MultiDiscrete([len(self.ORDER_LEVELS),self.n_stores+1,len(self.TRANSFER_LEVELS),len(self.MARKDOWNS),len(self.SUPPLIERS),2])
        self.reset(seed=seed)

    def _row(self, day_index, store_index):
        date=self.dates[day_index]; store=self.stores[store_index]
        rows=self.data[(self.data.date==date)&(self.data.store_id==store)]
        if rows.empty: raise RuntimeError(f"Missing row for {date}/{store}")
        return next(rows.itertuples(index=False))

    def _inventory(self,i): return int(sum(x[0] for x in self.lots[i]))

    def _minimum_remaining_shelf_life(self,i,shelf_life):
        lives=[shelf_life-age for qty,age,cost in self.lots[i] if qty>0]
        return float(max(0,min(lives))) if lives else 0.0

    def _obs(self):
        t=self.focus_store; row=self._row(self.day,t)
        prior=self.dates[max(0,self.day-7):self.day]
        hist=self.data[(self.data.store_id==self.stores[t])&self.data.date.isin(prior)]
        forecast=float(hist.demand_units.mean()) if not hist.empty else float(self.data[self.data.store_id==self.stores[t]].head(7).demand_units.mean())
        vals=[self._inventory(i) for i in range(self.n_stores)]+[float(i==t) for i in range(self.n_stores)]+[
            forecast,self._minimum_remaining_shelf_life(t,int(row.shelf_life_days)),
            float(row.competitor_price),float(row.supplier_lead_time_days),
            float(row.storage_cost_per_unit_day),float(row.festival_indicator),
            float(sum(q for a,q,c in self.pipeline[t]))]
        return np.asarray(vals,dtype=np.float32)

    def reset(self,*,seed=None,options=None):
        super().reset(seed=seed)
        if seed is not None:
            self.rng=np.random.default_rng(seed); reliability_seed=int(seed)+1_000_003
        else:
            s=int(self.np_random.integers(0,2**32-1)); self.rng=np.random.default_rng(s); reliability_seed=s+1_000_003
        rr=np.random.default_rng(reliability_seed)
        self.supplier_uniforms=rr.random((len(self.dates),self.n_stores))
        options=options or {}
        if "start_date" in options:
            requested=pd.Timestamp(options["start_date"])
            matches=[i for i in self.episode_start_candidates if self.dates[i]==requested]
            if not matches: raise ValueError(f"Requested start date {requested.date()} is not a valid start in configured range.")
            self.episode_start_day=int(matches[0])
        else:
            self.episode_start_day=int(self.rng.choice(self.episode_start_candidates))
        end=self.episode_start_day+self.episode_days
        self.episode_demand_total=int(self.data[self.data.date.isin(self.dates[self.episode_start_day:end])].demand_units.sum())
        self.day=self.episode_start_day; self.focus_store=0; self.last_supplier=0
        self.lots=[[] for _ in range(self.n_stores)]; self.pipeline=[[] for _ in range(self.n_stores)]
        self.current_prices={}
        for i in range(self.n_stores):
            row=self._row(self.day,i); self.lots[i].append([max(0,int(row.demand_units*1.5)),0,float(row.unit_purchase_cost)])
            self.current_prices[i]=float(row.retail_price)
        return self._obs(),{"stores":self.stores,"product_id":self.product_id,"episode_start_day":self.episode_start_day,
            "episode_start_date":self.dates[self.episode_start_day].date().isoformat(),"episode_demand_total":self.episode_demand_total}

    def _take_oldest(self,i,quantity):
        rem=int(quantity); moved=[]; self.lots[i].sort(key=lambda x:x[1],reverse=True)
        for lot in self.lots[i]:
            if rem<=0: break
            take=min(int(lot[0]),rem)
            if take: moved.append([take,int(lot[1]),float(lot[2])]); lot[0]-=take; rem-=take
        self.lots[i]=[x for x in self.lots[i] if x[0]>0]
        return moved

    def step(self,action):
        if not self.action_space.contains(np.asarray(action)): raise ValueError(f"Invalid action {action}")
        oi,sc,ti,mi,si,exp=map(int,action); target=self.focus_store; row=self._row(self.day,target)
        supplier=self.SUPPLIERS[si]; reward=0.0
        transfer_requested=int(self.TRANSFER_LEVELS[ti]); source=sc-1 if sc>0 else None; actual_transfer=0
        if source is not None and source!=target and transfer_requested>0:
            moved=self._take_oldest(source,min(transfer_requested,self._inventory(source))); self.lots[target].extend(moved)
            actual_transfer=sum(x[0] for x in moved); reward-=actual_transfer*self.TRANSFER_COST_PER_UNIT
        order_qty=int(self.ORDER_LEVELS[oi]); unit_cost=float(row.unit_purchase_cost)*float(supplier["cost_factor"])
        lead=max(1,int(supplier["lead_time"]-(1 if exp else 0)))
        if exp and order_qty>0: reward-=order_qty*self.EXPEDITE_COST_PER_UNIT
        if order_qty>0:
            arrival=self.day+lead
            if self.supplier_uniforms[self.day,target]>supplier["reliability"]: arrival+=1
            self.pipeline[target].append((arrival,order_qty,unit_cost))
        markdown=float(self.MARKDOWNS[mi]); base_price=float(row.retail_price); base_cost=float(row.unit_purchase_cost)
        selling_price=max(base_cost,base_price*(1-markdown)); self.current_prices[target]=selling_price
        received=0; pending=[]
        for arrival,qty,cost in self.pipeline[target]:
            if arrival<=self.day: self.lots[target].append([int(qty),0,float(cost)]); received+=int(qty)
            else: pending.append((arrival,qty,cost))
        self.pipeline[target]=pending
        demand=int(row.demand_units); effective=max(0,int(round(demand*(1+0.8*markdown))))
        inv_before=self._inventory(target); sold=min(inv_before,effective); unmet=max(0,effective-sold); revenue=sold*selling_price
        remaining=sold; cogs=0.0; self.lots[target].sort(key=lambda x:x[1],reverse=True)
        for lot in self.lots[target]:
            take=min(int(lot[0]),remaining)
            if take>0: lot[0]-=take; remaining-=take; cogs+=take*float(lot[2])
            if remaining<=0: break
        self.lots[target]=[x for x in self.lots[target] if x[0]>0]
        expired=0; waste=0.0; shelf=int(row.shelf_life_days)
        for lot in self.lots[target]: lot[1]+=1
        if shelf<365:
            keep=[]
            for qty,age,cost in self.lots[target]:
                if age>=shelf: expired+=int(qty); waste+=int(qty)*float(cost)
                else: keep.append([int(qty),int(age),float(cost)])
            self.lots[target]=keep
        inv_end=self._inventory(target); holding=inv_end*float(row.storage_cost_per_unit_day)
        stockout=unmet*float(row.retail_price)*self._weight_for_store("stockout_penalty_factor",target)
        service=sold/effective if effective else 1.0
        reward+=revenue-cogs-holding-waste-stockout+self._weight_for_store("service_reward",target)*service
        info={"date":pd.Timestamp(self.dates[self.day]).date().isoformat(),"focus_store":self.stores[target],"product_id":self.product_id,
            "base_demand":demand,"demand":effective,"units_sold":sold,"unmet_demand":unmet,"inventory_end":inv_end,
            "order_quantity":order_qty,"transfer_quantity":actual_transfer,"transfer_source":self.stores[source] if source is not None and source!=target else None,
            "markdown_pct":markdown,"supplier":supplier["name"],"supplier_lead_time":lead,"expedited":bool(exp),
            "units_expired":expired,"revenue":round(revenue,2),"cost_of_goods_sold":round(cogs,2),"holding_cost":round(holding,2),
            "wastage_cost":round(waste,2),"transfer_cost":round(actual_transfer*self.TRANSFER_COST_PER_UNIT,2),
            "expedite_cost":round(order_qty*self.EXPEDITE_COST_PER_UNIT if exp else 0.0,2),"stockout_penalty":round(stockout,2),
            "service_level":round(service,4),"reward":round(float(reward),2),"received_units":received,
            "pipeline_units_end":int(sum(q for a,q,c in self.pipeline[target]))}
        self.focus_store+=1; terminated=False
        if self.focus_store>=self.n_stores:
            self.focus_store=0; self.day+=1
            if self.day>=self.episode_start_day+self.episode_days or self.day>=len(self.dates): terminated=True
        obs=np.zeros(self.observation_space.shape,dtype=np.float32) if terminated else self._obs()
        return obs,float(reward),terminated,False,info
    def render(self): print({"day_index":self.day,"focus_store":self.stores[self.focus_store] if self.day<len(self.dates) else None,
        "inventories":{self.stores[i]:self._inventory(i) for i in range(self.n_stores)}})
