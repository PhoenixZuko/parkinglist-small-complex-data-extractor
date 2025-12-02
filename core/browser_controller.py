from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import os

def initialize_session(driver):
    """Accept cookies and close Tally popup once at the beginning."""
    wait = WebDriverWait(driver, 5)
    print("[⋅] Initializing session (cookies & popup)...")

    # Accept cookies
    try:
        cookie_btn = wait.until(EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")))
        cookie_btn.click()
        print("[✓] Cookies accepted.")
    except:
        print("[⋅] No cookie prompt.")

    # Close Tally popup
    try:
        iframe = WebDriverWait(driver, 1.5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[src*=\"tally.so/popup\"]')))
        driver.switch_to.frame(iframe)
        close_btn = WebDriverWait(driver, 1.5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg')))
        close_btn.click()
        print("[✓] Tally popup closed.")
        driver.switch_to.default_content()
    except:
        print("[⋅] No Tally popup.")
        driver.switch_to.default_content()

def load_parking_results(url, driver, departure_date, return_date, wait_time=22): #You can increase it from 22 to 30 or more depending on your system speed
    driver.get(url)
    print(f"[⋅] Page loaded: {url}")
    wait = WebDriverWait(driver, wait_time)
    collected_pages = []
    page_number = 1

    try:
        # Set date fields
        driver.execute_script(f"document.getElementById('startDay_input').value = '{departure_date}'")
        driver.execute_script(f"document.getElementById('endDay_input').value = '{return_date}'")
        print(f"[✓] Dates set: {departure_date} → {return_date}")

        # Click the "Search" button
        try:
            search_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="Search"]/..')))
            driver.execute_script("arguments[0].scrollIntoView(true);", search_btn)
            driver.execute_script("arguments[0].click();", search_btn)
            print("[→] Clicked Search.")
        except Exception as e:
            print(f"[!] Could not click Search button. Details: {e}")
            return [], url

        # Pagination loop
        while True:
            print(f"[⏳] Waiting for results page {page_number}...")
            time.sleep(wait_time)
            html = driver.page_source
            collected_pages.append((page_number, html))
            print(f"[✓] Page {page_number} collected.")

            # Check for next page
            try:
                next_button = driver.find_element(By.XPATH, '//div[@class="pag_text" and not(contains(@class, "disabled")) and text()="Next"]')
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(2)
                next_button.click()
                page_number += 1
            except:
                print("[!] Next button not found. Ending pagination.")
                break

    except Exception as e:
        print(f"[✖] General error while processing {url}:\n{e}")
        os.makedirs("screenshots", exist_ok=True)
        screenshot_path = f"screenshots/error_{int(time.time())}.png"
        driver.save_screenshot(screenshot_path)
        print(f"[✖] Screenshot saved: {screenshot_path}")

    return collected_pages, url
