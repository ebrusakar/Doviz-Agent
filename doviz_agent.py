import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets Bağlantısı ---
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", 
         "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
client = gspread.authorize(creds)

SPREADSHEET_ID = "SHEET_ID"  # GitHub Secret ile alacağız
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# --- Veri Çekme (USD ve EUR) ---
def scrape_currency(url, currency_name):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    data = []
    if table:
        rows = table.find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) >= 3:
                banka = cols[0].get_text(strip=True)
                try:
                    alis = float(cols[1].get_text(strip=True).replace(",", ".").replace(" TL", ""))
                    satis = float(cols[2].get_text(strip=True).replace(",", ".").replace(" TL", ""))
                    makas = satis - alis
                    data.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), currency_name, banka, alis, satis, makas])
                except:
                    continue
    return data

data_all = []
data_all += scrape_currency("https://kur.doviz.com/serbest-piyasa/amerikan-dolari", "USD")
data_all += scrape_currency("https://kur.doviz.com/serbest-piyasa/euro", "EUR")

# --- Sheets'e Yaz ---
df = pd.DataFrame(data_all, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])
sheet.clear()
sheet.update([df.columns.values.tolist()] + df.values.tolist())

print("Google Sheets güncellendi!")
