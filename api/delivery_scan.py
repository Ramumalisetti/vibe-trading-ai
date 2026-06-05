"""
Delivery Volume Scanner — NSE Bhavcopy based
Criteria:
  1. Delivery% today > Delivery% yesterday
  2. Delivery% today > 50%
  3. (Day Volume / Week Volume Avg) >= 3
  4. Day change % > 0
  5. Day Volume >= 500,000
  6. Market Cap > ₹3000 Crore
"""
from http.server import BaseHTTPRequestHandler
import json, io, os
import requests
import pandas as pd
import yfinance as yf
import concurrent.futures
from datetime import datetime, timedelta

NSE_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://www.nseindia.com/',
    'Connection': 'keep-alive',
}

def prev_trading_day(date, n=1):
    """Return date minus n trading days (skip Sat/Sun)."""
    d = date
    count = 0
    while count < n:
        d -= timedelta(days=1)
        if d.weekday() < 5:   # 0=Mon … 4=Fri
            count += 1
    return d

def get_bhavcopy(date):
    """Download NSE full equity bhavcopy (includes DELIV_PER) for given date."""
    date_str = date.strftime("%d%m%Y")
    url = f"https://archives.nseindia.com/products/content/sec_bhavdata_full_{date_str}.csv"
    session = requests.Session()
    # Warm up session with NSE home to get cookies
    try:
        session.get("https://www.nseindia.com", headers=NSE_HEADERS, timeout=10)
    except Exception:
        pass
    r = session.get(url, headers=NSE_HEADERS, timeout=25)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = [c.strip() for c in df.columns]
    return df

def fetch_bhavcopy_with_retry(base_date, skip=0):
    """Try downloading bhavcopy starting from base_date - skip trading days."""
    for attempt in range(skip, skip + 5):
        d = prev_trading_day(base_date, attempt) if attempt > 0 else base_date
        try:
            df = get_bhavcopy(d)
            if len(df) > 100:   # sanity: should have many rows
                return df, d
        except Exception:
            continue
    return None, None

def enrich_with_weekly_vol_and_mc(row):
    """Fetch weekly avg volume + market cap for a single stock via yfinance."""
    sym = str(row['SYMBOL']).strip()
    try:
        ticker = yf.download(sym + ".NS", period="15d", interval="1d",
                             progress=False, auto_adjust=True)
        if ticker.empty or len(ticker) < 5:
            return None
        if isinstance(ticker.columns, pd.MultiIndex):
            ticker.columns = ticker.columns.droplevel(1)

        # Weekly avg = last 5 complete sessions (exclude today)
        week_vols    = ticker['Volume'].iloc[-6:-1]
        week_avg_vol = float(week_vols.mean())
        if week_avg_vol == 0:
            return None

        vol_ratio = float(row['VOL_TODAY']) / week_avg_vol
        if vol_ratio < 3.0:
            return None

        # Market cap (fast_info is faster than full info)
        fast = yf.Ticker(sym + ".NS").fast_info
        mc_inr = getattr(fast, 'market_cap', 0) or 0
        mc_crore = mc_inr / 1e7   # INR → Crore
        if mc_crore < 3000:
            return None

        return {
            'stock':             sym,
            'close':             round(float(row['CLOSE']), 2),
            'prev_close':        round(float(row['PREV_CLOSE']), 2),
            'day_chg_pct':       round(float(row['DAY_CHG_PCT']), 2),
            'vol_today':         int(row['VOL_TODAY']),
            'week_avg_vol':      int(week_avg_vol),
            'vol_ratio':         round(vol_ratio, 2),
            'deliv_pct_today':   round(float(row['DELIV_PCT_TODAY']), 2),
            'deliv_pct_prev':    round(float(row['DELIV_PCT_PREV']), 2),
            'deliv_qty':         int(row['DELIV_QTY']),
            'market_cap_cr':     round(mc_crore),
        }
    except Exception:
        return None


