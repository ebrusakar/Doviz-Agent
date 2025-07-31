import os
import pandas as pd
import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Sheets bağlantısı
creds = Credentials.from_service_account_file("service_account.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
gc = gspread.authorize(creds)
sheet = gc.open_by_key(os.getenv("SHEET_ID")).sheet1

# API Key ve URL
API_KEY = os.getenv("EXCHANGE_RATE_KEY")
url = f"https://api.exchangerate.host/latest?access_key={API_KEY}&base=USD&symbols=TRY,EUR"
resp = requests.get(url).json()

rates = resp.get("rates", {})
if not rates:
    print("⚠️ API'den veri gelmedi:", resp)
    exit(0)

data = []
if "TRY" in rates:
    data.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "USD", "exchangerate.host", rates["TRY"], rates["TRY"], 0])
if "EUR" in rates:
    data.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "EUR", "exchangerate.host", rates["EUR"], rates["EUR"], 0])

df = pd.DataFrame(data, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])
sheet.clear()
sheet.update([df.columns.tolist()] + df.values.tolist())
print("✅ Google Sheets güncellendi!")
