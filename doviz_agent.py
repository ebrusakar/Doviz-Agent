from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime
import os
import time
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets Bağlantısı ---
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
client = gspread.authorize(creds)

SPREADSHEET_ID = os.getenv("SHEET_ID")
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# Chrome Headless ayarları
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

def temizle(text):
    return text.replace("TL", "").replace(" ", "").replace(",", ".").strip()

def scrape_kur(kur_adi, url):
    driver.get(url)
    time.sleep(3)  # Sayfanın yüklenmesini bekle
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
        data.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), kur_adi, banka, alis, satis, makas])
    return data

# USD ve EUR verilerini çek
tum_data = []
tum_data += scrape_kur("USD", "https://kur.doviz.com/serbest-piyasa/amerikan-dolari")
tum_data += scrape_kur("EUR", "https://kur.doviz.com/serbest-piyasa/euro")

driver.quit()

# --- Sheets'e EKLE (clear yerine append) ---
df = pd.DataFrame(tum_data, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])
sheet.append_rows(df.values.tolist())

print("✅ Yeni veriler Google Sheets'e eklendi!")
