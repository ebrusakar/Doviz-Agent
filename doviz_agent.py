import os
import pandas as pd
import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets bağlantısı
creds = Credentials.from_service_account_file("service_account.json", scopes=["https://www.googleapis.com/auth/spreadsheets"])
gc = gspread.authorize(creds)
sheet = gc.open_by_key(os.getenv("SHEET_ID")).sheet1

# exchangerate.host API (key gerekmiyor)
url = "https://api.exchangerate.host/latest?base=USD&symbols=TRY,EUR"
resp = requests.get(url).json()

if "rates" not in resp:
    print("⚠️ API'den veri gelmedi:", resp)
    exit(1)

usd_try = resp["rates"].get("TRY")
usd_eur = resp["rates"].get("EUR")

data = [
    [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "USD/TRY", "exchangerate.host", usd_try, usd_try, 0],
    [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "USD/EUR", "exchangerate.host", usd_eur, usd_eur, 0]
]

df = pd.DataFrame(data, columns=["Tarih", "Kur", "Kaynak", "Alış", "Satış", "Makas"])
sheet.clear()
sheet.update([df.columns.tolist()] + df.values.tolist())

print("✅ Google Sheets güncellendi!")
