import pandas as pd
import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os

# Google Sheets Bağlantısı
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
client = gspread.authorize(creds)
SPREADSHEET_ID = os.getenv("SHEET_ID")
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# API URL
url = "https://api.exchangerate.host/latest?base=USD&symbols=TRY,EUR"
r = requests.get(url)
print("📡 Status:", r.status_code)
print("📡 Raw response:", r.text)

try:
    data = r.json()
except Exception as e:
    print("❌ JSON parse hatası:", e)
    exit(1)

# Rates çek
rates = data.get("rates", {})
if not rates:
    print("⚠ Rates boş geldi, API yanıtını kontrol et")
    exit(0)

# Data hazırlama
data_all = []
usd_try = rates.get("TRY")
eur_try = rates.get("EUR")
if usd_try:
    data_all.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "USD", "API", usd_try, usd_try, 0])
if eur_try:
    data_all.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "EUR", "API", eur_try, eur_try, 0])

# Sheets’e yaz
if data_all:
    df = pd.DataFrame(data_all, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("✅ Google Sheets güncellendi!")
else:
    print("⚠ Veri bulunamadı")
