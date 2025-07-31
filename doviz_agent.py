import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def temizle(text):
    return text.replace("TL", "").replace(" ", "").replace(",", ".").strip()

def scrape_kur(kur_adi, url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"{kur_adi} verisi alınamadı!")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table tbody tr")
    data = []

    for row in rows:
        cols = row.find_all("td")
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

tum_data = []
tum_data += scrape_kur("USD", "https://kur.doviz.com/serbest-piyasa/amerikan-dolari")
tum_data += scrape_kur("EUR", "https://kur.doviz.com/serbest-piyasa/euro")

csv_dosya = "banka_makas.csv"
if os.path.exists(csv_dosya):
    eski_df = pd.read_csv(csv_dosya)
    yeni_df = pd.DataFrame(tum_data, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])
    df = pd.concat([eski_df, yeni_df], ignore_index=True)
else:
    df = pd.DataFrame(tum_data, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])

df.to_csv(csv_dosya, index=False, encoding="utf-8-sig")

print(df.tail())
