from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Retail Intelligence | Inventory & Markdown", page_icon="📦", layout="wide")
px.defaults.template = "plotly_white"

# ═══════════════════════════════════════════════════════════════════
#  GLOBAL STYLES — Warm Cream, Alabaster & Cashmere Palette
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Manrope:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:           #FAF7F2;
  --bg2:          #F3ECE2;
  --panel:        #FFFFFF;
  --panel2:       #F8F4EE;
  --line:         rgba(195, 178, 155, 0.40);
  --line-strong:  rgba(180, 160, 135, 0.65);
  --muted:        #736B63;
  --text:         #28231D;
  --heading:      #1C1713;
  --terracotta:   #C85A32;
  --amber:        #D97706;
  --navy:         #284B63;
  --sage:         #2E6B47;
  --rose:         #BE123C;
}

/* ── App Shell & Base ── */
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif;
}

.stApp {
  background:
    radial-gradient(ellipse at 12% -4%, rgba(217,119,6,.05) 0%, transparent 40%),
    radial-gradient(ellipse at 90% 7%,  rgba(200,90,50,.05) 0%, transparent 35%),
    radial-gradient(ellipse at 50% 95%, rgba(46,107,71,.03) 0%, transparent 40%),
    var(--bg);
  color: var(--text);
}

[data-testid="stHeader"] {
  background: rgba(250, 247, 242, 0.92) !important;
  backdrop-filter: blur(10px);
}

.block-container {
  padding: 2.2rem 2.8rem 3.5rem;
  max-width: 1560px;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #F5EFE8 0%, #EDE5DC 100%) !important;
  border-right: 1px solid var(--line-strong) !important;
}

section[data-testid="stSidebar"] > div {
  padding-top: 1.6rem;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
  padding: 0.5rem 0.75rem;
  border-radius: 9px;
  color: #3D352E !important;
  font-weight: 500;
  transition: all 0.15s ease;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  background: rgba(200, 90, 50, 0.08) !important;
  color: var(--terracotta) !important;
}

/* ── Typography ── */
h1, h2, h3, h4 {
  font-family: 'Manrope', sans-serif !important;
  color: var(--heading) !important;
  letter-spacing: -0.03em;
}

h1 { font-size: 2.2rem !important; font-weight: 800 !important; }
h2 { font-size: 1.55rem !important; font-weight: 750 !important; }
h3 { font-size: 1.15rem !important; font-weight: 700 !important; }
p, li, label { color: var(--text); }
.section-note { color: var(--muted); font-size: 0.96rem; margin-top: -0.45rem; }

/* ── Cards & Metrics ── */
[data-testid="stMetric"] {
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  border-radius: 14px !important;
  padding: 16px 20px !important;
  box-shadow: 0 4px 18px rgba(40, 35, 29, 0.04) !important;
}

