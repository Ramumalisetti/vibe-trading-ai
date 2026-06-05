from http.server import BaseHTTPRequestHandler
import json, os
import yfinance as yf
import pandas as pd
import numpy as np
import concurrent.futures

# ── Nifty 500 Universe ────────────────────────────────────────────────────────
TICKERS = [
    # Nifty 50
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
    # Nifty Next 50 / Large Midcap
    "BHEL.NS","BEL.NS","IRFC.NS","PFC.NS","RECLTD.NS","GAIL.NS",
    "SAIL.NS","NMDC.NS","AMBUJACEM.NS","PNB.NS","BANKBARODA.NS","CANBK.NS",
    "DLF.NS","GODREJCP.NS","DABUR.NS","COLPAL.NS","MARICO.NS","PIDILITIND.NS",
    "HAVELLS.NS","VOLTAS.NS","SIEMENS.NS","ABB.NS","CUMMINSIND.NS","ASHOKLEY.NS",
    "TVSMOTOR.NS","TATACOMM.NS","PERSISTENT.NS","COFORGE.NS","MPHASIS.NS",
    "SRF.NS","ASTRAL.NS","DIXON.NS","POLYCAB.NS","TATAPOWER.NS",
    "ATGL.NS","PETRONET.NS","INDHOTEL.NS","CHOLAFIN.NS","MUTHOOTFIN.NS",
    "IDFCFIRSTB.NS","BANDHANBNK.NS","FEDERALBNK.NS","AUBANK.NS",
    "JIOFIN.NS","LODHA.NS","VEDL.NS","SHRIRAMFIN.NS","HDFCAMC.NS",
    "NIPPONLIFE.NS","ICICIPRAMC.NS","UTIAMC.NS","NAUKRI.NS","DMART.NS",
    # Pharma / Healthcare
    "AUROPHARMA.NS","LUPIN.NS","ALKEM.NS","TORNTPHARM.NS","IPCALAB.NS",
    "LALPATHLAB.NS","FORTIS.NS","MAXHEALTH.NS","GLAXO.NS","PFIZER.NS",
    "ABBOTINDIA.NS","NATCOPHARMA.NS","AARTIIND.NS","GRANULES.NS","GLENMARK.NS",
    "BIOCON.NS","AJANTPHARM.NS","LAURUSLABS.NS","SYNGENE.NS","ERIS.NS",
    # IT / Technology
    "LTTS.NS","CYIENT.NS","KPITTECH.NS","TATAELXSI.NS",
    "RATEGAIN.NS","TANLA.NS","MASTEK.NS","ZENSAR.NS",
    "BIRLASOFT.NS","SONATSOFTW.NS","ECLERX.NS","FIRSTSOURCE.NS",
    "PERSISTENT.NS","COFORGE.NS","ROUTE.NS","MAPMYINDIA.NS",
    # Auto / EV
    "EXIDEIND.NS","MOTHERSON.NS","BOSCHLTD.NS","BHARATFORG.NS",
    "SUNDRMFAST.NS","ENDURANCE.NS","APOLLOTYRE.NS","MRF.NS",
    "CEATLTD.NS","BALKRISIND.NS","TIINDIA.NS","SCHAEFFLER.NS",
    # Capital Goods / Infra
    "CESC.NS","TORNTPOWER.NS","SUZLON.NS","THERMAX.NS",
    "KPIL.NS","NCC.NS","NBCC.NS","RVNL.NS","IRCON.NS","RITES.NS",
    "RAILVIKAS.NS","HCC.NS","ENGINERSIN.NS","INOXWIND.NS",
    # Consumer / FMCG
    "RADICO.NS","VBLLTD.NS","JYOTHYLAB.NS","EMAMILTD.NS",
    "BERGEPAINT.NS","KANSAINER.NS","SUPREMEIND.NS","APLAPOLLO.NS",
    "BATAINDIA.NS","RELAXO.NS","PGHH.NS",
    # Metals & Mining
    "HINDZINC.NS","NATIONALUM.NS","MOIL.NS","AIAENG.NS","RATNAMANI.NS",
    "WELSPUNIND.NS","JSWENERGY.NS",
    # Real Estate / Cement
    "GODREJPROP.NS","PRESTIGE.NS","PHOENIX.NS","BRIGADE.NS","SOBHA.NS",
    "OBEROIRLTY.NS","RAMCOCEM.NS","DALMIA.NS","JKCEMENT.NS",
    "BIRLACORPN.NS","JKPAPER.NS",
    # Chemicals / Specialty
    "DEEPAKNITR.NS","GNFC.NS","NAVINFLUOR.NS","PCBL.NS","TATACHEM.NS",
    "FINEORG.NS","GHCL.NS","ATUL.NS","PIDILITIND.NS",
    # Banking / Finance
    "ABCAPITAL.NS","PNBHOUSING.NS","LICHSGFIN.NS","MANAPPURAM.NS",
    "UJJIVANSFB.NS","EQUITASBNK.NS","KARURVYSYA.NS","DCBBANK.NS",
    "INDIAMART.NS","ANGELONE.NS","IIFL.NS","MOFSL.NS","IREDA.NS",
    "CDSL.NS","BSE.NS","MCX.NS","CAMS.NS","KFINTECH.NS",
    # Telecom / Logistics
    "INDUSTOWER.NS","SAREGAMA.NS","SUNTV.NS","PVRINOX.NS",
    "BLUEDART.NS","CONCOR.NS","TCI.NS","ALLCARGO.NS",
    # Retail / Hospitality
    "NYKAA.NS","JUBLFOOD.NS","WESTLIFE.NS","DEVYANI.NS","VMART.NS",
    # Adani Group
    "ADANIGREEN.NS","ADANIPOWER.NS","AWL.NS",
    # PSU / Govt
    "IOC.NS","HINDPETRO.NS","OIL.NS","MGL.NS","IGL.NS",
    "SJVN.NS","NHPC.NS","BEML.NS","HUDCO.NS","REC.NS",
    # Others
    "POLICYBZR.NS","JSWINFRA.NS","MOTILALOFS.NS","CHOLAHLDNG.NS",
    "RBLBANK.NS","CSBBANK.NS","IPCALAB.NS","WOCKPHARMA.NS",
]
TICKERS = list(dict.fromkeys(TICKERS))  # deduplicate

