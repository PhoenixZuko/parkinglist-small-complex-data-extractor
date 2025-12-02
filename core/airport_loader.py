import yaml
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def load_included_airports(yaml_file="included_airports.yaml"):
    try:
        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("included_airports", [])
    except Exception as e:
        print(f"[!] Error reading YAML file: {e}")
        return []

def generate_airport_list(output_file="airports.txt", yaml_file="included_airports.yaml"):
    included_airports = load_included_airports(yaml_file)
    if not included_airports:
        print("[!] No airports to include. Check your YAML file.")
        return

    # Start browser
    driver = webdriver.Chrome()
    driver.get("https://www.parkinglist.de/flughafen-parken/parken-flughafen-dresden")

    airport_urls = []

    try:
        wait = WebDriverWait(driver, 10)
        select_element = wait.until(EC.presence_of_element_located((By.ID, "abflughafen")))
        options = select_element.find_elements(By.TAG_NAME, "option")

        for option in options:
            url = option.get_attribute("value")
            if url and "parken-flughafen" in url:
                # Include URL only if any keyword is found
                if any(keyword.lower() in url.lower() for keyword in included_airports):
                    airport_urls.append(url.strip())

    except TimeoutException:
        print("[!] Dropdown with ID 'abflughafen' was not found – maybe the site layout changed.")
    finally:
        driver.quit()

    # Remove duplicates and sort
    unique_urls = sorted(set(airport_urls))

    # Save to file
    with open(output_file, "w", encoding="utf-8") as f:
        for url in unique_urls:
            f.write(url + "\n")

    print(f"[✓] Saved {len(unique_urls)} filtered airport URLs to {output_file}")

# Run directly
if __name__ == "__main__":
    generate_airport_list()