[data-testid="stMetricLabel"] {
  color: var(--muted) !important;
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

[data-testid="stMetricValue"] {
  color: var(--heading) !important;
  font-family: 'Manrope', sans-serif !important;
  font-size: 1.7rem !important;
  font-weight: 800 !important;
}

/* ── Tables & DataFrames ── */
[data-testid="stDataFrame"], [data-testid="stTable"] {
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  border-radius: 12px !important;
  box-shadow: 0 4px 14px rgba(40, 35, 29, 0.03) !important;
  overflow: hidden;
}

/* ── Plotly Charts ── */
[data-testid="stPlotlyChart"] {
  background: var(--panel) !important;
  border: 1px solid var(--line) !important;
  border-radius: 14px !important;
  padding: 12px !important;
  box-shadow: 0 4px 18px rgba(40, 35, 29, 0.04) !important;
}

/* ── Buttons ── */
.stButton > button, .stDownloadButton > button {
  background: linear-gradient(135deg, #C85A32 0%, #A84420 100%) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  padding: 0.58rem 1.25rem !important;
  box-shadow: 0 4px 12px rgba(200, 90, 50, 0.25) !important;
  transition: all 0.18s ease !important;
}

.stButton > button:hover, .stDownloadButton > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 18px rgba(200, 90, 50, 0.35) !important;
  color: #FFFFFF !important;
}

/* ── Form Controls & Selectboxes ── */
[data-baseweb="select"] > div, [data-baseweb="input"] > div {
  background: var(--panel) !important;
  border-color: var(--line) !important;
  border-radius: 9px !important;
  color: var(--text) !important;
}

/* ── Brand Strips & Badges ── */
.brand-strip {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 14px 18px;
  margin-bottom: 22px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: linear-gradient(135deg, #FFFFFF 0%, #F9F5EE 100%);
  box-shadow: 0 4px 16px rgba(40, 35, 29, 0.04);
}

.brand-mark {
  width: 40px;
  height: 40px;
  border-radius: 11px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #C85A32 0%, #D97706 100%);
  color: #FFFFFF;
  font-size: 19px;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(200, 90, 50, 0.30);
}

.brand-title {
  color: var(--heading);
  font-family: 'Manrope', sans-serif;
  font-weight: 800;
  font-size: 1.05rem;
  letter-spacing: -0.02em;
}

.brand-sub {
  color: var(--muted);
  font-size: 0.8rem;
}

/* ── Decision Badges ── */
.badge-order { background: #EBF3FA; border: 1px solid #C4DDF2; color: #1D5C96; font-weight: 700; border-radius: 8px; padding: 6px 12px; display: inline-flex; align-items: center; gap: 6px; }
.badge-transfer { background: #F5EEF8; border: 1px solid #DFCBEE; color: #6D2E8E; font-weight: 700; border-radius: 8px; padding: 6px 12px; display: inline-flex; align-items: center; gap: 6px; }
.badge-markdown { background: #FEF6EB; border: 1px solid #FADCB2; color: #A65700; font-weight: 700; border-radius: 8px; padding: 6px 12px; display: inline-flex; align-items: center; gap: 6px; }
.badge-supplier { background: #EEF7F2; border: 1px solid #C6E6D4; color: #1E6B43; font-weight: 700; border-radius: 8px; padding: 6px 12px; display: inline-flex; align-items: center; gap: 6px; }
</style>
""", unsafe_allow_html=True)

def locate(*paths):
    for rel in paths:
        p = ROOT / rel
        if p.exists():
            return p
    return None

def read_csv(*paths):
    p = locate(*paths)
    if p is None:
        return pd.DataFrame(), None
    try:
        return pd.read_csv(p), p
    except Exception as exc:
        st.error(f"Unable to read {p.name}: {exc}")
        return pd.DataFrame(), p

def money(v):
    return f"₹{v:,.0f}"

def metric_row(df, profit_col="operating_profit", fill_col="fill_rate_pct"):
    if df.empty:
        return
    profit = df[profit_col].mean() if profit_col in df else None
    fill = df[fill_col].mean() if fill_col in df else None
    expired = df["expired_units"].mean() if "expired_units" in df else None
    unmet = df["unmet_demand"].mean() if "unmet_demand" in df else None
    cols = st.columns(4)
    cols[0].metric("Mean operating profit / episode", money(profit) if profit is not None else "—")
    cols[1].metric("Mean fill rate", f"{fill:.2f}%" if fill is not None else "—")
    cols[2].metric("Mean expired units", f"{expired:,.1f}" if expired is not None else "—")
    cols[3].metric("Mean unmet demand", f"{unmet:,.1f}" if unmet is not None else "—")

# ---------- Data Loading ----------
m5, m5_path = read_csv("data/m5/m5_retail_processed.csv")
pred, pred_path = read_csv("forecasting_outputs/forecast_test_predictions.csv", "forecast_test_predictions.csv")
forecast_metrics, fm_path = read_csv("forecasting_outputs/forecast_model_comparison.csv", "forecast_model_comparison.csv")
episode, episode_path = read_csv("m5_robustness_episode_summary.csv")
steps, steps_path = read_csv("m5_robustness_step_results.csv")
policy_summary, ps_path = read_csv("m5_robustness_policy_summary.csv")
eval_overall, eval_path = read_csv("m5_evaluation_overall.csv")
final_comp, fc_path = read_csv("final_policy_comparison.csv")

for frame in [m5, pred, steps]:
    if not frame.empty and "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")

# ---------- Sidebar ----------
st.sidebar.markdown("""
<div class='brand-strip'>
  <div class='brand-mark'>📦</div>
  <div>
    <div class='brand-title'>RETAIL INTELLIGENCE</div>
    <div class='brand-sub'>Inventory & Markdown Engine</div>
  </div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("NAVIGATION", [
    "Executive Overview", "AI Decision Center", "Demand Forecasting", "Inventory Analytics",
    "Policy Comparison", "Project & Data"
])

st.sidebar.markdown("---")
st.sidebar.caption("Research prototype • M5 Holdout Experiments")

# Main Banner
st.markdown("""
<div class='brand-strip'>
  <div class='brand-mark'>✦</div>
  <div>
    <div class='brand-title'>DYNAMIC RETAIL INVENTORY &amp; MARKDOWN DECISION CENTER</div>
    <div class='brand-sub'>Multi-store inventory reinforcement learning, demand forecasting &amp; lateral transfer routing</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
#  PAGE: EXECUTIVE OVERVIEW
# ═══════════════════════════════════════════════════════════════════
if page == "Executive Overview":
    st.header("Executive Overview")
    st.markdown("<p class='section-note'>A multi-store retail decision intelligence platform combining ML demand forecasts with PPO reinforcement learning and heuristic benchmark policies.</p>", unsafe_allow_html=True)

    if not m5.empty:
        a, b, c, d = st.columns(4)
        a.metric("Historical Observations", f"{len(m5):,}")
        b.metric("Stores Analysed", f"{m5['store_id'].nunique():,}" if "store_id" in m5 else "—")
        c.metric("Historical Demand Units", f"{m5['demand_units'].sum():,.0f}" if "demand_units" in m5 else "—")
        d.metric("Products Analysed", f"{m5['product_id'].nunique():,}" if "product_id" in m5 else "—")
    else:
        st.warning("Processed M5 data was not found at data/m5/m5_retail_processed.csv.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Demand Forecasting Performance")
    if not forecast_metrics.empty:
        overall = forecast_metrics[forecast_metrics["scope"].eq("OVERALL")] if "scope" in forecast_metrics else forecast_metrics
        if not overall.empty:
            best = overall.sort_values("WAPE_percent").iloc[0]
            a, b, c = st.columns(3)
            a.metric("Best Evaluated Model", f"{str(best['method']).replace('_', ' ')} (not confirmed)")
            b.metric("Best Overall WAPE", f"{best['WAPE_percent']:.2f}%")
            c.metric("Test Observations", f"{int(best['test_observations']):,}")

            # Elegant Warm Bar Chart
            fig_ov = px.bar(
                overall.sort_values("WAPE_percent"), x="method", y="WAPE_percent",
                color="WAPE_percent", color_continuous_scale=["#284B63", "#C85A32", "#D97706"],
                text="WAPE_percent",
                labels={"method": "Model", "WAPE_percent": "WAPE (%)"},
                title="Forecasting Error Comparison (WAPE % — lower is better)"
            )
            fig_ov.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
            fig_ov.update_layout(
                showlegend=False, coloraxis_showscale=False,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=45, b=12, l=0, r=0), height=280,
                xaxis=dict(tickfont=dict(color="#28231D")),
                yaxis=dict(showgrid=True, gridcolor="rgba(195,178,155,.3)", tickfont=dict(color="#28231D"))
            )
            st.plotly_chart(fig_ov, use_container_width=True)
    else:
        st.info("Forecast comparison file not found.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Robustness Evaluation Snapshot")
    if not episode.empty:
        summary = episode.groupby("policy", as_index=False).agg(
            operating_profit=("operating_profit", "mean"),
            fill_rate_pct=("fill_rate_pct", "mean"),
            expired_units=("expired_units", "mean"),
            unmet_demand=("unmet_demand", "mean"))
        metric_row(summary)
        st.markdown("<br>", unsafe_allow_html=True)
        display = summary.rename(columns={
            "policy": "Policy", "operating_profit": "Mean profit (₹)",
            "fill_rate_pct": "Mean fill rate (%)", "expired_units": "Mean expired units",
            "unmet_demand": "Mean unmet demand"})
        st.dataframe(display, use_container_width=True, hide_index=True)

        # Side by side bar chart
        fig_snap = px.bar(
            summary.melt(id_vars="policy", value_vars=["operating_profit", "fill_rate_pct"],
                         var_name="Metric", value_name="Value"),
            x="Metric", y="Value", color="policy", barmode="group",
            color_discrete_sequence=["#C85A32", "#284B63"],
            title="Policy Trade-off Snapshot: Operating Profit vs Service Fill Rate"
        )
        fig_snap.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=1.14),
            margin=dict(t=50, b=12, l=0, r=0), height=300,
            xaxis=dict(tickfont=dict(color="#28231D")),
            yaxis=dict(showgrid=True, gridcolor="rgba(195,178,155,.3)", tickfont=dict(color="#28231D"))
        )
        st.plotly_chart(fig_snap, use_container_width=True)
    elif not policy_summary.empty:
        st.dataframe(policy_summary, use_container_width=True, hide_index=True)
    else:
        st.info("Robustness episode summary not found.")

    st.caption("Inventory economics are simulated using illustrative assumptions; they are not Walmart's actual internal operating costs or profits.")

# ═══════════════════════════════════════════════════════════════════
#  PAGE: DEMAND FORECASTING
# ═══════════════════════════════════════════════════════════════════
elif page == "Demand Forecasting":
    st.header("Demand Forecasting & EDA")
    st.markdown("<p class='section-note'>Random Forest one-day-ahead rolling forecasts evaluated on the 20% chronological holdout dataset.</p>", unsafe_allow_html=True)

    if pred.empty:
        st.warning("Forecast predictions not found. Expected forecasting_outputs/forecast_test_predictions.csv.")
    else:
        store_list = sorted(pred["store_id"].dropna().unique())
        store = st.selectbox("Select Store", store_list)
        d = pred[pred["store_id"].eq(store)].sort_values("date").copy()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=d["date"], y=d["actual_demand"], name="Historical Actual Demand", mode="lines",
            line=dict(width=2, color="#C85A32"),
            fill="tozeroy", fillcolor="rgba(200,90,50,0.08)"
        ))
        fig.add_trace(go.Scatter(
            x=d["date"], y=d["random_forest_prediction"], name="Random Forest Forecast", mode="lines",
            line=dict(width=2, color="#284B63", dash="dot")
        ))
        fig.update_layout(
            title=f"{store} — Actual Demand vs Random Forest Predictions",
            xaxis_title="Date", yaxis_title="Demand units",
            hovermode="x unified", legend=dict(orientation="h", y=1.12),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=50, b=15, l=0, r=0), height=360,
            xaxis=dict(showgrid=False, tickfont=dict(color="#28231D")),
            yaxis=dict(showgrid=True, gridcolor="rgba(195,178,155,.3)", tickfont=dict(color="#28231D"))
        )
        st.plotly_chart(fig, use_container_width=True)

        err = d["actual_demand"] - d["random_forest_prediction"]
        denom = d["actual_demand"].abs().sum()
        a, b, c = st.columns(3)
        a.metric("Mean Absolute Error (MAE)", f"{err.abs().mean():.2f}")
        b.metric("Root Mean Squared Error (RMSE)", f"{(err.pow(2).mean())**0.5:.2f}")
        c.metric("Weighted Absolute Percentage Error (WAPE)", f"{(err.abs().sum()/denom*100) if denom else 0:.2f}%")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Actual vs Predicted Holdout Records")
        forecast_view = d[["date", "store_id", "actual_demand", "random_forest_prediction"]].copy()
        forecast_view["absolute_error"] = (forecast_view["actual_demand"] - forecast_view["random_forest_prediction"]).abs()
        st.dataframe(forecast_view.tail(30), use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Download Selected-Store Forecast Records (CSV)",
            forecast_view.to_csv(index=False).encode("utf-8"),
            file_name=f"{store}_forecast_records.csv",
            mime="text/csv"
        )

    if not forecast_metrics.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Forecasting Model Benchmarks")
        overall = forecast_metrics[forecast_metrics["scope"].eq("OVERALL")] if "scope" in forecast_metrics else forecast_metrics
        chart = px.bar(
            overall.sort_values("WAPE_percent"), x="method", y="WAPE_percent",
            color="WAPE_percent", color_continuous_scale=["#284B63", "#C85A32", "#D97706"],
            text="WAPE_percent", title="Model Error Comparison (WAPE % — lower is better)",
            labels={"method": "Forecasting Method", "WAPE_percent": "WAPE (%)"}
        )
        chart.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        chart.update_layout(
            showlegend=False, coloraxis_showscale=False,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(showgrid=True, gridcolor="rgba(195,178,155,.3)")
        )
        st.plotly_chart(chart, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Random Forest Feature Importance (EDA Drivers)")
    model_candidates = [
        ROOT / "forecasting_outputs/random_forest_demand_model.joblib",
        ROOT / "forecasting_outputs/random_forest_model.joblib",
        ROOT / "models/random_forest_demand_model.joblib"
    ]
    model_file = next((p for p in model_candidates if p.exists()), None)
    if model_file is not None:
        try:
            import joblib
            model_bundle = joblib.load(model_file)
            if isinstance(model_bundle, dict):
                estimator = model_bundle.get("model")
                feature_names = model_bundle.get("feature_columns")
            else:
                estimator = getattr(model_bundle, "named_steps", {}).get("model", model_bundle) if hasattr(model_bundle, "named_steps") else model_bundle
                feature_names = getattr(estimator, "feature_names_in_", None)
            importances = getattr(estimator, "feature_importances_", None)
            if importances is not None:
                names = list(feature_names) if feature_names is not None else [f"Feature {i+1}" for i in range(len(importances))]
                importance_df = pd.DataFrame({"feature": names, "importance": importances}).sort_values("importance", ascending=False).head(15)
                fig_fi = px.bar(
                    importance_df.sort_values("importance"), x="importance", y="feature", orientation="h",
                    color="importance", color_continuous_scale=["#D97706", "#C85A32", "#9A3412"],
                    title="Top Demand Influencers Identified by Random Forest", labels={"importance": "Importance Score", "feature": "Driver"}
                )
                fig_fi.update_layout(
                    showlegend=False, coloraxis_showscale=False,
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor="rgba(195,178,155,.3)")
                )
                st.plotly_chart(fig_fi, use_container_width=True)
            else:
                st.info("The saved forecasting model does not expose feature_importances_.")
        except Exception as exc:
            st.info(f"Feature importance could not be loaded from the saved model: {exc}")
    else:
        st.info("Feature importance will appear when the trained Random Forest .joblib file is placed in forecasting_outputs/.")

# ═══════════════════════════════════════════════════════════════════
#  PAGE: AI DECISION CENTER
# ═══════════════════════════════════════════════════════════════════
elif page == "AI Decision Center":
    st.header("AI Inventory Decision Center")
    st.markdown("<p class='section-note'>Choose a historical holdout date and store, then execute the saved PPO policy against the revised baseline under identical simulation conditions.</p>", unsafe_allow_html=True)
    st.info("ℹ️ This is a one-day historical replay on the Random Forest test period — not a live inventory deployment or future-date forecast.")

    if pred.empty or m5.empty:
        st.error("Forecast predictions or processed M5 data are missing. Check the Project & Data page.")
    else:
        available = pred[["date", "store_id", "random_forest_prediction", "actual_demand"]].dropna().copy()
        available["date"] = pd.to_datetime(available["date"]).dt.normalize()
        stores = sorted(available["store_id"].unique())

        col1, col2 = st.columns(2)
        with col1:
            selected_store = st.selectbox("🏪 Select Store", stores, key="decision_store")
        with col2:
            store_dates = sorted(available.loc[available["store_id"].eq(selected_store), "date"].unique())
            selected_date = st.selectbox("📅 Select Historical Date (Holdout Period)", store_dates, index=0,
                                         format_func=lambda x: pd.Timestamp(x).strftime("%d %b %Y"), key="decision_date")

        forecast_row = available[(available["store_id"].eq(selected_store)) & (available["date"].eq(pd.Timestamp(selected_date)))].iloc[0]

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Holdout Demand Telemetry")
        a, b, c = st.columns(3)
        a.metric("🌲 RF Predicted Demand", f"{forecast_row['random_forest_prediction']:.1f} units")
        b.metric("📦 Historical Actual Demand", f"{forecast_row['actual_demand']:.0f} units")
        c.metric("📏 Absolute Forecast Error", f"{abs(forecast_row['actual_demand']-forecast_row['random_forest_prediction']):.1f} units")
        st.caption("The Random Forest prediction is shown for decision support. PPO retains its original 7-day historical-average observation input.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("▶ Run PPO vs Revised Baseline Simulation", type="primary", use_container_width=True):
            with st.spinner("⚙️ Loading saved PPO policy and executing matched simulations across stores..."):
                try:
                    from integrated_decision import run_comparison
                    result = run_comparison(selected_store, selected_date, ROOT)
                    st.session_state["integrated_decision_result"] = result
                except Exception as exc:
                    st.error(f"Simulation could not be completed: {exc}")
                    st.exception(exc)

        result = st.session_state.get("integrated_decision_result")
        if result and result.get("store") == selected_store and pd.Timestamp(result.get("date")).normalize() == pd.Timestamp(selected_date).normalize():
            st.divider()
            st.subheader(f"Inventory Decisions — {selected_store} | {pd.Timestamp(selected_date).strftime('%d %b %Y')}")
            st.caption(f"PPO's internal 7-day mean forecast input for this store: {result['ppo'].get('ppo_internal_forecast_input_7d_mean', float('nan')):.1f} units.")

            left, right = st.columns(2)
            with left:
                st.markdown("#### 🤖 PPO Reinforcement Learning Policy")
                ppo_act = result["ppo_action"]
                st.markdown(f"""
                <div style='display:flex; flex-wrap:wrap; gap:8px; margin-bottom:12px;'>
                  <span class='badge-order'>📦 Order: {ppo_act.get('Order quantity', '—')} Units</span>
                  <span class='badge-transfer'>🔀 Transfer: {ppo_act.get('Transfer quantity', 0)} from {ppo_act.get('Transfer source', 'None')}</span>
                  <span class='badge-markdown'>🏷️ Markdown: {ppo_act.get('Markdown', '0%')}</span>
                  <span class='badge-supplier'>⚡ Supplier: {ppo_act.get('Supplier', '—')}</span>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(list(ppo_act.items()), columns=["Decision Variable", "Action"]), hide_index=True, use_container_width=True)

            with right:
                st.markdown("#### 📐 Rule-Based Baseline Policy")
                base_act = result["baseline_action"]
                st.markdown(f"""
                <div style='display:flex; flex-wrap:wrap; gap:8px; margin-bottom:12px;'>
                  <span class='badge-order'>📦 Order: {base_act.get('Order quantity', '—')} Units</span>
                  <span class='badge-transfer'>🔀 Transfer: {base_act.get('Transfer quantity', 0)} from {base_act.get('Transfer source', 'None')}</span>
                  <span class='badge-markdown'>🏷️ Markdown: {base_act.get('Markdown', '0%')}</span>
                  <span class='badge-supplier'>⚡ Supplier: {base_act.get('Supplier', '—')}</span>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(pd.DataFrame(list(base_act.items()), columns=["Decision Variable", "Action"]), hide_index=True, use_container_width=True)

            ppo, base = result["ppo"], result["baseline"]
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Simulated Outcome Comparison")

            x1, x2, x3 = st.columns(3)
            x1.metric("PPO Simulated Profit", money(ppo["operating_profit"]))
            x2.metric("Baseline Simulated Profit", money(base["operating_profit"]))
            diff = ppo["operating_profit"] - base["operating_profit"]
            x3.metric("Profit Difference (PPO − Baseline)", money(diff), delta=f"{diff:+.0f} ₹")

            outcome = pd.DataFrame([
                {"Metric": "Units sold", "PPO": ppo["units_sold"], "Revised Baseline": base["units_sold"]},
                {"Metric": "Unmet demand", "PPO": ppo["unmet_demand"], "Revised Baseline": base["unmet_demand"]},
                {"Metric": "Ending inventory", "PPO": ppo["inventory_end"], "Revised Baseline": base["inventory_end"]},
                {"Metric": "Expired units", "PPO": ppo["units_expired"], "Revised Baseline": base["units_expired"]},
                {"Metric": "Operating profit (₹)", "PPO": ppo["operating_profit"], "Revised Baseline": base["operating_profit"]},
                {"Metric": "Fill rate (%)", "PPO": ppo["service_level"] * 100, "Revised Baseline": base["service_level"] * 100},
            ])
            st.dataframe(outcome, hide_index=True, use_container_width=True)

            chart_df = pd.DataFrame([
                {"Policy": "PPO", "Units sold": ppo["units_sold"], "Unmet demand": ppo["unmet_demand"], "Ending inventory": ppo["inventory_end"]},
                {"Policy": "Revised Baseline", "Units sold": base["units_sold"], "Unmet demand": base["unmet_demand"], "Ending inventory": base["inventory_end"]},
            ]).melt(id_vars="Policy", var_name="Outcome", value_name="Units")

            fig_bar = px.bar(
                chart_df, x="Outcome", y="Units", color="Policy", barmode="group",
                color_discrete_sequence=["#C85A32", "#284B63"],
                title="Operational Units Comparison"
            )
            fig_bar.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=1.12),
                xaxis=dict(tickfont=dict(color="#28231D")),
                yaxis=dict(showgrid=True, gridcolor="rgba(195,178,155,.3)")
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            download = pd.DataFrame([{"policy": "PPO", **ppo}, {"policy": "Revised Baseline", **base}])
            st.download_button(
                "⬇️ Download Simulation Result (CSV)",
                download.to_csv(index=False).encode("utf-8"),
                file_name=f"decision_{selected_store}_{pd.Timestamp(selected_date).date()}.csv",
                mime="text/csv"
            )

# ═══════════════════════════════════════════════════════════════════
#  PAGE: INVENTORY ANALYTICS
# ═══════════════════════════════════════════════════════════════════
elif page == "Inventory Analytics":
    st.header("Inventory Analytics")
    st.markdown("<p class='section-note'>Explore daily multi-store inventory curves, stockout risk, lateral transfers, and holding dynamics.</p>", unsafe_allow_html=True)

    if steps.empty:
        st.warning("Robustness step results not found. Expected m5_robustness_step_results.csv.")
    else:
        if "window" in steps.columns:
            windows = sorted(steps["window"].dropna().unique(), key=lambda x: str(x))
            chosen_window = st.selectbox("Evaluation Window", windows, format_func=lambda x: f"Window {x}")
            d = steps[steps["window"].eq(chosen_window)].copy()
        else:
            d = steps.copy()
            st.info("Window identifier not present; using available step records.")

        policies = sorted(d["policy"].dropna().unique())
        stores = sorted(d["focus_store"].dropna().unique())
        psel = st.multiselect("Filter Policies", policies, default=policies)
        ssel = st.multiselect("Filter Stores", stores, default=stores)
        d = d[d["policy"].isin(psel) & d["focus_store"].isin(ssel)].copy()

        agg_cols = [c for c in ["demand", "units_sold", "unmet_demand", "inventory_end", "units_expired"] if c in d.columns]
        if not d.empty and agg_cols:
            per_store_day = (
                d.groupby(["date", "policy", "focus_store"], as_index=False)[agg_cols]
                 .mean()
                 .sort_values("date")
            )
            daily = (
                per_store_day.groupby(["date", "policy"], as_index=False)[agg_cols]
                .sum()
                .sort_values("date")
            )
            seed_count = d["seed"].nunique() if "seed" in d.columns else None
            st.info(
                f"Charts show average across {seed_count} random seeds per date and store, summed across selected stores."
                if seed_count else "Charts show per-date averages by store."
            )

            labels = {
                "inventory_end": "Average Ending Inventory (Units)",
                "unmet_demand": "Average Unmet Demand (Units)"
            }
            for col, title in [
                ("inventory_end", "Average Ending Inventory Trajectory Over Time"),
                ("unmet_demand", "Average Unmet Demand (Stockouts) Over Time")
            ]:
                if col in daily:
                    fig = px.line(
                        daily, x="date", y=col, color="policy", markers=True, title=title,
                        color_discrete_sequence=["#C85A32", "#284B63"],
                        labels={"date": "Date", col: labels[col], "policy": "Policy"}
                    )
                    fig.update_layout(
                        hovermode="x unified", legend=dict(orientation="h", y=1.12),
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                        yaxis_title=labels[col],
                        xaxis=dict(tickfont=dict(color="#28231D")),
                        yaxis=dict(showgrid=True, gridcolor="rgba(195,178,155,.3)")
                    )
                    st.plotly_chart(fig, use_container_width=True)

            if "units_expired" in d.columns:
                per_seed_expiry = (
                    d.groupby(["policy", "seed"], as_index=False)["units_expired"].sum()
                    if "seed" in d.columns else
                    d.groupby(["policy"], as_index=False)["units_expired"].sum()
                )
                if "seed" in per_seed_expiry.columns:
                    exp = per_seed_expiry.groupby("policy", as_index=False)["units_expired"].mean()
                    exp_title = "Mean Expired Units per Seed in Selected Window"
                else:
                    exp = per_seed_expiry
                    exp_title = "Expired Units in Selected Window"
                fig_exp = px.bar(
                    exp, x="policy", y="units_expired", title=exp_title,
                    color="policy", color_discrete_sequence=["#C85A32", "#284B63"],
                    labels={"policy": "Policy", "units_expired": "Expired units"}
                )
                fig_exp.update_layout(
                    showlegend=False,
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    yaxis=dict(showgrid=True, gridcolor="rgba(195,178,155,.3)")
                )
                st.plotly_chart(fig_exp, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Store-Wise Inventory Comparison")
            store_daily = (
                d.groupby(["focus_store", "policy", "date"], as_index=False)
                 .agg(inventory_end=("inventory_end", "mean"),
                      unmet_demand=("unmet_demand", "mean"),
                      units_expired=("units_expired", "mean"))
            )
            store_summary = (
                store_daily.groupby(["focus_store", "policy"], as_index=False)
                .agg(mean_inventory=("inventory_end", "mean"),
                     peak_average_inventory=("inventory_end", "max"),
                     total_average_unmet=("unmet_demand", "sum"),
                     total_average_expired=("units_expired", "sum"))
            )
            st.dataframe(store_summary, use_container_width=True, hide_index=True)
            store_fig = px.bar(
                store_summary, x="focus_store", y="mean_inventory", color="policy", barmode="group",
                color_discrete_sequence=["#C85A32", "#284B63"],
                title="Mean Ending Inventory by Store and Policy",
                labels={"focus_store": "Store", "mean_inventory": "Mean Ending Inventory (Units)", "policy": "Policy"}
            )
            store_fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(showgrid=True, gridcolor="rgba(195,178,155,.3)")
            )
            st.plotly_chart(store_fig, use_container_width=True)
        else:
            st.info("No rows match the selected window, policies and stores.")

# ═══════════════════════════════════════════════════════════════════
#  PAGE: POLICY COMPARISON
# ═══════════════════════════════════════════════════════════════════
elif page == "Policy Comparison":
    st.header("Policy Comparison & Robustness")
    st.markdown("<p class='section-note'>Robustness evaluation across 5 random seeds and 3 independent 60-day holdout windows (30 total simulation episodes).</p>", unsafe_allow_html=True)

    if not episode.empty:
        agg = episode.groupby("policy", as_index=False).agg(
            operating_profit=("operating_profit", "mean"),
            profit_std=("operating_profit", "std"),
            fill_rate_pct=("fill_rate_pct", "mean"),
            expired_units=("expired_units", "mean"),
            unmet_demand=("unmet_demand", "mean"),
            holding_cost=("holding_cost", "mean"),
            wastage_cost=("wastage_cost", "mean"),
            transfer_cost=("transfer_cost", "mean"),
            expedite_cost=("expedite_cost", "mean"))
        st.subheader("Key Benchmark Metrics")
        metric_row(agg)
        st.dataframe(agg.rename(columns={
            "policy": "Policy", "operating_profit": "Mean operating profit (₹)",
            "profit_std": "Profit standard deviation (₹)", "fill_rate_pct": "Mean fill rate (%)",
            "expired_units": "Mean expired units", "unmet_demand": "Mean unmet demand",
            "holding_cost": "Mean holding cost (₹)", "wastage_cost": "Mean wastage cost (₹)",
            "transfer_cost": "Mean transfer cost (₹)", "expedite_cost": "Mean expedite cost (₹)"
        }), use_container_width=True, hide_index=True)

        for col, title, ylabel in [
            ("operating_profit", "Mean Operating Profit Across Episodes", "Profit (₹)"),
            ("fill_rate_pct", "Mean Service Fill Rate (%)", "Fill Rate (%)"),
            ("expired_units", "Mean Expired / Wastage Units", "Units"),
            ("unmet_demand", "Mean Unmet Customer Demand", "Units")
        ]:
            fig = px.bar(
                agg, x="policy", y=col, color="policy", title=title,
                color_discrete_sequence=["#C85A32", "#284B63"],
                labels={col: ylabel, "policy": "Policy"}
            )
            fig.update_layout(
                showlegend=False,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(showgrid=True, gridcolor="rgba(195,178,155,.3)")
            )
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Store-Wise Policy Breakdown")
        store_required = {"focus_store", "policy", "seed", "window", "revenue", "cost_of_goods_sold",
                          "holding_cost", "wastage_cost", "transfer_cost", "expedite_cost",
                          "demand", "units_sold", "unmet_demand", "units_expired"}
        if not steps.empty and store_required.issubset(steps.columns):
            store_runs = steps.groupby(["window", "seed", "policy", "focus_store"], as_index=False).agg(
                revenue=("revenue", "sum"),
                cogs=("cost_of_goods_sold", "sum"),
                holding=("holding_cost", "sum"),
                wastage=("wastage_cost", "sum"),
                transfer=("transfer_cost", "sum"),
                expedite=("expedite_cost", "sum"),
                demand=("demand", "sum"),
                sold=("units_sold", "sum"),
                unmet=("unmet_demand", "sum"),
                expired=("units_expired", "sum")
            )
            store_runs["operating_profit"] = (store_runs["revenue"] - store_runs["cogs"] -
                store_runs["holding"] - store_runs["wastage"] - store_runs["transfer"] - store_runs["expedite"])
            store_runs["fill_rate_pct"] = (store_runs["sold"] / store_runs["demand"].replace(0, pd.NA) * 100).fillna(0)
            store_summary = store_runs.groupby(["policy", "focus_store"], as_index=False).agg(
                mean_profit=("operating_profit", "mean"),
                mean_fill_rate=("fill_rate_pct", "mean"),
                mean_expired=("expired", "mean"),
                mean_unmet=("unmet", "mean")
            )
            st.dataframe(store_summary, use_container_width=True, hide_index=True)
            store_profit_fig = px.bar(
                store_summary, x="focus_store", y="mean_profit", color="policy", barmode="group",
                color_discrete_sequence=["#C85A32", "#284B63"],
                title="Mean Simulated Operating Profit by Store",
                labels={"focus_store": "Store", "mean_profit": "Mean Profit (₹)", "policy": "Policy"}
            )
            store_profit_fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(showgrid=True, gridcolor="rgba(195,178,155,.3)")
            )
            st.plotly_chart(store_profit_fig, use_container_width=True)

        st.download_button(
            "⬇️ Download Episode-Level Policy Results (CSV)",
            episode.to_csv(index=False).encode("utf-8"),
            file_name="policy_episode_results.csv",
            mime="text/csv"
        )
    else:
        st.warning("Policy evaluation CSVs not found.")

# ═══════════════════════════════════════════════════════════════════
#  PAGE: PROJECT & DATA
# ═══════════════════════════════════════════════════════════════════
else:
    st.header("Project & Data Explorer")
    st.markdown("<p class='section-note'>Inspection of data pipelines, RL policy checkpoints, and simulation assets.</p>", unsafe_allow_html=True)

    st.subheader("Project Components")
    st.markdown("""
    - **M5 Processed Dataset:** Cleaned retail demand for stores `CA_1`, `TX_1`, and `WI_1`.
    - **Random Forest Forecaster:** Rolling one-day-ahead demand predictions.
    - **PPO Reinforcement Learning Policy:** Multi-discrete action policy with matched VecNormalize observation statistics.
    - **Transparent Baseline Policy:** Rule-based inventory policy with safety stock and lateral rebalancing.
    - **Gymnasium Retail Environment:** Multi-echelon perishable inventory simulation with realistic holding and spoilage penalties.
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📁 File Integrity & Checkpoints Status")
    checks = [
        ("Processed M5 Data", "data/m5/m5_retail_processed.csv"),
        ("Environment-Ready M5 Data", "data/m5/m5_retail_env_ready.csv"),
        ("Forecast Predictions", "forecasting_outputs/forecast_test_predictions.csv"),
        ("Forecast Model Metrics", "forecasting_outputs/forecast_model_comparison.csv"),
        ("PPO M5 Holdout Model", "models/retail_ppo_M5_HOLDOUT.zip"),
        ("PPO VecNormalize Statistics", "models/retail_vecnormalize_M5_HOLDOUT.pkl"),
        ("Robustness Episode Summary", "m5_robustness_episode_summary.csv"),
        ("Robustness Step Results", "m5_robustness_step_results.csv"),
        ("Robustness Policy Summary", "m5_robustness_policy_summary.csv"),
    ]
    cols = st.columns(2)
    for i, (label, rel) in enumerate(checks):
        exists = (ROOT / rel).exists()
        icon = "✅" if exists else "⚠️"
        (cols[0] if i % 2 == 0 else cols[1]).write(f"{icon} **{label}:** `{rel}`")

st.sidebar.markdown("---")
st.sidebar.caption("Dashboard v6 • Integrated AI Decision Center")