# ── Technical Helpers ──────────────────────────────────────────────────────────

def atr(df, period=14):
    hl  = df['High'] - df['Low']
    hc  = (df['High'] - df['Close'].shift()).abs()
    lc  = (df['Low']  - df['Close'].shift()).abs()
    tr  = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def rsi(close, period=14):
    d = close.diff()
    gain = d.where(d > 0, 0.0).rolling(period).mean()
    loss = (-d.where(d < 0, 0.0)).rolling(period).mean()
    rs   = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def macd(close, fast=12, slow=26, signal=9):
    ema_fast   = close.ewm(span=fast,   adjust=False).mean()
    ema_slow   = close.ewm(span=slow,   adjust=False).mean()
    macd_line  = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist        = macd_line - signal_line
    return macd_line, signal_line, hist

def adx(df, period=14):
    up   = df['High'].diff()
    down = -df['Low'].diff()
    pdm  = up.where((up > down) & (up > 0), 0.0)
    ndm  = down.where((down > up) & (down > 0), 0.0)
    atr_ = atr(df, period)
    pdi  = 100 * pdm.rolling(period).mean() / atr_
    ndi  = 100 * ndm.rolling(period).mean() / atr_
    dx   = (abs(pdi - ndi) / (pdi + ndi).replace(0, np.nan)) * 100
    return dx.rolling(period).mean(), pdi, ndi

def ema(close, span):
    return close.ewm(span=span, adjust=False).mean()

# ── Core Analyzer ──────────────────────────────────────────────────────────────
TARGET_PCT = 0.05     # 5% target (fixed)
MIN_RR     = 1.2      # minimum reward/risk ratio to show

