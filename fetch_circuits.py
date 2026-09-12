import json
import requests

def fetch_price_band_changes():
    # Official NSE API endpoint powering the /reports/price-band-changes page
    api_url = "https://www.nseindia.com/api/price-band-changes"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/reports/price-band-changes"
    }

    session = requests.Session()
    
    try:
        # Step 1: Establish session and retrieve cookies from main site
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        session.get("https://www.nseindia.com/reports/price-band-changes", headers=headers, timeout=10)
        
        # Step 2: Request the price band changes JSON data
        response = session.get(api_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            formatted_list = []
            
            # Key inside JSON response containing the list of modified securities
            records = data.get('data', []) if isinstance(data, dict) else data
            
            for item in records:
                # Extract Symbol and New Price Band percentage
                symbol = str(item.get('symbol', '')).strip().upper()
                # Band field may be named 'newBand', 'applicableBand', or 'band'
                band = str(item.get('newBand', item.get('applicableBand', item.get('band', '')))).strip().replace('%', '')
                
                if symbol and band:
                    formatted_list.append(f"{symbol}:{band}")
            
            if formatted_list:
                output_string = ",".join(formatted_list)
                with open("nse_circuit_data.txt", "w") as f:
                    f.write(output_string)
                print(f"Successfully processed {len(formatted_list)} stocks from Price Band Changes report.")
                return
            else:
                print("No price band revisions found for today.")
                
    except Exception as e:
        print(f"Error fetching price band changes: {e}")

    # Fallback if no revisions are listed or API returns empty (e.g., non-trading days)
    with open("nse_circuit_data.txt", "w") as f:
        f.write("")
    print("nse_circuit_data.txt updated with empty state.")

if __name__ == "__main__":
    fetch_price_band_changes()
