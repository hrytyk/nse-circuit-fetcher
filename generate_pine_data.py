import datetime
import requests
import pandas as pd
from io import StringIO

def fetch_and_generate():
    today = datetime.date.today()
    date_str = today.strftime("%d%m%Y")

    # Target URL for official NSE Daily Price Band Complete Report
    url = f"https://www.nseindia.com/content/circulars/bulk/sec_list_{date_str}.csv"
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.nseindia.com/all-reports"
    })
    
    try:
        session.get("https://www.nseindia.com", timeout=10)
        res = session.get(url, timeout=10)
    except Exception as e:
        print(f"Error connecting to NSE: {e}")
        return

    if res.status_code != 200:
        print(f"No file available for date (Status Code: {res.status_code}). Might be market holiday or non-trading hours.")
        return

    df = pd.read_csv(StringIO(res.text))
    df.columns = [c.strip().lower() for c in df.columns]

    sym_col = [c for c in df.columns if 'symbol' in c or 'sec' in c][0]
    upper_col = [c for c in df.columns if 'upper' in c or 'band' in c][0]
    lower_col = [c for c in df.columns if 'lower' in c or 'band' in c][0]

    pair_list = []
    for _, row in df.iterrows():
        sym = str(row[sym_col]).strip().upper()
        try:
            up = float(row[upper_col])
            low = float(row[lower_col])
            pct = round(((up - low) / (up + low)) * 100)
            pair_list.append(f"{sym}:{pct}")
        except:
            continue

    # Join stock data into a single string
    data_str = ",".join(pair_list)

    # Save to a raw text file inside the GitHub repository
    with open("nse_circuit_data.txt", "w") as f:
        f.write(data_str)
        
    print(f"Successfully formatted {len(pair_list)} stock circuit bands.")

if __name__ == "__main__":
    fetch_and_generate()