def analyze_stock(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 60:
            return []
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)

        close = df['Close']
        high  = df['High']
        low   = df['Low']
        vol   = df['Volume']

        # ── Indicators ────────────────────────────────────────────────────────
        atr14    = atr(df, 14)
        rsi14    = rsi(close, 14)
        rsi5     = rsi(close, 5)
        ema9     = ema(close, 9)
        ema21    = ema(close, 21)
        ema50    = ema(close, 50)
        ema200   = ema(close, 200)
        vol20    = vol.rolling(20).mean()
        macd_l, macd_s, macd_h = macd(close)
        adx14, pdi14, ndi14    = adx(df, 14)

        # Current values
        c    = float(close.iloc[-1])
        h1   = float(high.iloc[-1])
        l1   = float(low.iloc[-1])
        atr_ = float(atr14.iloc[-1])
        r14  = float(rsi14.iloc[-1])
        r5   = float(rsi5.iloc[-1])
        e9   = float(ema9.iloc[-1])
        e21  = float(ema21.iloc[-1])
        e50  = float(ema50.iloc[-1])
        e200 = float(ema200.iloc[-1])
        v1   = float(vol.iloc[-1])
        v20  = float(vol20.iloc[-1])
        ml   = float(macd_l.iloc[-1])
        ms   = float(macd_s.iloc[-1])
        mh   = float(macd_h.iloc[-1])
        mh_1 = float(macd_h.iloc[-2])
        adx_ = float(adx14.iloc[-1])
        pdi_ = float(pdi14.iloc[-1])
        ndi_ = float(ndi14.iloc[-1])

        # Previous values for crossover detection
        e9_1  = float(ema9.iloc[-2])
        e21_1 = float(ema21.iloc[-2])
        ml_1  = float(macd_l.iloc[-2])
        ms_1  = float(macd_s.iloc[-2])

        if any(np.isnan(x) for x in [atr_, e200, e50, v20]) or atr_ == 0 or v20 == 0:
            return []

        name       = ticker.replace('.NS', '')
        vol_ratio  = round(v1 / v20, 1) if v20 > 0 else 0
        sl_atr     = round(c - 1.5 * atr_, 2)   # default ATR stop loss (long)
        target_5   = round(c * 1.05, 2)           # fixed 5% target

        def make_setup(signal, grade, entry, sl, reason):
            """Build a setup dict. Grade A/B/C determines confidence score."""
            if sl >= entry:   return None
            risk_pct   = (entry - sl) / entry * 100
            reward_pct = TARGET_PCT * 100
            if risk_pct <= 0: return None
            rr = round(reward_pct / risk_pct, 2)
            if rr < MIN_RR: return None
            conf = {"A": 78, "B": 65, "C": 55}.get(grade, 55)
            return dict(
                signal    = signal,
                grade     = grade,
                confidence= conf,
                stock     = name,
                entry     = round(entry, 2),
                sl        = round(sl, 2),
                target    = round(entry * (1 + TARGET_PCT), 2),
                risk_pct  = round(risk_pct, 2),
                rr        = rr,
                reason    = reason,
            )

        setups = []

        # ═══════════════════════════════════════════════════════════════════════
        # SIGNAL 1 ── EMA Golden Cross  (9 crosses above 21 today)
        #   Best for: fresh momentum entry with trend confirmation
        # ═══════════════════════════════════════════════════════════════════════
        cross_today = (e9 > e21) and (e9_1 <= e21_1)
        if cross_today and c > e50 and adx_ > 20:
            grade  = "A" if (c > e200 and v1 > 1.2 * v20) else "B"
            s = make_setup(
                "EMA Golden Cross",
                grade, c, sl_atr,
                f"EMA9 crossed EMA21 today. ADX {round(adx_,1)} (trend strong). Vol {vol_ratio}x avg."
            )
            if s: setups.append(s)

        # ═══════════════════════════════════════════════════════════════════════
        # SIGNAL 2 ── MACD Bullish Cross  (MACD crosses signal line)
        #   Best for: momentum confirmation in trending stocks
        # ═══════════════════════════════════════════════════════════════════════
        macd_cross = (ml > ms) and (ml_1 <= ms_1)
        if macd_cross and c > e50:
            grade = "A" if (mh > 0 and c > e200 and adx_ > 25) else "B"
            s = make_setup(
                "MACD Bullish Cross",
                grade, c, sl_atr,
                f"MACD crossed signal line. Hist: {round(mh,2)} (prev {round(mh_1,2)}). Above 50 EMA."
            )
            if s: setups.append(s)

        # ═══════════════════════════════════════════════════════════════════════
        # SIGNAL 3 ── Oversold RSI Reversal  (RSI<35 bouncing up + above 200EMA)
        #   Best for: value entry on high-quality stocks dipping
        # ═══════════════════════════════════════════════════════════════════════
        r14_1 = float(rsi14.iloc[-2])
        if r14 < 38 and r14 > r14_1 and c > e200:
            # Tighter stop for oversold bounce
            sl_os  = round(low.rolling(5).min().iloc[-1] * 0.995, 2)
            grade  = "A" if (r14 < 30 and v1 > 1.3 * v20) else "B"
            s = make_setup(
                "Oversold RSI Bounce",
                grade, c, min(sl_os, sl_atr),
                f"RSI {round(r14,1)} bouncing from oversold. Above 200 EMA. Quality dip-buy."
            )
            if s: setups.append(s)

        # ═══════════════════════════════════════════════════════════════════════
        # SIGNAL 4 ── 20-Day Breakout + Volume Surge
        #   Best for: momentum breakouts with institutional participation
        # ═══════════════════════════════════════════════════════════════════════
        h20 = float(high.rolling(20).max().iloc[-2])  # prior 20-day high (not today)
        if c > h20 and v1 > 1.5 * v20:
            sl_bo  = round(h20 * 0.995, 2)  # just below the breakout level
            grade  = "A" if (c > e50 and adx_ > 25) else "B"
            s = make_setup(
                "20D Breakout + Volume",
                grade, c, max(sl_bo, sl_atr),
                f"Broke 20-day high ₹{round(h20,2)} with {vol_ratio}x avg volume. Institutional demand."
            )
            if s: setups.append(s)

        # ═══════════════════════════════════════════════════════════════════════
        # SIGNAL 5 ── EMA50 Pullback in Uptrend  (c near EMA50, ADX strong)
        #   Best for: buying the dip in a healthy uptrend
        # ═══════════════════════════════════════════════════════════════════════
        near_e50 = abs(c - e50) / e50 < 0.025   # within 2.5% of 50EMA
        if near_e50 and c > e50 and c > e200 and adx_ > 22 and pdi_ > ndi_:
            sl_pb  = round(e50 * 0.975, 2)
            grade  = "A" if (r14 < 55 and v1 > 0.8 * v20) else "B"
            s = make_setup(
                "EMA50 Trend Pullback",
                grade, c, sl_pb,
                f"Pulled back to 50 EMA (₹{round(e50,2)}). ADX {round(adx_,1)}, +DI > -DI. Trend intact."
            )
            if s: setups.append(s)

        # ═══════════════════════════════════════════════════════════════════════
        # SIGNAL 6 ── RSI Momentum + ADX Trend (RSI 55-70, ADX>28, above all EMAs)
        #   Best for: riding strong momentum stocks mid-trend
        # ═══════════════════════════════════════════════════════════════════════
        if 55 < r14 < 72 and adx_ > 28 and c > e9 > e21 > e50 > e200 and v1 > v20:
            grade = "A" if (adx_ > 35 and r14 < 65) else "B"
            s = make_setup(
                "Trend Momentum Ride",
                grade, c, sl_atr,
                f"RSI {round(r14,1)}, ADX {round(adx_,1)}. Price above all EMAs. Strong trend continuation."
            )
            if s: setups.append(s)

        # ═══════════════════════════════════════════════════════════════════════
        # SIGNAL 7 ── Volume Accumulation (3-day vol surge, price consolidating)
        #   Best for: catching institutional accumulation before move
        # ═══════════════════════════════════════════════════════════════════════
        vol3 = float(vol.iloc[-3:].mean())
        vol10 = float(vol.rolling(10).mean().iloc[-1])
        price_range = (float(close.iloc[-5:].max()) - float(close.iloc[-5:].min())) / c
        if vol3 > 1.8 * vol10 and price_range < 0.04 and c > e50:
            grade = "B" if c > e200 else "C"
            s = make_setup(
                "Volume Accumulation",
                grade, c, sl_atr,
                f"3-day avg vol {round(vol3/vol10,1)}x norm. Price consolidating ({round(price_range*100,1)}% range). Breakout imminent."
            )
            if s: setups.append(s)

        # Deduplicate: keep best R:R if same stock from multiple signals
        seen = {}
        for s in setups:
            key = s['signal']
            if key not in seen or s['rr'] > seen[key]['rr']:
                seen[key] = s
        return list(seen.values())

    except Exception:
        return []


