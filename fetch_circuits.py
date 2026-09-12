import io
import requests
import pandas as pd

def fetch_nse_circuit_data():
    # Official NSE Daily Price Band / Security Master URL
    report_url = "https://archives.nseindia.com/content/equities/sec_banned.csv"
    
    # Custom headers mimicking a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()
    
    try:
        # Step 1: Establish session cookies by visiting the main site first
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        
        # Step 2: Download the CSV report
        response = session.get(report_url, headers=headers, timeout=15)
        
        if response.status_code == 200 and len(response.text.strip()) > 0:
            # Parse CSV content
            df = pd.read_csv(io.StringIO(response.text))
            df.columns = [col.strip().upper() for col in df.columns]
            
            formatted_list = []
            
            # Find symbol and band columns dynamically
            sym_col = next((col for col in df.columns if "SYMBOL" in col), None)
            band_col = next((col for col in df.columns if "BAND" in col or "LIMIT" in col), None)
            
            if sym_col and band_col:
                for _, row in df.iterrows():
                    symbol = str(row[sym_col]).strip().upper()
                    band = str(row[band_col]).strip().replace('%', '')
                    if symbol and band and symbol != 'NAN':
                        formatted_list.append(f"{symbol}:{band}")
                        
            if formatted_list:
                output_string = ",".join(formatted_list)
                with open("nse_circuit_data.txt", "w") as f:
                    f.write(output_string)
                print(f"Successfully wrote {len(formatted_list)} records to nse_circuit_data.txt")
                return

        print(f"Direct download failed (Status: {response.status_code}). Using backup master dataset.")
        
    except Exception as e:
        print(f"Error fetching live data: {e}")

    # Fallback dataset if NSE blocks cloud runner IP
    fallback_data = "GENESYS:20,RELIANCE:20,TATAMOTORS:10,SBIN:20,TCS:20,INFY:20,HDFCBANK:20,ICICIBANK:20,BHARTIARTL:20,ITC:20"
    with open("nse_circuit_data.txt", "w") as f:
        f.write(fallback_data)
    print("Fallback dataset written to nse_circuit_data.txt")

if __name__ == "__main__":
    fetch_nse_circuit_data()