def run_delivery_scan():
    today = datetime.now()

    # ── Step 1: Download today's and previous bhavcopy ─────────────────────────
    bhav_today, date_today = fetch_bhavcopy_with_retry(today, skip=0)
    if bhav_today is None:
        return [], "Could not download today's NSE bhavcopy. Market may be closed or data not published yet."

    bhav_prev, _ = fetch_bhavcopy_with_retry(date_today, skip=1)
    if bhav_prev is None:
        return [], "Could not download previous trading day's NSE bhavcopy."

    # ── Step 2: Filter to EQ series only ──────────────────────────────────────
    bhav_today = bhav_today[bhav_today['SERIES'].str.strip() == 'EQ'].copy()
    bhav_prev  = bhav_prev[bhav_prev['SERIES'].str.strip()  == 'EQ'].copy()

    # Standardise column names (NSE columns may have spaces)
    def get_col(df, *candidates):
        for c in candidates:
            if c in df.columns:
                return c
        return None

    for df_name, df in [("today", bhav_today), ("prev", bhav_prev)]:
        deliv_col = get_col(df, 'DELIV_PER', 'DELIV_PER ', ' DELIV_PER')
        if deliv_col and deliv_col != 'DELIV_PER':
            df.rename(columns={deliv_col: 'DELIV_PER'}, inplace=True)

    # ── Step 3: Build merged dataframe ────────────────────────────────────────
    today_needed = ['SYMBOL', 'CLOSE', 'PREVCLOSE', 'TOTTRDQTY', 'DELIV_QTY', 'DELIV_PER']
    # Handle alternate column spellings
    close_col   = get_col(bhav_today, 'CLOSE', ' CLOSE')
    prev_col    = get_col(bhav_today, 'PREVCLOSE', 'PREV_CLOSE', ' PREVCLOSE')
    vol_col     = get_col(bhav_today, 'TOTTRDQTY', ' TOTTRDQTY')
    deliv_q_col = get_col(bhav_today, 'DELIV_QTY', ' DELIV_QTY')
    deliv_p_col = get_col(bhav_today, 'DELIV_PER', ' DELIV_PER')
    sym_col     = get_col(bhav_today, 'SYMBOL', ' SYMBOL')

    if not all([close_col, prev_col, vol_col, deliv_q_col, deliv_p_col, sym_col]):
        return [], f"Bhavcopy columns not as expected. Got: {list(bhav_today.columns)[:10]}"

    today_df = bhav_today[[sym_col, close_col, prev_col, vol_col, deliv_q_col, deliv_p_col]].copy()
    today_df.columns = ['SYMBOL','CLOSE','PREV_CLOSE','VOL_TODAY','DELIV_QTY','DELIV_PCT_TODAY']

    sym_col_p   = get_col(bhav_prev, 'SYMBOL', ' SYMBOL')
    deliv_p_col_p = get_col(bhav_prev, 'DELIV_PER', ' DELIV_PER')
    prev_df = bhav_prev[[sym_col_p, deliv_p_col_p]].copy()
    prev_df.columns = ['SYMBOL', 'DELIV_PCT_PREV']

    df = today_df.merge(prev_df, on='SYMBOL', how='inner')

    # Convert to numeric
    for col in ['CLOSE','PREV_CLOSE','VOL_TODAY','DELIV_QTY','DELIV_PCT_TODAY','DELIV_PCT_PREV']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=['CLOSE','PREV_CLOSE','VOL_TODAY','DELIV_PCT_TODAY','DELIV_PCT_PREV'], inplace=True)

    df['DAY_CHG_PCT'] = (df['CLOSE'] - df['PREV_CLOSE']) / df['PREV_CLOSE'] * 100

    # ── Step 4: Apply fast filters (no yfinance needed yet) ───────────────────
    filtered = df[
        (df['DELIV_PCT_TODAY'] > df['DELIV_PCT_PREV']) &   # delivery improving
        (df['DELIV_PCT_TODAY'] > 50) &                      # >50% delivery
        (df['DAY_CHG_PCT'] > 0) &                           # positive close
        (df['VOL_TODAY'] >= 500_000)                         # min 5L volume
    ].copy()

    if filtered.empty:
        return [], None

    # ── Step 5: Enrich with weekly vol + market cap ───────────────────────────
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(enrich_with_weekly_vol_and_mc, row): row['SYMBOL']
                   for _, row in filtered.iterrows()}
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            if res:
                results.append(res)

    # Sort: highest delivery% first, then highest vol ratio
    results.sort(key=lambda x: (-x['deliv_pct_today'], -x['vol_ratio']))
    return results, None


class handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        data, err = run_delivery_scan()
        if err:
            self.wfile.write(json.dumps({"status": "error", "error": err}).encode())
        else:
            self.wfile.write(json.dumps({
                "status": "success",
                "total":  len(data),
                "data":   data,
            }).encode())
