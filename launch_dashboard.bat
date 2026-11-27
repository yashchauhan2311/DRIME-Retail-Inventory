@echo off
title Dynamic Retail Inventory Dashboard Launcher
cd /d "%~dp0integrated_ai_decision_package"
echo Starting Streamlit Dashboard...
python -m streamlit run app.py
pause
