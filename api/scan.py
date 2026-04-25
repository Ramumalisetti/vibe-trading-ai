from http.server import BaseHTTPRequestHandler
import json
import yfinance as yf
import pandas as pd
import numpy as np
import concurrent.futures

# ── Complete Nifty 500 + All F&O Universe (~400 unique stocks) ───────────────
TICKERS = [
    # ── Nifty 50 ───────────────────────────────────────────────────────────
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "SBIN.NS","BHARTIARTL.NS","ITC.NS","LT.NS","BAJFINANCE.NS",
    "M&M.NS","ASIANPAINT.NS","TATASTEEL.NS","AXISBANK.NS","MARUTI.NS",
    "SUNPHARMA.NS","TITAN.NS","WIPRO.NS","KOTAKBANK.NS","ULTRACEMCO.NS",
    "ONGC.NS","NTPC.NS","POWERGRID.NS","COALINDIA.NS","BAJAJFINSV.NS",
    "HCLTECH.NS","JSWSTEEL.NS","HINDALCO.NS","ADANIENT.NS","ADANIPORTS.NS",
    "DRREDDY.NS","CIPLA.NS","HEROMOTOCO.NS","BAJAJ-AUTO.NS","EICHERMOT.NS",
    "TECHM.NS","HDFCLIFE.NS","SBILIFE.NS","TRENT.NS","HAL.NS",
    "GRASIM.NS","DIVISLAB.NS","APOLLOHOSP.NS","INDUSINDBK.NS","BRITANNIA.NS",
    "NESTLEIND.NS","TATACONSUM.NS","BPCL.NS","HINDUNILVR.NS","SHREECEM.NS",
    # ── Nifty Next 50 / Large Midcap ───────────────────────────────────────
    "BHEL.NS","BEL.NS","IRFC.NS","PFC.NS","RECLTD.NS","GAIL.NS",
    "SAIL.NS","NMDC.NS","AMBUJACEM.NS","PNB.NS","BANKBARODA.NS","CANBK.NS",
    "DLF.NS","GODREJCP.NS","DABUR.NS","COLPAL.NS","MARICO.NS","PIDILITIND.NS",
    "HAVELLS.NS","VOLTAS.NS","SIEMENS.NS","ABB.NS","CUMMINSIND.NS","ASHOKLEY.NS",
    "TVSMOTOR.NS","TATACOMM.NS","PERSISTENT.NS","COFORGE.NS","MPHASIS.NS",
    "SRF.NS","ASTRAL.NS","DIXON.NS","POLYCAB.NS","TATAPOWER.NS",
    "ATGL.NS","PETRONET.NS","INDHOTEL.NS","CHOLAFIN.NS","MUTHOOTFIN.NS",
    "IDFCFIRSTB.NS","BANDHANBNK.NS","FEDERALBNK.NS","RBLBANK.NS","AUBANK.NS",
    "JIOFIN.NS","LODHA.NS","VEDL.NS","SHRIRAMFIN.NS","HDFCAMC.NS",
    "NIPPONLIFE.NS","ICICIPRAMC.NS","UTIAMC.NS","NAUKRI.NS","DMART.NS",
    # ── F&O Pharma / Healthcare ────────────────────────────────────────────
    "AUROPHARMA.NS","LUPIN.NS","ALKEM.NS","TORNTPHARM.NS","IPCALAB.NS",
    "LALPATHLAB.NS","METROPOLIS.NS","FORTIS.NS","MAXHEALTH.NS",
    "GLAXO.NS","PFIZER.NS","ABBOTINDIA.NS","SANOFI.NS","NATCOPHARMA.NS",
    "POLYMED.NS","AARTIIND.NS","GRANULES.NS","GLENMARK.NS",
    "BIOCON.NS","AJANTPHARM.NS","JBCHEPHARM.NS","ERIS.NS","LAURUSLABS.NS",
    "STRIDES.NS","SUVEN.NS","NEULANDLAB.NS","SYNGENE.NS",
    # ── F&O IT / Technology ────────────────────────────────────────────────
    "LTTS.NS","CYIENT.NS","KPITTECH.NS","TATAELXSI.NS",
    "RATEGAIN.NS","TANLA.NS","INTELLECT.NS","MASTEK.NS","ZENSAR.NS",
    "BIRLASOFT.NS","SONATSOFTW.NS","CMSINFO.NS","ECLERX.NS",
    "DATAMATICS.NS","FIRSTSOURCE.NS","MAPMYINDIA.NS","ROUTE.NS",
    # ── F&O Auto / EV ──────────────────────────────────────────────────────
    "EXIDEIND.NS","MOTHERSON.NS","BOSCHLTD.NS","BHARATFORG.NS",
    "SUNDRMFAST.NS","GABRIEL.NS","CRAFTSMAN.NS","PRICOL.NS",
    "ENDURANCE.NS","SUPRAJIT.NS","LUMAXTECH.NS",
    "TIINDIA.NS","SCHAEFFLER.NS","SKFINDIA.NS","TIMKEN.NS",
    "APOLLOTYRE.NS","MRF.NS","CEATLTD.NS","BALKRISIND.NS","JKTYRE.NS",
    # ── F&O Infrastructure / Capital Goods ────────────────────────────────
    "CESC.NS","TORNTPOWER.NS","INOXWIND.NS","SUZLON.NS","THERMAX.NS",
    "KPIL.NS","NCC.NS","NBCC.NS","RVNL.NS","IRCON.NS","RITES.NS",
    "RAILVIKAS.NS","GRINFRA.NS","PNCINFRATECH.NS","AHLUCONT.NS","KNRCON.NS",
    "HCC.NS","ENGINERSIN.NS",
    # ── F&O Consumer / FMCG ───────────────────────────────────────────────
    "RADICO.NS","VARUN.NS","VBLLTD.NS","UNITDSPR.NS",
    "JYOTHYLAB.NS","EMAMILTD.NS","BAJAJCONS.NS","HATSUN.NS",
    "PGHH.NS","BERGEPAINT.NS","KANSAINER.NS","AKZONOBEL.NS",
    "SUPREMEIND.NS","APLAPOLLO.NS","BATAINDIA.NS","RELAXO.NS",
    # ── F&O Metals & Mining ────────────────────────────────────────────────
    "HINDZINC.NS","NATIONALUM.NS","MOIL.NS","AIAENG.NS","RATNAMANI.NS",
    "MAHSEAMLES.NS","MIDHANI.NS","WELSPUNIND.NS","JSWENERGY.NS","TINPLATE.NS",
    # ── F&O Real Estate / Cement ──────────────────────────────────────────
    "GODREJPROP.NS","PRESTIGE.NS","PHOENIX.NS","BRIGADE.NS","SOBHA.NS",
    "OBEROIRLTY.NS","KOLTEPATIL.NS","MAHLIFE.NS","SUNTECK.NS",
    "RAMCOCEM.NS","DALMIA.NS","HEIDELBERG.NS","JKCEMENT.NS","STARCEMENT.NS",
    "ORIENTCEM.NS","BIRLACORPN.NS","JKPAPER.NS","TNPL.NS",
    # ── F&O Chemicals / Specialty ─────────────────────────────────────────
    "DEEPAKNITR.NS","GNFC.NS","ALKYLAMINE.NS","VINATIORGA.NS","NAVINFLUOR.NS",
    "FLUOROCHEM.NS","PCBL.NS","TATACHEM.NS",
    "BALAMINES.NS","FINEORG.NS","GALAXYSURF.NS","NOCIL.NS",
    "GHCL.NS","ATUL.NS","SUDARSCHEM.NS","HFCL.NS",
    # ── F&O Banking / Finance ─────────────────────────────────────────────
    "ABCAPITAL.NS","CHOLAHLDNG.NS","PNBHOUSING.NS","LICHSGFIN.NS",
    "MANAPPURAM.NS","BAJAJHFL.NS","UJJIVANSFB.NS","EQUITASBNK.NS",
    "ESAFSFB.NS","CSBBANK.NS","SURYODAY.NS","KARURVYSYA.NS","DCBBANK.NS",
    "INDIAMART.NS","ANGELONE.NS","IIFL.NS","MOFSL.NS","IREDA.NS",
    "CDSL.NS","BSE.NS","MCX.NS","CAMS.NS","KFINTECH.NS",
    # ── F&O Telecom / Media ───────────────────────────────────────────────
    "INDUSTOWER.NS","TTML.NS","TEJASNET.NS",
    "SAREGAMA.NS","SUNTV.NS","PVRINOX.NS","NETWORK18.NS","ZEEL.NS",
    # ── F&O Logistics / Transport ─────────────────────────────────────────
    "BLUEDART.NS","TCI.NS","CONCOR.NS","ALLCARGO.NS",
    # ── F&O Retail / Hospitality ──────────────────────────────────────────
    "NYKAA.NS","PAYTM.NS","JUBLFOOD.NS","WESTLIFE.NS",
    "DEVYANI.NS","SAPPHIRE.NS","VMART.NS","SHOPERSTOP.NS",
    # ── Adani Group ───────────────────────────────────────────────────────
    "ADANIGREEN.NS","ADANIPOWER.NS","ADANITRANS.NS","AWL.NS",
    # ── PSU / Government Enterprises ──────────────────────────────────────
    "IOC.NS","HINDPETRO.NS","MRPL.NS","CPCL.NS",
    "OIL.NS","MGL.NS","IGL.NS","GSPL.NS",
    "SJVN.NS","NHPC.NS","BEML.NS","HUDCO.NS","REC.NS",
    # ── Others ────────────────────────────────────────────────────────────
    "POLICYBZR.NS","SPARC.NS","WOCKPHARMA.NS","EDELWEISS.NS",
    "MOTILALOFS.NS","JSWINFRA.NS",
]
TICKERS = list(dict.fromkeys(TICKERS))  # remove any duplicates

