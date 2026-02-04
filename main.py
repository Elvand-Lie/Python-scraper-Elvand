import requests
from bs4 import BeautifulSoup
import json
import sys
from collections import defaultdict

# custom error so we don't crash the main app
class ScraperError(Exception):
    pass

def scrape_akiya_table(url, table_class=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        # fix japanese text encoding
        response.encoding = response.apparent_encoding
    except requests.exceptions.RequestException as e:
        raise ScraperError(f"Network error: {e}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # grab specific table if needed, otherwise grab all
    if table_class:
        tables = soup.find_all('table', class_=table_class)
    else:
        tables = soup.find_all('table')

    if not tables:
        return None

    # use defaultdict to handle duplicate keys easily
    data = defaultdict(list)

    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows:
            header = row.find('th')
            value = row.find('td')

            if header and value:
                key = header.get_text(strip=True)
                val = value.get_text(strip=True)
                
                if val:
                    data[key].append(val)
    
    # join multiple values with /
    clean_data = {}
    for k, v in data.items():
        if len(v) == 1:
            clean_data[k] = v[0]
        else:
            clean_data[k] = " / ".join(v)
            
    return clean_data

def main():
    target_url = "https://katashina-iju.jp/akiya/no-80%e3%80%80オグナほたかスキー場内の物件（cafeめし屋ごは/"
    
    print(f"Fetching: {target_url}...")
    
    try:
        result = scrape_akiya_table(target_url)
        
        if result:
            json_output = json.dumps(result, ensure_ascii=False, indent=4)
            print("\n--- JSON Output ---")
            print(json_output)
            
            with open('akiya_data.json', 'w', encoding='utf-8') as f:
                f.write(json_output)
                print("\nSaved to 'akiya_data.json'")
        else:
            print("No data found.")

    except ScraperError as e:
        print(f"Scraper failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()