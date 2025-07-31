import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets Bağlantısı ---
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
client = gspread.authorize(creds)

SPREADSHEET_ID = "SHEET_ID"  # GitHub Secret ile alacağız
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# --- Veri Çekme (USD ve EUR) ---
def scrape_currency(url, currency_name):
    print(f"--- {currency_name} verisi çekiliyor ---")
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if not table:
        print(f"{currency_name} tablosu bulunamadı! URL: {url}")
        return []
    else:
        print(f"{currency_name} tablosu bulundu.")
    
    rows = table.find_all("tr")
    print(f"{currency_name} tablosunda {len(rows)-1} satır bulundu.")
    
    data = []
    for row in rows[1:]:
        cols = row.find_all("td")
        print(f"Satır verileri: {[c.get_text(strip=True) for c in cols]}")  # Debug
        if len(cols) >= 3:
            try:
                alis = float(cols[1].get_text(strip=True).replace(",", ".").replace(" TL", ""))
                satis = float(cols[2].get_text(strip=True).replace(",", ".").replace(" TL", ""))
                makas = satis - alis
                data.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), currency_name, cols[0].get_text(strip=True), alis, satis, makas])
            except Exception as e:
                print(f"Hata: {e}")
                continue
    return data

data_all = []
data_all += scrape_currency("https://kur.doviz.com/serbest-piyasa/amerikan-dolari", "USD")
data_all += scrape_currency("https://kur.doviz.com/serbest-piyasa/euro", "EUR")

# --- Sheets'e Yaz ---
if data_all:
    df = pd.DataFrame(data_all, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("Google Sheets güncellendi!")
else:
    print("Hiç veri çekilemedi.")
