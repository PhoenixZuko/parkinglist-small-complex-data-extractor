import os
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_FOLDER = 'saved_pages'
AIRPORTS_FILE = os.path.join('core', 'airports.txt')
OUTPUT_FOLDER = 'json_out'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
OUTPUT_JSON = os.path.join(OUTPUT_FOLDER, 'parking_data.json')


def parse_dates_from_filename(filename):
    match = re.search(r'(\d{4}-\d{2}-\d{2})→(\d{4}-\d{2}-\d{2})', filename)
    if match:
        start_str, end_str = match.groups()
        start = datetime.strptime(start_str, "%Y-%m-%d").replace(hour=7, minute=0)
        end = datetime.strptime(end_str, "%Y-%m-%d").replace(hour=21, minute=0)
        return start, end
    return None, None

def detect_parking_type(icon_div):
    parking_types = set()
    if icon_div:
        for icon in icon_div.find_all('p'):
            bg = icon.get('data-bg', '').lower()
            if 'shuttle' in bg:
                parking_types.add('shuttle')
            if 'valet' in bg:
                parking_types.add('valet')
    return ' | '.join(parking_types) if parking_types else 'unknown'

def extract_parking_data(filepath, scrape_link):
    airport_slug = scrape_link.split('/')[-1].replace('parken-flughafen-', '').replace('-', ' ').title()
    airport_slug = airport_slug.replace("Am Main", "am Main").replace("Koeln", "Köln").replace("Muenchen", "München")

    with open(filepath, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file.read(), 'html.parser')

    page_title = soup.title.string.strip() if soup.title else "unknown"
    place_tag = soup.find('h2')
    place_text = place_tag.get_text(strip=True) if place_tag else "unknown"

    parking_entries = soup.find_all('div', class_='airport_search')
    start_dt, end_dt = parse_dates_from_filename(filepath)
    scraped_timestamp = os.path.getmtime(filepath)
    scraped_at = datetime.fromtimestamp(scraped_timestamp).strftime('%Y-%m-%d %H:%M:%S')

    records = []
    for entry in parking_entries:
        # ✅ Check availability
        is_unavailable = entry.find('div', class_='not_available') is not None
        availability = "unavailable" if is_unavailable else "available"

        # ❗ Uncomment this line if you want to **exclude** unavailable ones
        # if availability == "unavailable":
        #     continue

        price_tag = entry.find('div', class_='kjll')
        if not price_tag:
            continue
        price_text = price_tag.get_text()
        price_match = re.findall(r"[-+]?\d[\d,\.]*", price_text)
        if not price_match:
            continue
        price = price_match[0].replace('.', '').replace(',', '')
        try:
            price_num = float(price)
        except ValueError:
            continue

        parking_type = detect_parking_type(entry.find('div', class_='iconDiv'))

        slug_tag = entry.find('div', class_='logoIcon')
        slug_img = slug_tag.find('img') if slug_tag else None
        parking_slug = slug_img.get('alt', '').strip() if slug_img else "unknown"

        duration_days = (end_dt - start_dt).days if start_dt and end_dt else 0
        duration_hours = int((end_dt - start_dt).total_seconds() // 3600) if start_dt and end_dt else 0

        price_per_day = round(price_num / duration_days, 2) if duration_days else 0
        price_per_hour = round(price_num / duration_hours, 2) if duration_hours else 0

        detail_text = entry.get_text().lower()
        parking_detail_type = 'covered' if 'überdacht' in detail_text or 'gedeckt' in detail_text else 'open'

        address_tag = entry.find(string=re.compile("Adresse", re.IGNORECASE))
        address = address_tag.find_next().get_text(strip=True) if address_tag else "unknown"

        services_div = entry.find('div', class_='air_desript')
        included_services = [li.get_text(strip=True) for li in services_div.find_all('li')] if services_div else []

        book_link_tag = entry.find('a', string=re.compile("jetzt buchen", re.IGNORECASE))
        booking_link = book_link_tag['href'] if book_link_tag else scrape_link

        record = {
            "Title": page_title,
            "Place": place_text,
            "ParkingFromDt": start_dt.strftime('%Y-%m-%d %H:%M:%S'),
            "ParkingToDt": end_dt.strftime('%Y-%m-%d %H:%M:%S'),
            "DurationDays": duration_days,
            "DurationHours": duration_hours,
            "Price": price,
            "Currency": "EURO",
            "PricePerDay": price_per_day,
            "PricePerHour": price_per_hour,
            "ParkingType": parking_type,
            "ParkingDetailType": parking_detail_type,
            "ParkingSlug": parking_slug,
            "Address": address,
            "IncludedServices": included_services,
            "BookingLink": booking_link,
            "ScrapeLink": scrape_link,
            "ScrapedAt": scraped_at,
            "Availability": availability
        }

        records.append((airport_slug, record))
    return records

def process_file(html_file, scrape_links):
    matched = [link for link in scrape_links if link.split("/")[-1] in html_file.name]
    scrape_link = matched[0] if matched else f"https://dummy-link/{html_file.name}"
    return extract_parking_data(str(html_file), scrape_link)

def main():
    if not os.path.exists(INPUT_FOLDER) or not os.path.exists(AIRPORTS_FILE):
        print("❌ 'saved_pages' folder or 'core/airports.txt' file is missing.")
        return

    with open(AIRPORTS_FILE, 'r', encoding='utf-8') as f:
        scrape_links = [line.strip() for line in f if line.strip()]

    html_files = sorted(Path(INPUT_FOLDER).glob("*.html"))
    if not html_files:
        print("❌ No HTML files found in 'saved_pages'.")
        return

    data = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_file, html_file, scrape_links): html_file for html_file in html_files}
        for future in as_completed(futures):
            try:
                results = future.result()
                for airport_slug, record in results:
                    data.setdefault(airport_slug, []).append(record)
            except Exception as e:
                print(f"❌ Error processing a file: {e}")

    for airport in data:
        data[airport] = sorted(data[airport], key=lambda x: x["DurationDays"], reverse=True)

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Data successfully saved to '{OUTPUT_JSON}'")

    # Move processed files
    from shutil import move
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_folder = os.path.join("old_saved_pages", timestamp)
    os.makedirs(archive_folder, exist_ok=True)

    for html_file in html_files:
        destination = os.path.join(archive_folder, html_file.name)
        try:
            move(str(html_file), destination)
        except Exception as e:
            print(f"❌ Failed to move file {html_file.name}: {e}")

    print(f"📦 All processed HTML files moved to '{archive_folder}'")

if __name__ == "__main__":
    main()
