import os
import re
import json
from bs4 import BeautifulSoup

input_folder = "saved_pages"
output_folder = "text_out"
output_log = os.path.join(output_folder, "parkinglist_saved_pages.log")

def extract_dates_from_filename(filename):
    match = re.search(r'_(\d{4}-\d{2}-\d{2})→(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1), match.group(2)
    return None, None

def extract_airport_from_filename(filename):
    match = re.search(r'parken-flughafen-([a-z\-]+)_', filename)
    if match:
        return match.group(1)
    return "unknown"

def process_html_file(filepath, filename):
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    products = soup.findAll('div', {'class': 'airport_search'})

    from_date, to_date = extract_dates_from_filename(filename)
    airport_code = extract_airport_from_filename(filename)
    scrape_link = f"https://www.parkinglist.de/flughafen-parken/parken-flughafen-{airport_code}?param=newSearch"

    results = []

    for product in products:
        try:
            price_text = product.find('div', class_='kjll').get_text()
            price = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", price_text)[0]
            currency = "EURO"
            parking_slug = product.find('div', class_='logoIcon').find('img')["alt"].strip()

            parking_type = ''
            icons = product.find('div', class_='iconDiv').find_all('p')
            for icon in icons:
                icon_name = icon.get('data-bg', '').lower()
                if 'shuttle' in icon_name:
                    parking_type += 'shuttle'
                if 'valet' in icon_name:
                    parking_type += '| valet'
            parking_type = parking_type.strip('| ')

            item = {
                "ScrapeSource": "parkinglist",
                "AirportSlug": airport_code,
                "IATA": airport_code.upper(),
                "ParkingSlug": parking_slug,
                "ParkingType": parking_type,
                "ParkingFromDt": from_date + " 07:00",
                "ParkingToDt": to_date + " 21:00",
                "Price": price,
                "Currency": currency,
                "ScrapeLink": scrape_link
            }

            results.append(json.dumps(item, ensure_ascii=False))
        except Exception as e:
            print(f"Error parsing product in file {filename}: {e}")

    return results

def main():
    all_results = []

    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(input_folder):
        if file.endswith(".html"):
            filepath = os.path.join(input_folder, file)
            print(f"Processing: {file}")
            results = process_html_file(filepath, file)
            all_results.extend(results)

    with open(output_log, "w", encoding="utf-8") as out_file:
        for line in all_results:
            out_file.write(line + "\n")

    print(f"✅ Done. Saved {len(all_results)} entries to: {output_log}")

if __name__ == "__main__":
    main()
