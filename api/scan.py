from http.server import BaseHTTPRequestHandler
import json
import yfinance as yf
import pandas as pd
import numpy as np
import concurrent.futures

# ── Nifty 500 + F&O Universe ──────────────────────────────────────────────────
TICKERS = [
    # Large Caps / Nifty 50
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","BAJFINANCE.NS",
    "M&M.NS","ASIANPAINT.NS","TATASTEEL.NS","AXISBANK.NS","MARUTI.NS",
    "SUNPHARMA.NS","TITAN.NS","WIPRO.NS","KOTAKBANK.NS","ULTRACEMCO.NS",
    "ONGC.NS","NTPC.NS","POWERGRID.NS","COALINDIA.NS","BAJAJFINSV.NS",
    "HCLTECH.NS","JSWSTEEL.NS","HINDALCO.NS","GRASIM.NS","ADANIENT.NS",
    "ADANIPORTS.NS","DIVISLAB.NS","DRREDDY.NS","CIPLA.NS","APOLLOHOSP.NS",
    "HEROMOTOCO.NS","BAJAJ-AUTO.NS","EICHERMOT.NS","INDUSINDBK.NS","TECHM.NS",
    "BRITANNIA.NS","NESTLEIND.NS","HDFCLIFE.NS","SBILIFE.NS","TATACONSUM.NS",
    "BPCL.NS","HINDUNILVR.NS","SHREECEM.NS","LTIM.NS","TRENT.NS",
    # Nifty Next 50 / Midcap F&O
    "BHEL.NS","BEL.NS","HAL.NS","IRFC.NS","PFC.NS","RECLTD.NS","GAIL.NS",
    "SAIL.NS","NMDC.NS","AMBUJACEM.NS","PNB.NS","BANKBARODA.NS","CANBK.NS",
    "DLF.NS","GODREJCP.NS","DABUR.NS","COLPAL.NS","MARICO.NS","PIDILITIND.NS",
    "HAVELLS.NS","VOLTAS.NS","SIEMENS.NS","ABB.NS","CUMMINSIND.NS","ASHOKLEY.NS",
    "TVSMOTOR.NS","TATACOMM.NS","PERSISTENT.NS","COFORGE.NS","MPHASIS.NS",
    "SRF.NS","ASTRAL.NS","DIXON.NS","POLYCAB.NS","TATAPOWER.NS",
    "ATGL.NS","PETRONET.NS","INDHOTEL.NS","CHOLAFIN.NS","MUTHOOTFIN.NS",
    "PGHH.NS","BERGEPAINT.NS","KANSAINER.NS","AKZONOBEL.NS","SUPREMEIND.NS",
    "APLAPOLLO.NS","FINPIPE.NS","ABCAPITAL.NS","IDFCFIRSTB.NS","BANDHANBNK.NS",
    "FEDERALBNK.NS","RBLBANK.NS","KARURVYSYA.NS","DCBBANK.NS","UJJIVANSFB.NS",
    "AUBANK.NS","EQUITASBNK.NS","ESAFSFB.NS","CSBBANK.NS","SURYODAY.NS",
    "JIOFIN.NS","BAJAJHFL.NS","MANAPPURAM.NS","LICHSGFIN.NS","PNBHOUSING.NS",
    # Pharma / Healthcare
    "AUROPHARMA.NS","LUPIN.NS","ALKEM.NS","TORNTPHARM.NS","IPCALAB.NS",
    "GLAXO.NS","PFIZER.NS","ABBOTINDIA.NS","SANOFI.NS","NATCOPHARMA.NS",
    "LALPATHLAB.NS","METROPOLIS.NS","POLYMED.NS","FORTIS.NS","MAXHEALTH.NS",
    # IT / Tech
    "LTTS.NS","CYIENT.NS","KPITTECH.NS","TATAELXSI.NS","RATEGAIN.NS",
    "NAUKRI.NS","JUSTDIAL.NS","MAPMYINDIA.NS","TANLA.NS","INTELLECT.NS",
    # Auto & EV
    "EXIDEIND.NS","AMARAJABAT.NS","MOTHERSON.NS","BOSCHLTD.NS","BHARATFORG.NS",
    "SUNDRMFAST.NS","MINDAIND.NS","GABRIEL.NS","CRAFTSMAN.NS","PRICOL.NS",
    # Infrastructure / Capital Goods
    "CESC.NS","TORNTPOWER.NS","INOXWIND.NS","SUZLON.NS","THERMAX.NS",
    "KPIL.NS","NCC.NS","NBCC.NS","RVNL.NS","IRCON.NS","RITES.NS",
    "RAILVIKAS.NS","GRINFRA.NS","HG INFRA.NS","PNC INFRATECH.NS","PNCINFRATECH.NS",
    # Consumer / FMCG
    "VARUN.NS","RADICO.NS","UNITDSPR.NS","VBLLTD.NS","HINDWAREAP.NS",
    "JYOTHYLAB.NS","EMAMILTD.NS","BAJAJCONS.NS","HATSUN.NS","PARAS.NS",
    # Metals & Mining
    "HINDZINC.NS","NATIONALUM.NS","MOIL.NS","GMRINFRA.NS","AIAENG.NS",
    "RATNAMANI.NS","MAHSEAMLES.NS","APL.NS","MIDHANI.NS","WELSPUNIND.NS",
    # Real Estate / Cement
    "GODREJPROP.NS","PRESTIGE.NS","PHOENIX.NS","BRIGADE.NS","SOBHA.NS",
    "OBEROIRLTY.NS","KOLTEPATIL.NS","RAMCOCEM.NS","DALMIA.NS","HEIDELBERG.NS",
    # Chemicals / Specialty
    "DEEPAKNITR.NS","GNFC.NS","AAVAS.NS","CLEAN.NS","ALKYLAMINE.NS",
    "VINATIORGA.NS","NAVINFLUOR.NS","FLUOROCHEM.NS","PCBL.NS","HOCL.NS",
    # Telecom / Media
    "IDEA.NS","INDUSTOWER.NS","TTML.NS","HFCL.NS","TEJASNET.NS",
    # Logistics / Transport
    "BLUEDART.NS","GATI.NS","MAHLOG.NS","TCI.NS","MAHINDCIE.NS",
    # Retail / E-Commerce
    "DMART.NS","TATACOMM.NS","NYKAA.NS","PAYTM.NS","CARTRADE.NS",
    # Additional F&O
    "LODHA.NS","VEDL.NS","HDFCAMC.NS","NIPPONLIFE.NS","ICICIPRAMC.NS",
    "UTIAMC.NS","ABSLAMFI.NS","CHOLAHLDNG.NS","SHRIRAMFIN.NS","BAJAJFINSERV.NS",
]