# ── Vercel top-60 vs full list locally ────────────────────────────────────────
VERCEL_TICKERS = TICKERS[:60]

SIGNAL_ORDER = [
    "EMA Golden Cross",
    "MACD Bullish Cross",
    "20D Breakout + Volume",
    "Oversold RSI Bounce",
    "EMA50 Trend Pullback",
    "Trend Momentum Ride",
    "Volume Accumulation",
]


class handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        is_vercel  = os.environ.get('VERCEL', '') == '1'
        scan_list  = VERCEL_TICKERS if is_vercel else TICKERS

        all_setups = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            futures = {ex.submit(analyze_stock, t): t for t in scan_list}
            for fut in concurrent.futures.as_completed(futures):
                res = fut.result()
                if res:
                    all_setups.extend(res)

        # Sort: by signal priority, then grade A>B>C, then best R:R
        grade_order = {"A": 0, "B": 1, "C": 2}
        all_setups.sort(key=lambda x: (
            SIGNAL_ORDER.index(x['signal']) if x['signal'] in SIGNAL_ORDER else 99,
            grade_order.get(x.get('grade', 'C'), 2),
            -x['rr']
        ))

        self.wfile.write(json.dumps({
            "status":  "success",
            "total":   len(all_setups),
            "target":  "5%",
            "data":    all_setups,
        }).encode())
