import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_banka_data(url, currency):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    rows = table.find_all("tr")[1:]
    data = []
    for row in rows:
        cols = row.find_all("td")
        banka = cols[0].text.strip()
        alis = float(cols[1].text.strip().replace(",", "."))
        satis = float(cols[2].text.strip().replace(",", "."))
        makas = satis - alis
        data.append([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), currency, banka, alis, satis, makas])
    return data

urls = {
    "USD": "https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "EUR": "https://kur.doviz.com/serbest-piyasa/euro",
    "Gram Altın": "https://altin.doviz.com/serbest-piyasa/gram-altin"
}

all_data = []
for kur, url in urls.items():
    all_data += scrape_banka_data(url, kur)

df = pd.DataFrame(all_data, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])
df.to_csv("banka_makas.csv", index=False, encoding="utf-8-sig")
print("CSV dosyası oluşturuldu.")
