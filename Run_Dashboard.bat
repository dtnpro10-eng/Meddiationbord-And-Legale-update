@echo off
cd /d "%~dp0"
echo ========================================================
echo Future Life Investments - Legal and Recovery Dashboard
echo ========================================================
echo Local PC Address:    http://localhost:8501
echo Other PCs (Same Wi-Fi): http://192.168.8.196:8501
echo ========================================================
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
pause
