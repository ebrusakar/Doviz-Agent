import pandas as pd
import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os

# --- Google Sheets Bağlantısı ---
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
client = gspread.authorize(creds)
SPREADSHEET_ID = os.getenv("SHEET_ID")
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# --- API URL ---
URLS = {
    "USD": "https://api.genelpara.com/embed/altin.json",  # Örnek API, farklı endpoint eklenebilir
    "EUR": "https://api.genelpara.com/embed/doviz.json"
}

data_all = []
for kur, url in URLS.items():
    r = requests.get(url).json()
    if kur in r:
        satis = float(r[kur]["satis"])
        alis = float(r[kur]["alis"])
        makas = satis - alis
        data_all.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), kur, "Genelpara API", alis, satis, makas])

# --- Sheets'e Yaz ---
if data_all:
    df = pd.DataFrame(data_all, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("✅ Google Sheets güncellendi!")
else:
    print("⚠ Veri bulunamadı.")
