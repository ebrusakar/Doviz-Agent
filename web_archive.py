# Gerekli kütüphaneleri içe aktarın.
# Bu kütüphaneler yüklü değilse, terminalinizde:
# 'pip install selenium pandas' komutunu çalıştırarak yükleyebilirsiniz.
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import os
import re

# Chrome Headless ayarları
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

# WebDriver'ı başlat
driver = webdriver.Chrome(options=options)

def temizle(text):
    """
    Metinden 'TL', boşluk gibi istenmeyen karakterleri temizler ve ondalık ayıracı
    olarak virgül yerine nokta kullanır.
    """
    return text.replace("TL", "").replace(" ", "").replace(",", ".").strip()

def scrape_kur_from_archive(url):
    """
    Internet Archive URL'sinden banka döviz kurlarını çeker.
    Tarih, saat ve kur adı URL'den ayrıştırılır.
    
    Args:
        url (str): Döviz kuru sayfasının Internet Archive URL'si.

    Returns:
        list: Tarih, kur adı, banka, alış, satış ve makas bilgilerini içeren verilerin listesi.
    """
    # URL'den tarih, saat ve kur adını ayrıştır
    # Örnek URL: https://web.archive.org/web/20250120053901/https://kur.doviz.com/serbest-piyasa/amerikan-dolari
    url_parts = re.search(r'web/(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})\d{2}.*/(.*)', url)
    if not url_parts:
        print(f"Uyarı: {url} adresinden tarih/saat bilgisi çekilemedi. Atlanıyor.")
        return []

    year, month, day, hour, minute, currency_path = url_parts.groups()
    snapshot_datetime = datetime.strptime(f"{year}-{month}-{day} {hour}:{minute}", "%Y-%m-%d %H:%M")
    
    kur_adi = currency_path.split('/')[-1]
    if kur_adi == 'amerikan-dolari':
        kur_adi = 'USD'
    elif kur_adi == 'euro':
        kur_adi = 'EUR'

    print(f"--- {kur_adi} verisi çekiliyor (Snapshot: {snapshot_datetime.strftime('%Y-%m-%d %H:%M')}) ---")
    
    try:
        driver.get(url)
        # Sayfanın yüklenmesini, banka tablosunun görünmesine göre bekle.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
        
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        
        data = []
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, "td")
            if len(cols) < 3:
                continue
            try:
                # Banka adı, alış ve satış fiyatlarını çek ve temizle
                banka = cols[0].text.strip()
                alis = float(temizle(cols[1].text))
                satis = float(temizle(cols[2].text))
            except ValueError:
                # Eğer fiyatlar sayısal değilse bu satırı atla
                print(f"Uyarı: '{banka}' bankası için sayısal olmayan değer bulundu. Satır atlanıyor.")
                continue
            
            makas = satis - alis
            data.append([snapshot_datetime.strftime("%Y-%m-%d %H:%M:%S"), kur_adi, banka, alis, satis, makas])
        return data

    except Exception as e:
        print(f"Hata oluştu: {kur_adi} verisi çekilemedi. Hata: {e}")
        return []

# Veri çekilecek URL'lerin listesi
archive_urls = [
    # Önceki USD URL'leri
    "https://web.archive.org/web/20250120053901/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250124105408/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250203101326/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250207011454/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250221192941/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250312160608/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250319073414/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250322034944/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250322082840/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250322192806/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250324084245/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250404010640/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250404213654/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250417051255/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250430045136/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250501194606/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250512143412/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250515134355/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250517174940/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250518111410/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250519195500/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250601154348/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250604034308/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250617202803/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    "https://web.archive.org/web/20250619090932/https://kur.doviz.com/serbest-piyasa/amerikan-dolari",
    # Yeni eklenen EUR URL'leri
    "https://web.archive.org/web/20250118203616/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250203101327/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250316115713/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250405021538/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250429173800/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250430045402/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250430214655/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250501194535/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250512143624/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250515134526/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250516105323/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250517175115/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250518111159/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250519195325/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250520173411/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250616011359/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250619092221/https://kur.doviz.com/serbest-piyasa/euro",
    "https://web.archive.org/web/20250721124456/https://kur.doviz.com/serbest-piyasa/euro",
]

# Verileri çek
tum_data = []
for url in archive_urls:
    tum_data += scrape_kur_from_archive(url)

# WebDriver'ı kapat ve belleği temizle
driver.quit()

# CSV'ye ekle (eski veri silinmesin)
csv_dosya = "banka_makas.csv"
if os.path.exists(csv_dosya):
    try:
        eski_df = pd.read_csv(csv_dosya)
        yeni_df = pd.DataFrame(tum_data, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])
        df = pd.concat([eski_df, yeni_df], ignore_index=True)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(tum_data, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])
else:
    df = pd.DataFrame(tum_data, columns=["Tarih", "Kur", "Banka", "Alış", "Satış", "Makas"])

# Veriyi CSV dosyasına kaydet
df.to_csv(csv_dosya, index=False, encoding="utf-8-sig")

print("\n--- Veri Çekme Tamamlandı ---")
print(f"Veriler '{csv_dosya}' dosyasına kaydedildi.")
print("\nSon 5 Kayıt:")
print(df.tail())