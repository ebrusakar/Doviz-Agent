import pandas as pd
import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os

# Google Sheets bağlantısı
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
client = gspread.authorize(creds)
SPREADSHEET_ID = os.getenv("SHEET_ID")
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# API (ExchangeRateHost)
url = "https://api.exchangerate.host/latest?base=USD&symbols=TRY,EUR"
r = requests.get(url).json()

data_all = []
if "rates" in r:
    usd_try = r["rates"]["TRY"]
    eur_try = r["rates"]["EUR"]
    data_all.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "USD", "API", usd_try, usd_try, 0])
    data_all.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "EUR", "API", eur_try, eur_try, 0])

# Sheets'e yaz
if data_all:
    df = pd.DataFrame(data_all, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("✅ Google Sheets güncellendi!")
else:
    print("⚠ Veri bulunamadı")
