import io
import pandas as pd
import requests

def fetch_nse_circuit_data():
    # Official NSE Daily Security Master Report URL
    url = "https://archives.nseindia.com/content/equities/sec_banned.csv"
    
    # Custom headers required to bypass NSE 403 Forbidden blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()
    # Establish session cookies by visiting the main home page
    session.get("https://www.nseindia.com", headers=headers, timeout=10)
    
    # Download the CSV price band report from NSE
    report_url = "https://archives.nseindia.com/content/equities/sec_banned.csv"
    response = session.get(report_url, headers=headers, timeout=15)

    if response.status_code == 200:
        df = pd.read_csv(io.StringIO(response.text))
        
        # Clean up column headers (strip whitespace and uppercase)
        df.columns = [col.strip().upper() for col in df.columns]
        
        # Extract Symbol and Applicable Band percentage columns
        formatted_list = []
        for _, row in df.iterrows():
            symbol = str(row.get('SYMBOL', '')).strip()
            # Extract numeric value for circuit band percentage
            band = str(row.get('APPLICABLE BAND', '')).strip().replace('%', '')
            
            if symbol and band and band.isdigit():
                formatted_list.append(f"{symbol}:{band}")

        # Join into single string formatted for TradingView input
        output_string = ",".join(formatted_list)
        
        # Save output string to repository text file
        with open("nse_circuit_data.txt", "w") as f:
            f.write(output_string)
            
        print(f"Successfully processed {len(formatted_list)} stocks into nse_circuit_data.txt")
    else:
        print(f"Failed to fetch data from NSE. HTTP Status: {response.status_code}")

if __name__ == "__main__":
    fetch_nse_circuit_data()
