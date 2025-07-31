from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime
import os
import time

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

# CSV'ye ekle (eski veri silinmesin)
csv_dosya = "banka_makas.csv"
if os.path.exists(csv_dosya):
    eski_df = pd.read_csv(csv_dosya)
    yeni_df = pd.DataFrame(tum_data, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])
    df = pd.concat([eski_df, yeni_df], ignore_index=True)
else:
    df = pd.DataFrame(tum_data, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])

df.to_csv(csv_dosya, index=False, encoding="utf-8-sig")

print(df.tail())