def calculate_atr(df, period=14):
    hl = df['High'] - df['Low']
    hc = np.abs(df['High'] - df['Close'].shift())
    lc = np.abs(df['Low'] - df['Close'].shift())
    return pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(period).mean()

def calculate_dema(series, period):
    ema1 = series.ewm(span=period, adjust=False).mean()
    ema2 = ema1.ewm(span=period, adjust=False).mean()
    return 2 * ema1 - ema2

def analyze_stock(ticker):
    try:
        df = yf.download(ticker, period="1y", progress=False)
        if df.empty or len(df) < 200: return []
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)

        close, high, low, vol = df['Close'], df['High'], df['Low'], df['Volume']
        dma50  = close.rolling(50).mean()
        dma200 = close.rolling(200).mean()
        ema21  = close.ewm(span=21, adjust=False).mean()
        dema9  = calculate_dema(close, 9)
        atr    = calculate_atr(df)
        vol20  = vol.rolling(20).mean()
        delta  = close.diff()
        gain   = delta.where(delta > 0, 0).rolling(14).mean()
        loss   = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi    = 100 - (100 / (1 + gain / loss))
        low20     = low.rolling(20).min()
        rsi_min20 = rsi.rolling(20).min()
        high50    = high.rolling(50).max()

        c, d50, d200 = float(close.iloc[-1]), float(dma50.iloc[-1]), float(dma200.iloc[-1])
        atr_ = float(atr.iloc[-1])
        rsi_ = float(rsi.iloc[-1])
        v1, v20 = float(vol.iloc[-1]), float(vol20.iloc[-1])
        name = ticker.replace('.NS','')

        if np.isnan(d200) or np.isnan(atr_) or atr_ == 0 or v20 == 0: return []

        def make(strategy, confidence, entry, sl, target, ttype, reason):
            risk = (entry - sl) / entry * 100
            if risk <= 0: return None
            tpct = 50.0 if 'Multibagger' in ttype else 3.0
            rr = round(tpct / risk, 2)
            if rr < 0.8: return None
            return dict(strategy=strategy, confidence=confidence, stock=name,
                        entry=round(entry,2), sl=round(sl,2), target=round(target,2),
                        target_type=ttype, rr=rr, reason=reason)

        setups = []

        # 1. RSI Divergence + Vol Spike — MULTIBAGGER
        cl, pl = float(low.iloc[-1]), float(low20.iloc[-5])
        cr, pr = float(rsi.iloc[-1]), float(rsi_min20.iloc[-5])
        if cl < pl and cr > pr and cr < 50 and v1 > 2.5*v20 and c > d200:
            s = make('RSI Divergence + Vol Spike','77.8%', c, c-2.0*atr_, c*1.50,
                     'Multibagger 50%+', f'Lower low in price, higher low in RSI. Vol {round(v1/v20,1)}x avg!')
            if s: setups.append(s)

        # 2. DEMA Momentum Spike
        if c > d50 > d200:
            vdry  = float(vol.iloc[-4:-1].mean()) < float(vol20.iloc[-2])
            vspike= v1 > 1.2*v20
            if float(dema9.iloc[-1]) > float(ema21.iloc[-1]) and vdry and vspike:
                s = make('DEMA Momentum Spike','61.0%', c, c-1.5*atr_, c*1.03,
                         'Fixed 3%', 'DEMA > EMA21. Volume dried then spiked.')
                if s: setups.append(s)

        # 3. Pullback to Value
        if c > d200 and abs(c-d50)/d50 < 0.05 and rsi_ < 55:
            s = make('Pullback to Value','64.4%', c, c-2.0*atr_, c*1.03,
                     'Fixed 3%', f'Near 50DMA. RSI: {round(rsi_,1)}.')
            if s: setups.append(s)

        # 4. Darvas Breakout
        ph50 = float(high50.iloc[-2])
        if c > ph50 and v1 > 2.0*v20 and c > d200:
            s = make('Darvas Breakout','44.6%', c, c-1.5*atr_, c*1.03,
                     'Fixed 3%', 'Breakout above 50-day high with 2x volume.')
            if s: setups.append(s)

        return setups
    except Exception:
        return []


class handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        all_setups = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
            for res in concurrent.futures.as_completed(
                    {ex.submit(analyze_stock, t): t for t in TICKERS}):
                if res.result(): all_setups.extend(res.result())

        priority = {'RSI Divergence + Vol Spike':0,'DEMA Momentum Spike':1,
                    'Pullback to Value':2,'Darvas Breakout':3}
        all_setups.sort(key=lambda x: (priority.get(x['strategy'],9), -x['rr']))
        self.wfile.write(json.dumps({"status":"success","data":all_setups}).encode())
