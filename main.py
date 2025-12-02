import os
import datetime
import warnings
import contextlib
import sys
import undetected_chromedriver as uc
from core.browser_controller import load_parking_results, initialize_session
from core.airport_loader import generate_airport_list
import core.finalizer

def build_target_dates():
    target_dates = []
    today = datetime.date.today()
    durations = range(1, 15)  # 14 durations
    for n in range(1, 6):     # 5 from-dates
        parking_from_date = today + datetime.timedelta(days=n)
        for duration in durations:
            parking_to_date = parking_from_date + datetime.timedelta(days=duration)
            target_dates.append({
                "from": parking_from_date.strftime("%d/%m/%Y"),
                "to": parking_to_date.strftime("%d/%m/%Y"),
                "from_raw": parking_from_date.strftime("%Y-%m-%d"),
                "to_raw": parking_to_date.strftime("%Y-%m-%d")
            })
    return target_dates

def read_airport_list(file_path):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        print("[⋅] Airport list is empty or missing. Generating new list...")
        generate_airport_list(output_file=file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def update_airport_list(file_path, processed_url):
    with open(file_path, "r", encoding="utf-8") as f:
        airports = [line.strip() for line in f if line.strip()]
    updated_list = [url for url in airports if url != processed_url]
    with open(file_path, "w", encoding="utf-8") as f:
        for url in updated_list:
            f.write(url + "\n")

def load_progress(log_file):
    if not os.path.exists(log_file):
        return set()
    with open(log_file, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def append_to_log(log_file, line):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def main():
    airport_file = os.path.join("core", "airports.txt")
    log_file = "progress.log"

    airport_urls = read_airport_list(airport_file)
    target_dates = build_target_dates()
    progress_set = load_progress(log_file)

    if not airport_urls:
        print("[✓] All airports processed. Nothing to do.")
        return

    # Launch browser
    options = uc.ChromeOptions()
    # Maximized window (for better element rendering)
    options.add_argument("--start-maximized")
    # Optional: enable headless mode (runs browser in background, no GUI)
    # Uncomment the next line to run in headless (hidden) mode:
    # options.add_argument("--headless=new")  # Use "new" for better stability

    # Performance and compatibility flags
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Start the Chrome driver

    driver = uc.Chrome(options=options, use_subprocess=True)

    try:
        print(f"[⋅] Initializing session on: {airport_urls[0]}")
        driver.get(airport_urls[0])
        initialize_session(driver)

        for airport_url in airport_urls:
            print(f"\n[→] Starting airport: {airport_url}")
            completed_combos = 0

            for combo in target_dates:
                combo_key = f"{airport_url}|{combo['from_raw']}|{combo['to_raw']}"
                if combo_key in progress_set:
                    print(f"[⏩] Skipping already processed: {combo_key}")
                    completed_combos += 1
                    continue

                print(f"[⋅] Processing: {combo['from']} → {combo['to']}")

                pages, url = load_parking_results(
                    airport_url,
                    driver,
                    combo["from"],
                    combo["to"]
                )

                if pages:
                    os.makedirs("saved_pages", exist_ok=True)
                    name = url.split("/")[-1]
                    for page_number, html in pages:
                        suffix = f"_page{page_number}" if page_number > 1 else ""
                        filename = f"{name}_{combo['from_raw']}→{combo['to_raw']}{suffix}.html"
                        output_file = os.path.join("saved_pages", filename)

                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(html)
                        print(f"[✓] Saved: {output_file}")

                    append_to_log(log_file, combo_key)
                    progress_set.add(combo_key)
                    completed_combos += 1
                else:
                    print(f"[!] No results for {combo_key}")

            if completed_combos == len(target_dates):
                update_airport_list(airport_file, airport_url)
                print(f"[✓] All combinations done for: {airport_url}")
            else:
                print(f"[!] Partial progress saved for: {airport_url}")

    finally:
        driver.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    else:
        import core.finalizer
        core.finalizer.finalize_progress()

    print("✅ Program ended successfully (Chrome was closed).")
