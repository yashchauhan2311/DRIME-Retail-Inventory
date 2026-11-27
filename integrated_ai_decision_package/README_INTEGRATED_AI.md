# Integrated AI Decision Center — setup

## What is new
- Adds **AI Decision Center** to the Streamlit navigation.
- Select a store and a date from the Random Forest holdout prediction period.
- Displays the saved Random Forest forecast and historical actual demand.
- Loads the existing PPO holdout model and its matching VecNormalize statistics.
- Executes a one-day historical replay for all three stores so cross-store transfers and the PPO observation sequence remain consistent; displays the selected store's action and outcome.
- Compares PPO with the revised rule-based baseline using the same date, seed, starting inventory logic and environment assumptions.
- Keeps existing dashboard pages and saved models/results.

## Important methodological note
The Random Forest prediction is displayed as a forecast reference. The PPO model was trained with the environment's seven-day historical mean observation, so the integration deliberately does **not** replace that PPO input with the Random Forest prediction. The dashboard shows PPO's original seven-day mean input separately.

This is a one-day **historical holdout replay**, not a future-date forecast or live deployment. The environment initializes starting stock from the selected historical day's demand, and both policies receive matched initial conditions. Profit is simulated operating profit (revenue minus COGS, holding, wastage, transfer and expedite costs); it excludes reward shaping/stockout penalties and is not actual retailer profit.

## Recommended setup
Use Python 3.11 in a fresh virtual environment. Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements_dashboard.txt
```

Run from this folder:

```bash
streamlit run app.py
```

## Notes
- Do not retrain or overwrite the PPO model.
- The Random Forest `.joblib` was serialized with scikit-learn 1.9.1; the requirements pin that version to reduce model-loading compatibility warnings.
- The PPO decision execution requires Gymnasium and Stable-Baselines3. The app reports missing dependencies or files if setup is incomplete.
