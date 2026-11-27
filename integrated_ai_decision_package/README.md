# Dynamic Retail Inventory & Markdown Engine
## Integrated AI Decision Center — Team Project Package

This folder contains the Streamlit dashboard, forecasting artifacts, PPO policy and normalization statistics, simulation environment, rule-based baseline, datasets, and saved evaluation outputs.

> **Project status:** Research prototype using historical M5 data and illustrative simulation assumptions. It is not a live Walmart system and does not use Walmart internal operational data.

## 1. What's included

- `app.py` — Streamlit dashboard with Executive Overview, AI Decision Center, Demand Forecasting, Inventory Analytics, Policy Comparison, and Project & Data pages.
- `integrated_decision.py` — one-day historical holdout replay comparing the saved PPO policy with the revised rule-based baseline.
- `retail_rl_env.py` — Gymnasium retail inventory simulation environment.
- `baseline_policy.py` — transparent rule-based comparison policy.
- `models/retail_ppo_M5_HOLDOUT.zip` — trained PPO model.
- `models/retail_vecnormalize_M5_HOLDOUT.pkl` — matching observation/reward normalization statistics.
- `forecasting_outputs/random_forest_demand_model.joblib` — saved Random Forest forecasting model.
- `forecasting_outputs/` — saved predictions and model-comparison metrics.
- `data/m5/` — processed M5 dataset and environment-ready dataset.
- `m5_*.csv`, `final_policy_comparison.csv` (if present) — saved evaluation and robustness outputs.
- `requirements.txt` — Python dependencies.

## 2. Setup

Use **Python 3.11** and create a fresh virtual environment from this project folder.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run the commands below instead from Command Prompt:

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. Run the dashboard

Make sure the terminal's current directory is this folder (the folder containing `app.py`), then run:

```bash
streamlit run app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`, which you can open in a browser.

## 4. AI Decision Center — what it does

1. Select a store and a date from the saved Random Forest holdout prediction period.
2. The dashboard displays the saved Random Forest prediction alongside historical actual demand.
3. It loads the saved PPO model and its matching VecNormalize statistics.
4. It runs a one-day historical replay for the three stores so the cross-store transfer logic and PPO observation sequence remain consistent.
5. It compares PPO and the revised rule-based baseline using matched date, seed, initial-state logic, and environment assumptions.

### Important methodology notes

- The Random Forest prediction is displayed as a forecast reference. It is **not** passed into PPO. PPO uses the environment's original seven-day historical mean-demand observation; the dashboard displays that input separately.
- This is a **one-day historical holdout replay**, not a future-date forecast or live deployment.
- Starting inventory is initialized by the simulation environment using the selected historical day's demand. Both policies use the same date, seed, and environment assumptions.
- Operating profit is simulated as revenue minus cost of goods sold, holding cost, wastage cost, transfer cost, and expedite cost. It excludes reward shaping and stockout penalties. It is not actual retailer profit.
- Do not retrain or overwrite the supplied PPO model or VecNormalize file when running the dashboard.

## 5. Model and evaluation context

The supplied forecasting evaluation used a chronological 80/20 split and rolling one-day-ahead evaluation. Saved Random Forest results: MAE 11.997, RMSE 17.301, WAPE 31.71%. The comparison results in the dashboard are the saved experiment outputs; they should not be described as proof that PPO wins on every metric.

The robustness evaluation used five seeds, three selected 60-day windows, and two policies (30 episodes total). In the saved results, the revised baseline had higher mean operating profit and zero expired units, while PPO had a slightly higher fill rate and slightly lower unmet demand. Refer to the CSV outputs for the exact metric values and scope.

## 6. Troubleshooting

- **`ModuleNotFoundError`:** Activate the project's virtual environment and rerun `python -m pip install -r requirements.txt`.
- **Model-loading / scikit-learn warning:** The saved Random Forest artifact was serialized with scikit-learn 1.9.1; keep the version pinned in `requirements.txt`.
- **AI Decision Center reports missing files:** Run Streamlit from this project folder and keep the supplied `data/`, `models/`, and `forecasting_outputs/` directories in their original locations.
- **PPO dependency errors:** Confirm that `gymnasium` and `stable-baselines3` installed successfully in the same environment used to launch Streamlit.
- **Port already in use:** Run `streamlit run app.py --server.port 8502`.

## 7. Sharing with teammates

Share the complete ZIP, not just `app.py`. Ask each teammate to extract the ZIP, open a terminal in the extracted project folder, follow the setup instructions above, and run the dashboard. Do not rename or move the model/data subfolders unless the corresponding paths in the code are also updated.

## Updated dashboard interface

The dashboard now uses a dark navy enterprise-style interface with purple/blue/cyan accents, refined typography, improved navigation, polished KPI cards, and dark Plotly charts. The update is presentation-layer only: the forecasting, PPO, baseline, simulation, evaluation calculations, saved model files, and source datasets are retained.

Run from this folder:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Recommended environment: Python 3.11.
