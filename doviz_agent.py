import os
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# --- Google Sheets Bağlantısı ---
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
client = gspread.authorize(creds)
SPREADSHEET_ID = os.getenv("SHEET_ID")
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# --- Selenium setup ---
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)

def temizle(text):
    return text.replace("TL", "").replace(" ", "").replace(",", ".").strip()

def scrape_currency(url, currency_name):
    driver.get(url)
    time.sleep(3)  # JS'nin yüklenmesi için bekle
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    
    data = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 3:
            continue
        try:
            alis = float(temizle(cols[1].text))
            satis = float(temizle(cols[2].text))
        except ValueError:
            continue
        banka = cols[0].text.strip()
        makas = satis - alis
        data.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), currency_name, banka, alis, satis, makas])
    return data

data_all = []
data_all += scrape_currency("https://kur.doviz.com/serbest-piyasa/amerikan-dolari", "USD")
data_all += scrape_currency("https://kur.doviz.com/serbest-piyasa/euro", "EUR")

driver.quit()

# --- Sheets'e Yaz ---
df = pd.DataFrame(data_all, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])

if df.empty:
    print("⚠️ Veri bulunamadı, Sheets güncellenmedi.")
else:
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    print("✅ Google Sheets güncellendi!")
