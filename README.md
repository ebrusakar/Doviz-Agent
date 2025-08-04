# Bank Spread Monitoring Dashboard

This Power BI dashboard monitors the currency spread (buy-sell difference) across multiple banks.  
It enables analysis by time period, bank, and currency with statistical insights (average and standard deviation).  

---

## 🔍 ETL Process Overview
The project automates the pipeline from both **live exchange rate scraping** and **historical Web Archive extraction** to Power BI reporting.

- **Live Data:** Collected every 30 minutes from *a currency rates website*  
- **Archived Data:** Retrieved from Web Archive snapshots for historical backfill  
- **Data Storage:** Combined dataset stored in Google Sheets (versioned via GitHub)  
- **Visualization:** Power BI dashboard with yearly, working hours, and last 2 months statistics  

---

## ⚙️ ETL Steps

### 1️⃣ Extract (Data Retrieval)  
#### Live Data  
- **Agent:** `doviz_agent.py` uses **Selenium** to scrape USD and EUR buy/sell prices from a currency rates website.  
- **Storage:** Appended to Google Sheets via `gspread` API.  
- **Automation:** GitHub Actions (`doviz_yml`) runs every 30 minutes (cron).  

#### Archived Data  
- **Source:** Web Archive snapshots of the same site.  
- **Method:** Scraped historical buy/sell rates.  
- **Integration:** Results inserted into CSV.  
- **Upload:** CSV appended to the same Google Sheets dataset for continuous historical records.  

---

### 2️⃣ Transform (Data Preparation)  
In **Power Query (Power BI):**  
- Adjusted `Date` field (+3 hours for local time).  
- Converted spread column to numeric type.  
- Removed unnecessary columns.  
- Prepared USD/EUR aggregations (yearly, working hours, last 2 months).  

---

### 3️⃣ Load (Data Integration & Modeling)  
- Power BI connects to **Google Sheets public CSV link** via `Web.Contents()`.  
- DAX measures in `Doviz_Bot_Ozet_Banka` table:  
  - **2025 Average** & **Std. Dev.**  
  - **Working Hours Average** & **Std. Dev.**  
  - **Last 2 Months Average** & **Std. Dev.**  
- Dashboard visuals: tables, bar charts, and slicers for interactive analysis.  

---

## 📊 Dashboard Features
- Yearly averages and volatility for USD/EUR spreads  
- Working hours performance analysis  
- Last 2 months trends  
- Bank and currency filters  
- Visual comparisons through bar charts  

---

## 📡 Data Pipeline Diagram

# Bank Spread Monitoring Dashboard Flowchart

flowchart TD
    A[Data Sources] -->|Data| C[Google Sheets]
    B[Live Scraper (Selenium)<br>Web Archive Scraper] -->|Data| C[Google Sheets]
    C -->|Version Control| D[Github]
    C -->|Data Transformation| E[Power BI]
    E -->|Dashboard Visualization| F[Dashboard]
    D --> E

<img src="https://github.com/ebrusakar/doviz-agent/blob/main/panel.png"  width="900" height="500">