# Deduplicate
TICKERS = list(dict.fromkeys(TICKERS))

def calculate_atr(df, period=14):
    hl = df['High'] - df['Low']
    hc = np.abs(df['High'] - df['Close'].shift())
    lc = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def calculate_dema(series, period):
    ema1 = series.ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    return 2 * ema1 - ema2

def analyze_stock(ticker):
    try:
        df = yf.download(ticker, period="1y", progress=False)
        if df.empty or len(df) < 200:
            return []
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)

        close, high, low, vol = df['Close'], df['High'], df['Low'], df['Volume']

        dma50  = close.rolling(50).mean()
        dma200 = close.rolling(200).mean()
        ema21  = close.ewm(span=21, adjust=False).mean()
        dema9  = calculate_dema(close, 9)
        atr    = calculate_atr(df, 14)
        vol20  = vol.rolling(20).mean()

        delta = close.diff()
        gain  = delta.where(delta > 0, 0).rolling(14).mean()
        loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi   = 100 - (100 / (1 + gain / loss))

        low20     = low.rolling(20).min()
        rsi_min20 = rsi.rolling(20).min()
        high50    = high.rolling(50).max()

        c   = float(close.iloc[-1])
        d50 = float(dma50.iloc[-1])
        d200= float(dma200.iloc[-1])
        atr_= float(atr.iloc[-1])
        rsi_= float(rsi.iloc[-1])
        v1  = float(vol.iloc[-1])
        v20 = float(vol20.iloc[-1])
        name = ticker.replace('.NS', '')

        if np.isnan(d200) or np.isnan(atr_) or atr_ == 0:
            return []

        setups = []

        def make_setup(strategy, confidence, entry, sl, target, target_type, reason):
            risk = (entry - sl) / entry * 100
            if risk <= 0: return None
            tgt_pct = float(target_type.split('%')[0].replace('Fixed ','').replace('Multibagger ','').replace('+','').strip())
            rr = round(tgt_pct / risk, 2)
            if rr < 0.8: return None
            return {
                'strategy': strategy, 'confidence': confidence, 'stock': name,
                'entry': round(entry, 2), 'sl': round(sl, 2), 'target': round(target, 2),
                'target_type': target_type, 'rr': rr, 'reason': reason
            }

        # ── 1. RSI Divergence + Vol Spike (MULTIBAGGER) ──────────────────
        cl   = float(low.iloc[-1])
        pl   = float(low20.iloc[-5])
        cr   = float(rsi.iloc[-1])
        pr   = float(rsi_min20.iloc[-5])
        if (cl < pl) and (cr > pr) and (cr < 50) and (v1 > 2.5 * v20) and c > d200:
            s = make_setup('RSI Divergence + Vol Spike', '77.8%',
                           c, c - 2.0 * atr_, c * 1.50, 'Multibagger 50%',
                           f'Price lower-low, RSI higher-low. Vol {round(v1/v20,1)}x avg!')
            if s: setups.append(s)

        # ── 2. DEMA Momentum Spike ────────────────────────────────────────
        if c > d50 > d200:
            vdry  = float(vol.iloc[-4:-1].mean()) < float(vol20.iloc[-2])
            vspike= v1 > 1.2 * v20
            dcross= float(dema9.iloc[-1]) > float(ema21.iloc[-1])
            if dcross and vdry and vspike:
                s = make_setup('DEMA Momentum Spike', '61.0%',
                               c, c - 1.5 * atr_, c * 1.03, 'Fixed 3%',
                               'DEMA > EMA21. Volume dried then spiked.')
                if s: setups.append(s)

        # ── 3. Pullback to Value ──────────────────────────────────────────
        if c > d200 and abs(c - d50) / d50 < 0.05 and rsi_ < 55:
            s = make_setup('Pullback to Value', '64.4%',
                           c, c - 2.0 * atr_, c * 1.03, 'Fixed 3%',
                           f'Near 50DMA. RSI: {round(rsi_, 1)}.')
            if s: setups.append(s)

        # ── 4. Darvas Breakout ────────────────────────────────────────────
        ph50 = float(high50.iloc[-2])
        if c > ph50 and v1 > 2.0 * v20 and c > d200:
            s = make_setup('Darvas Breakout', '44.6%',
                           c, c - 1.5 * atr_, c * 1.03, 'Fixed 3%',
                           'Breakout above 50-day high with 2x volume.')
            if s: setups.append(s)

        return setups
    except Exception:
        return []


class handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass   # suppress noisy logs

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        all_setups = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
            futures = {ex.submit(analyze_stock, t): t for t in TICKERS}
            for f in concurrent.futures.as_completed(futures):
                res = f.result()
                if res:
                    all_setups.extend(res)

        priority = {
            'RSI Divergence + Vol Spike': 0,
            'DEMA Momentum Spike':        1,
            'Pullback to Value':          2,
            'Darvas Breakout':            3,
        }
        all_setups.sort(key=lambda x: (priority.get(x['strategy'], 9), -x['rr']))

        self.wfile.write(json.dumps({"status": "success", "data": all_setups}).encode())
