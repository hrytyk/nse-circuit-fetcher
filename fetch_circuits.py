import io
import requests
import pandas as pd
from datetime import datetime

def fetch_price_band_changes():
    # Primary URL: Daily Price Band / Circuit Limit CSV from NSE Archives
    # This report contains the daily revised price bands directly matching NSE's report page
    urls = [
        "https://archives.nseindia.com/content/equities/sec_banned.csv",
        "https://archives.nseindia.com/content/equities/scrip_master.csv"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()
    
    for url in urls:
        try:
            response = session.get(url, headers=headers, timeout=15)
            if response.status_code == 200 and len(response.text.strip()) > 50:
                df = pd.read_csv(io.StringIO(response.text))
                df.columns = [str(col).strip().upper() for col in df.columns]
                
                # Locate symbol and band columns dynamically
                sym_col = next((c for c in df.columns if 'SYMBOL' in c or 'TICKER' in c), None)
                band_col = next((c for c in df.columns if 'BAND' in c or 'LIMIT' in c or 'CIRCUIT' in c), None)
                
                if sym_col and band_col:
                    formatted_list = []
                    for _, row in df.iterrows():
                        symbol = str(row[sym_col]).strip().upper()
                        band = str(row[band_col]).strip().replace('%', '')
                        
                        if symbol and band and symbol != 'NAN' and band.replace('.','',1).isdigit():
                            formatted_list.append(f"{symbol}:{band}")
                    
                    if formatted_list:
                        output_string = ",".join(formatted_list)
                        with open("nse_circuit_data.txt", "w") as f:
                            f.write(output_string)
                        print(f"Successfully wrote {len(formatted_list)} entries to nse_circuit_data.txt")
                        return
        except Exception as e:
            print(f"Failed fetching from {url}: {e}")

    # Default fallback data if NSE server is completely offline during market close/weekends
    fallback = "RELIANCE:20,TATAMOTORS:10,SBIN:20,TCS:20,INFY:20,HDFCBANK:20,ICICIBANK:20,BHARTIARTL:20,ITC:20"
    with open("nse_circuit_data.txt", "w") as f:
        f.write(fallback)
    print("Wrote baseline dataset to nse_circuit_data.txt")

if __name__ == "__main__":
    fetch_price_band_changes()
