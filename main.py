import requests
from bs4 import BeautifulSoup
import json
import sys

def scrape_akiya_table(url):
    # Use a real User-Agent. 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise error for 404/500
        
        # Ensure correct encoding for Japanese characters
        response.encoding = response.apparent_encoding 

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'html.parser')

    # We look for the first significant table or specific headers.
    tables = soup.find_all('table') 

    if not tables:
        print("No tables found.")
        return {}

    data = {}

    # Loop through every table found on the page
    for table in tables:
        rows = table.find_all('tr')
        
        for row in rows:
            header = row.find('th')
            value = row.find('td')

            if header and value:
                key_text = header.get_text(strip=True)
                value_text = value.get_text(strip=True)
                
                # Check if key already exists (to prevent overwriting if duplicates exist)
                if key_text not in data:
                    data[key_text] = value_text
                else:
                    # Append if duplicate key (rare but happens)
                    data[key_text] = f"{data[key_text]} / {value_text}"
    
    return data

def main():
    target_url = "https://katashina-iju.jp/akiya/no-80%e3%80%80オグナほたかスキー場内の物件（cafeめし屋ごは/"
    
    print(f"Fetching data from: {target_url}...")
    result = scrape_akiya_table(target_url)

    # 4. output: Print as formatted JSON
    if result:
        json_output = json.dumps(result, ensure_ascii=False, indent=4)
        print("\n--- Extracted Data (JSON) ---")
        print(json_output)
        
        # Optional: Save to file
        with open('akiya_data.json', 'w', encoding='utf-8') as f:
            f.write(json_output)
            print("\nSaved to 'akiya_data.json'")
    else:
        print("Extraction failed.")

if __name__ == "__main__":
    main()