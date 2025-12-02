
> **Note:**  
> This extractor was developed under a limited budget of 150 USD.  
> The implemented features strictly followed the client's minimal requirements:  
> bypassing basic anti-bot checks, completing the booking form automatically,  
> and extracting parking data over multiple date combinations.  
>  
> The current design provides a logical and stable baseline suitable for the  
> requested scope. With extended budget and requirements, the system can be  
> further enhanced for higher performance, deeper anti-bot resistance, and  
> large-scale enterprise-level data extraction.




# Airport Parking Scraper – parkinglist.de Automation Tool
Developer: **Andrei Sorin Ștefan**

This project automates the extraction of parking offers from https://www.parkinglist.de for multiple German and Austrian airports.  
It is a production-grade, fully resumable scraping system designed for long-running tasks, unstable networks, and high-volume data collection.

---

## 🎥 Demo Video
YouTube Demo: https://www.youtube.com/watch?v=eX9hydLaTK8

---

## 🚀 Features
- Automatic airport URL discovery
- 70 date combinations per airport (5 departure dates × 14 durations)
- Full resume support using `progress.log`
- Saves raw HTML, TXT logs, and structured JSON
- Optional airport filtering via `included_airports.yaml`
- Stable long-run execution with recovery logic
- Suitable for periodic scraping and data pipelines

---

## 📁 Folder Structure
```
project/
├── main.py                      # Scraper engine
├── text_out.py                  # Converts HTML → text log
├── extract_parking_data.py      # Converts HTML → JSON
├── progress.log                 # Resume tracking file
├── included_airports.yaml       # Optional airport filter
│
├── core/
│   ├── airport_loader.py        # Loads airport URLs
│   ├── browser_controller.py    # Selenium automation
│   ├── finalizer.py             # End-of-run validation & cleanup
│   └── airports.txt             # Active airport queue
│
├── saved_pages/                 # Raw HTML
├── old_saved_pages/             # Archived HTML
├── text_out/                    # Log files
├── json_out/                    # Final JSON
```

---

## ⚙️ How It Works
### 1. main.py
- Loads airport list  
- Generates 70 combinations  
- Automates browser with undetected-chromedriver  
- Saves HTML and logs progress  

### 2. text_out.py
Parses HTML and creates `text_out/parkinglist_saved_pages.log`.

### 3. extract_parking_data.py
- Extracts structured parking data  
- Saves final dataset in `json_out/parking_data.json`  
- Moves processed HTML to timestamped archive  

### 4. finalizer.py
- Ensures all airports are finished  
- Clears progress  
- Prepares next execution run  

---

## 🔁 Resume Logic
- Every processed combination is logged  
- Already completed runs are skipped instantly  
- When all 70 combos are done → airport removed from `airports.txt`  
- When all airports are done:
  - JSON is regenerated  
  - progress.log is cleared  
  - pipeline resets  

---

## 📦 Dependencies
Install using:
```
pip install -r requirements.txt
```

requirements.txt:
```
undetected-chromedriver
selenium
beautifulsoup4
pyyaml
```

---

## ⚠️ Notes
### Slower PC?
Increase wait time:
```python
def load_parking_results(..., wait_time=22):
```
Recommended for low-end systems:
```
wait_time = 30
```

### Headless Mode (for servers / SSH)
```python
options.add_argument("--headless=new")
```

Recommended Chrome config:
```python
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
# options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome(options=options, use_subprocess=True)
```

---

## 🔠 Usage
```
python3 main.py
python3 text_out.py
python3 extract_parking_data.py
python3 core/finalizer.py
```

---

## 📜 License
MIT License – free to use, modify, and distribute.

---

## 👤 Maintainer
**Andrei Sorin Ștefan**
