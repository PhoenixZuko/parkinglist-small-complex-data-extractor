# 💡 Running the Airport Parking Scraper in Jupyter Notebook

If you prefer to run the script in a Jupyter Notebook environment, here are a few recommendations to ensure everything works smoothly:

---

## ✅ 1. Install Required Packages

In a notebook cell, run:

```python
!pip install undetected-chromedriver selenium beautifulsoup4 pyyaml
```

Make sure these are installed in the same environment where Jupyter is running.

---

## ✅ 2. Split the Code into Cells

Divide the Python script into logical sections:

* Imports
* Utility functions (date builder, logging, scraping logic)
* Browser setup
* Execution loop (airport + date)

You can use `# %%` to separate code blocks if you're using JupyterLab or VSCode.

---

## ✅ 3. Notes on ChromeDriver

* `undetected-chromedriver` will automatically download and launch the right driver version.
* Make sure Chrome/Chromium is installed and accessible on your system.
* Avoid using headless mode if you're running locally and want to debug.

---

## ⚠️ Additional Tips

* Long loops: avoid printing too much in loops – Jupyter may slow down.
* If you face timeout issues, increase the `wait_time` parameter in `browser_controller.py`.
* You can test with a **single airport + one date range** first, before running all combinations.

---

## 🧪 Example Snippet to Test One Case

```python
from core.browser_controller import load_parking_results
from core.airport_loader import generate_airport_list
import undetected_chromedriver as uc

options = uc.ChromeOptions()
driver = uc.Chrome(options=options)

url = "https://www.parkinglist.de/flughafen-parken/parken-flughafen-bremen"
combo = {"from": "14/05/2025", "to": "20/05/2025"}

pages, url = load_parking_results(url, driver, combo['from'], combo['to'])
```

---

## ✅ Final Notes

Running the scraper in Jupyter works great for debugging, testing, or integrating into a data pipeline. Let me know if you'd like a `.ipynb` version or a simplified test notebook.
