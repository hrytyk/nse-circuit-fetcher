import io
import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_price_band_changes():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()
    today = datetime.now()
    
    # Check the last 5 days to handle weekends and market holidays
    for i in range(5):
        target_date = today - timedelta(days=i)
        date_str = target_date.strftime("%d%m%Y")  # Format: DDMMYYYY
        
        # Static archival link for "Price Band changes from next trade date"
        url = f"https://archives.nseindia.com/content/equities/eq_band_changes_{date_str}.csv"
        
        try:
            response = session.get(url, headers=headers, timeout=10)
            if response.status_code == 200 and len(response.text.strip()) > 10:
                df = pd.read_csv(io.StringIO(response.text))
                df.columns = [str(c).strip().upper() for c in df.columns]
                
                # Dynamic column lookup for Symbol and New Band Percentage
                sym_col = next((c for c in df.columns if 'SYMBOL' in c or 'TICKER' in c), None)
                band_col = next((c for c in df.columns if 'NEW' in c or 'BAND' in c or 'LIMIT' in c or 'APPLICABLE' in c), None)
                
                if sym_col and band_col:
                    formatted_list = []
                    for _, row in df.iterrows():
                        symbol = str(row[sym_col]).strip().upper()
                        band = str(row[band_col]).strip().replace('%', '')
                        
                        if symbol and band and symbol != 'NAN':
                            formatted_list.append(f"{symbol}:{band}")
                    
                    if formatted_list:
                        output_string = ",".join(formatted_list)
                        with open("nse_circuit_data.txt", "w") as f:
                            f.write(output_string)
                        print(f"Successfully loaded {len(formatted_list)} stocks from date: {date_str}")
                        return
        except Exception as e:
            print(f"Failed to fetch date {date_str}: {e}")

    # Baseline fallback if no file is found (e.g., multi-day holiday window)
    fallback = "RELIANCE:20,TATAMOTORS:10,SBIN:20,TCS:20,INFY:20,HDFCBANK:20"
    with open("nse_circuit_data.txt", "w") as f:
        f.write(fallback)
    print("Writing default baseline dataset.")

if __name__ == "__main__":
    fetch_price_band_changes()
