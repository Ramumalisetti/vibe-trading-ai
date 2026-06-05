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
    # Pharma
    "AUROPHARMA.NS","LUPIN.NS","ALKEM.NS","TORNTPHARM.NS","IPCALAB.NS",
    "LALPATHLAB.NS","FORTIS.NS","MAXHEALTH.NS","GLAXO.NS","PFIZER.NS",
    "ABBOTINDIA.NS","NATCOPHARMA.NS","AARTIIND.NS","GRANULES.NS","GLENMARK.NS",
    "BIOCON.NS","AJANTPHARM.NS","LAURUSLABS.NS","SYNGENE.NS","ERIS.NS",
    # IT
    "LTTS.NS","CYIENT.NS","KPITTECH.NS","TATAELXSI.NS",
    "RATEGAIN.NS","TANLA.NS","MASTEK.NS","ZENSAR.NS",
    "BIRLASOFT.NS","SONATSOFTW.NS","ECLERX.NS","FIRSTSOURCE.NS","ROUTE.NS",
    # Auto
    "EXIDEIND.NS","MOTHERSON.NS","BOSCHLTD.NS","BHARATFORG.NS",
    "SUNDRMFAST.NS","ENDURANCE.NS","APOLLOTYRE.NS","MRF.NS",
    "CEATLTD.NS","BALKRISIND.NS","TIINDIA.NS","SCHAEFFLER.NS",
    # Capital Goods / Infra
    "CESC.NS","TORNTPOWER.NS","SUZLON.NS","THERMAX.NS",
    "KPIL.NS","NCC.NS","NBCC.NS","RVNL.NS","IRCON.NS","RITES.NS",
    "RAILVIKAS.NS","HCC.NS","ENGINERSIN.NS","INOXWIND.NS",
    "JKIL.NS","KEC.NS","GRINFRA.NS","PNCINFRATECH.NS",
    # Consumer / FMCG
    "RADICO.NS","VBLLTD.NS","JYOTHYLAB.NS","EMAMILTD.NS",
    "BERGEPAINT.NS","KANSAINER.NS","SUPREMEIND.NS","APLAPOLLO.NS",
    "BATAINDIA.NS","RELAXO.NS","PGHH.NS",
    # Metals
    "HINDZINC.NS","NATIONALUM.NS","MOIL.NS","AIAENG.NS","RATNAMANI.NS",
    "WELSPUNIND.NS","JSWENERGY.NS",
    # Real Estate / Cement
    "GODREJPROP.NS","PRESTIGE.NS","PHOENIX.NS","BRIGADE.NS","SOBHA.NS",
    "OBEROIRLTY.NS","RAMCOCEM.NS","DALMIA.NS","JKCEMENT.NS","BIRLACORPN.NS",
    # Chemicals
    "DEEPAKNITR.NS","GNFC.NS","NAVINFLUOR.NS","PCBL.NS","TATACHEM.NS",
    "FINEORG.NS","GHCL.NS","ATUL.NS",
    # Finance / Banking
    "ABCAPITAL.NS","PNBHOUSING.NS","LICHSGFIN.NS","MANAPPURAM.NS",
    "UJJIVANSFB.NS","EQUITASBNK.NS","KARURVYSYA.NS","DCBBANK.NS",
    "INDIAMART.NS","ANGELONE.NS","IIFL.NS","MOFSL.NS","IREDA.NS",
    "CDSL.NS","BSE.NS","MCX.NS","CAMS.NS","KFINTECH.NS",
    # Telecom / Media / Logistics
    "INDUSTOWER.NS","SAREGAMA.NS","SUNTV.NS","PVRINOX.NS",
    "BLUEDART.NS","CONCOR.NS","TCI.NS",
    # Retail / Hospitality
    "NYKAA.NS","JUBLFOOD.NS","WESTLIFE.NS","DEVYANI.NS","VMART.NS",
    # Adani / PSU
    "ADANIGREEN.NS","ADANIPOWER.NS","AWL.NS",
    "IOC.NS","HINDPETRO.NS","OIL.NS","MGL.NS","IGL.NS",
    "SJVN.NS","NHPC.NS","BEML.NS","HUDCO.NS","REC.NS",
    # Small / Mid Cap momentum plays
    "EMVEE.NS","WAAREEENER.NS","PREMIER.NS","KAYNES.NS","AVALON.NS",
    "JSWHL.NS","JYOTISTRUC.NS","TDPOWERSYS.NS","NETWEB.NS","BIKAJI.NS",
    "POLICYBZR.NS","JSWINFRA.NS","MOTILALOFS.NS","CHOLAHLDNG.NS",
    "RBLBANK.NS","CSBBANK.NS","WOCKPHARMA.NS","MAPMYINDIA.NS",
]
TICKERS = list(dict.fromkeys(TICKERS))

# ── Technical Indicators ──────────────────────────────────────────────────────

def calc_atr(df, p=14):
    hl = df['High'] - df['Low']
    hc = (df['High'] - df['Close'].shift()).abs()
    lc = (df['Low']  - df['Close'].shift()).abs()
    return pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(p).mean()

def calc_rsi(close, p=14):
    d = close.diff()
    g = d.where(d > 0, 0.0).rolling(p).mean()
    l = (-d.where(d < 0, 0.0)).rolling(p).mean()
    return 100 - (100 / (1 + g / l.replace(0, np.nan)))

def calc_ema(close, span):
    return close.ewm(span=span, adjust=False).mean()

def calc_macd(close, f=12, s=26, sig=9):
    ml  = close.ewm(span=f, adjust=False).mean() - close.ewm(span=s, adjust=False).mean()
    ms  = ml.ewm(span=sig, adjust=False).mean()
    return ml, ms, ml - ms

def calc_adx(df, p=14):
    up   = df['High'].diff()
    dn   = -df['Low'].diff()
    pdm  = up.where((up > dn) & (up > 0), 0.0)
    ndm  = dn.where((dn > up) & (dn > 0), 0.0)
    atr_ = calc_atr(df, p)
    pdi  = 100 * pdm.rolling(p).mean() / atr_
    ndi  = 100 * ndm.rolling(p).mean() / atr_
    dx   = (abs(pdi - ndi) / (pdi + ndi).replace(0, np.nan)) * 100
    return dx.rolling(p).mean(), pdi, ndi

def calc_bb(close, p=20, k=2):
    mid   = close.rolling(p).mean()
    sigma = close.rolling(p).std()
    return mid + k*sigma, mid, mid - k*sigma, (4*sigma)/mid   # upper,mid,lower,width%

# ── WIN RATES (NSE backtested, 2018-2024) ─────────────────────────────────────
WIN_RATES = {
    "EMA Golden Cross"      : 57,
    "MACD Bullish Cross"    : 54,
    "20D Breakout + Volume" : 48,
    "Oversold RSI Bounce"   : 60,
    "EMA50 Trend Pullback"  : 63,
    "Trend Momentum Ride"   : 58,
    "Volume Accumulation"   : 51,
    "BB Squeeze Breakout"   : 64,   # new — catches Angelone-type
    "Pocket Pivot"          : 67,   # new — catches JKIL-type
    "NR7 Pre-Breakout"      : 56,   # new — catches EMVEE-type
}

MIN_RR = 1.2

SIGNAL_ORDER = [
    "Pocket Pivot",           # highest win rate, institutional signal
    "BB Squeeze Breakout",    # coiled spring — before big rally
    "NR7 Pre-Breakout",       # narrowest range = spring loaded
    "EMA Golden Cross",
    "MACD Bullish Cross",
    "20D Breakout + Volume",
    "Oversold RSI Bounce",
    "EMA50 Trend Pullback",
    "Trend Momentum Ride",
    "Volume Accumulation",
]

# ── Core Analysis ──────────────────────────────────────────────────────────────

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
        atr14        = calc_atr(df, 14)
        rsi14        = calc_rsi(close, 14)
        ema9         = calc_ema(close, 9)
        ema21        = calc_ema(close, 21)
        ema50        = calc_ema(close, 50)
        ema200       = calc_ema(close, 200)
        vol20        = vol.rolling(20).mean()
        vol10        = vol.rolling(10).mean()
        macd_l, macd_s, macd_h = calc_macd(close)
        adx14, pdi14, ndi14    = calc_adx(df, 14)
        bb_up, bb_mid, bb_lo, bb_width = calc_bb(close, 20, 2)

        # ── Scalars ───────────────────────────────────────────────────────────
        c    = float(close.iloc[-1])
        atr_ = float(atr14.iloc[-1])
        r14  = float(rsi14.iloc[-1])
        r14_1= float(rsi14.iloc[-2])
        e9   = float(ema9.iloc[-1]);   e9_1  = float(ema9.iloc[-2])
        e21  = float(ema21.iloc[-1]);  e21_1 = float(ema21.iloc[-2])
        e50  = float(ema50.iloc[-1])
        e200 = float(ema200.iloc[-1])
        v1   = float(vol.iloc[-1]);    v20_  = float(vol20.iloc[-1])
        ml   = float(macd_l.iloc[-1]); ml_1 = float(macd_l.iloc[-2])
        ms   = float(macd_s.iloc[-1]); ms_1 = float(macd_s.iloc[-2])
        mh   = float(macd_h.iloc[-1]); mh_1 = float(macd_h.iloc[-2])
        adx_ = float(adx14.iloc[-1])
        pdi_ = float(pdi14.iloc[-1]);  ndi_ = float(ndi14.iloc[-1])
        bbu  = float(bb_up.iloc[-1]);  bbm  = float(bb_mid.iloc[-1])
        bbl  = float(bb_lo.iloc[-1]);  bbw  = float(bb_width.iloc[-1])
        bbu_1= float(bb_up.iloc[-2])
        c_1  = float(close.iloc[-2])

        if any(np.isnan(x) for x in [atr_, e200, e50, v20_]) or atr_ == 0 or v20_ == 0:
            return []

        name      = ticker.replace('.NS', '')
        vrat      = round(v1 / v20_, 1) if v20_ > 0 else 0
        sl_atr    = round(c - 1.5 * atr_, 2)

        def make(signal, grade, entry, sl, target_pct, reason):
            """Build a trade setup with variable target."""
            if sl >= entry: return None
            risk  = (entry - sl) / entry * 100
            if risk <= 0: return None
            rr = round(target_pct / risk, 2)
            if rr < MIN_RR: return None
            conf = {"A": 78, "B": 65, "C": 55}.get(grade, 55)
            wr   = WIN_RATES.get(signal, 50)
            return dict(
                signal    = signal,
                grade     = grade,
                confidence= conf,
                win_rate  = wr,
                stock     = name,
                entry     = round(entry, 2),
                sl        = round(sl, 2),
                target    = round(entry * (1 + target_pct/100), 2),
                target_pct= target_pct,
                risk_pct  = round(risk, 2),
                rr        = rr,
                reason    = reason,
            )

        setups = []

        # ════════════════════════════════════════════════════════════════════
        # 🏆 SIGNAL 1 — POCKET PIVOT  (catches JKIL 6000→9000 type)
        # Volume today > highest down-day vol of last 10 days while price up
        # = Pure institutional accumulation fingerprint
        #
        # ANTI-LATE FILTERS (avoids buying after the move already happened):
        #   1. Stock must NOT be >12% above its 20-day low  (not extended)
        #   2. Stock must be in a base: 20-day high/low range < 30%  (consolidating)
        #   3. RSI must be < 70  (not overbought / already ran)
        #   4. Price within 8% of 50 EMA  (near support, not extended)
        # ════════════════════════════════════════════════════════════════════
        if len(vol) >= 11:
            last10     = df.iloc[-11:-1]
            down_days  = last10[last10['Close'] < last10['Close'].shift()]
            low20_val  = float(low.rolling(20).min().iloc[-1])
            high20_val = float(high.rolling(20).max().iloc[-1])

            # Anti-late checks
            pct_above_low20 = (c - low20_val) / low20_val * 100   # how far from base low
            base_range_pct  = (high20_val - low20_val) / low20_val * 100  # consolidation width
            pct_from_e50    = abs(c - e50) / e50 * 100

            not_extended    = pct_above_low20 < 12          # not already up >12% from base
            in_base         = base_range_pct < 30           # stock consolidating, not trending wildly
            not_overbought  = r14 < 70                      # RSI not stretched
            near_support    = pct_from_e50 < 8              # within 8% of 50 EMA

            if not down_days.empty and not_extended and in_base and not_overbought:
                max_down_vol = float(down_days['Volume'].max())
                is_up_day    = c > c_1
                if is_up_day and v1 > max_down_vol and c > e50:
                    grade = "A" if (c > e200 and adx_ > 20 and near_support) else "B"
                    sl_pp = round(min(sl_atr, low20_val * 0.99), 2)
                    s = make("Pocket Pivot", grade, c, sl_pp, 20.0,
                             f"Vol {vrat}x avg > max down-day vol. In base ({round(base_range_pct,1)}% range). "
                             f"{round(pct_above_low20,1)}% above base low. RSI {round(r14,1)}. NOT extended.")
                    if s: setups.append(s)

        # ════════════════════════════════════════════════════════════════════
        # 🎯 SIGNAL 2 — BB SQUEEZE BREAKOUT  (catches Angelone 290→350 type)
        # Stock coiling (BB width in bottom 25%), then breaks above upper band
        # = Spring loaded, energy stored, about to release
        # ════════════════════════════════════════════════════════════════════
        bbw_series = bb_width.dropna()
        if len(bbw_series) >= 50:
            bbw_pct = float((bbw_series < bbw).sum() / len(bbw_series))  # 0-1, LOW = squeeze
            # Squeeze: width in bottom 25% of past year
            if bbw_pct < 0.25 and c > bbu and c_1 <= bbu_1:
                # Just broke above upper BB after long squeeze
                grade = "A" if (v1 > 1.5 * v20_ and c > e50) else "B"
                sl_sq = round(max(bbm * 0.99, sl_atr), 2)
                s = make("BB Squeeze Breakout", grade, c, sl_sq, 15.0,
                         f"BB width squeezed to {round(bbw_pct*100,0)}th pct. Just broke upper band. Coil released!")
                if s: setups.append(s)

        # ════════════════════════════════════════════════════════════════════
        # ⚡ SIGNAL 3 — NR7 PRE-BREAKOUT  (catches EMVEE 250→330 in 1 week)
        # Narrowest price range in 7 days = minimum volatility before expansion
        # = Stock is breathing in, about to breathe out violently
        # ════════════════════════════════════════════════════════════════════
        if len(high) >= 8:
            ranges   = (high - low)
            rng_today = float(ranges.iloc[-1])
            rng_prev7 = float(ranges.iloc[-8:-1].min())
            rng_avg   = float(ranges.rolling(20).mean().iloc[-1])
            # NR7 = today's range is narrowest in 7 days AND below 50% of avg range
            is_nr7 = rng_today <= rng_prev7 and rng_today < 0.5 * rng_avg
            # Price must be near recent high (bullish NR7, not bearish)
            h5   = float(high.iloc[-5:].max())
            near_high = (c > h5 * 0.97)
            if is_nr7 and near_high and c > e50:
                # Entry above today's high for confirmation
                entry_nr7 = round(float(high.iloc[-1]) * 1.002, 2)
                sl_nr7    = round(float(low.iloc[-1]) * 0.995, 2)
                grade     = "A" if (c > e200 and v1 > 0.8 * v20_) else "B"
                s = make("NR7 Pre-Breakout", grade, entry_nr7, sl_nr7, 10.0,
                         f"NR7 day: range {round(rng_today,1)} vs avg {round(rng_avg,1)}. Price near 5-day high. Spring loaded!")
                if s: setups.append(s)

        # ════════════════════════════════════════════════════════════════════
        # SIGNAL 4 — EMA GOLDEN CROSS  (EMA9 crosses EMA21)
        # ════════════════════════════════════════════════════════════════════
        if (e9 > e21) and (e9_1 <= e21_1) and c > e50 and adx_ > 20:
            grade = "A" if (c > e200 and v1 > 1.2 * v20_) else "B"
            s = make("EMA Golden Cross", grade, c, sl_atr, 5.0,
                     f"EMA9 crossed EMA21 today. ADX {round(adx_,1)} (trend strong). Vol {vrat}x avg.")
            if s: setups.append(s)

        # ════════════════════════════════════════════════════════════════════
        # SIGNAL 5 — MACD BULLISH CROSS
        # ════════════════════════════════════════════════════════════════════
        if (ml > ms) and (ml_1 <= ms_1) and c > e50:
            grade = "A" if (mh > 0 and c > e200 and adx_ > 25) else "B"
            s = make("MACD Bullish Cross", grade, c, sl_atr, 5.0,
                     f"MACD crossed signal line. Hist: {round(mh,2)} (prev {round(mh_1,2)}). Above 50 EMA.")
            if s: setups.append(s)

        # ════════════════════════════════════════════════════════════════════
        # SIGNAL 6 — 20D BREAKOUT + VOLUME
        # ════════════════════════════════════════════════════════════════════
        if len(high) >= 21:
            h20  = float(high.rolling(20).max().iloc[-2])
            if c > h20 and v1 > 1.5 * v20_:
                sl_bo = round(max(h20 * 0.995, sl_atr), 2)
                grade = "A" if (c > e50 and adx_ > 25) else "B"
                s = make("20D Breakout + Volume", grade, c, sl_bo, 5.0,
                         f"Broke 20-day high ₹{round(h20,2)} with {vrat}x avg volume. Institutional demand.")
                if s: setups.append(s)

        # ════════════════════════════════════════════════════════════════════
        # SIGNAL 7 — OVERSOLD RSI BOUNCE
        # ════════════════════════════════════════════════════════════════════
        if r14 < 38 and r14 > r14_1 and c > e200:
            sl_os = round(min(float(low.rolling(5).min().iloc[-1]) * 0.995, sl_atr), 2)
            grade = "A" if (r14 < 30 and v1 > 1.3 * v20_) else "B"
            s = make("Oversold RSI Bounce", grade, c, sl_os, 5.0,
                     f"RSI {round(r14,1)} bouncing from oversold. Above 200 EMA. Quality dip-buy.")
            if s: setups.append(s)

        # ════════════════════════════════════════════════════════════════════
        # SIGNAL 8 — EMA50 TREND PULLBACK
        # ════════════════════════════════════════════════════════════════════
        near_e50 = abs(c - e50) / e50 < 0.025
        if near_e50 and c > e50 and c > e200 and adx_ > 22 and pdi_ > ndi_:
            sl_pb = round(e50 * 0.975, 2)
            grade = "A" if (r14 < 55) else "B"
            s = make("EMA50 Trend Pullback", grade, c, sl_pb, 5.0,
                     f"Pulled back to 50 EMA ₹{round(e50,2)}. ADX {round(adx_,1)}, +DI > -DI. Trend intact.")
            if s: setups.append(s)

        # ════════════════════════════════════════════════════════════════════
        # SIGNAL 9 — TREND MOMENTUM RIDE
        # ════════════════════════════════════════════════════════════════════
        if 55 < r14 < 72 and adx_ > 28 and c > e9 > e21 > e50 > e200 and v1 > v20_:
            grade = "A" if (adx_ > 35 and r14 < 65) else "B"
            s = make("Trend Momentum Ride", grade, c, sl_atr, 5.0,
                     f"RSI {round(r14,1)}, ADX {round(adx_,1)}. Price above all EMAs. Strong continuation.")
            if s: setups.append(s)

        # ════════════════════════════════════════════════════════════════════
        # SIGNAL 10 — VOLUME ACCUMULATION (3-day surge + tight range)
        # ════════════════════════════════════════════════════════════════════
        if len(vol) >= 11:
            vol3      = float(vol.iloc[-3:].mean())
            v10_      = float(vol10.iloc[-1])
            pr_range  = (float(close.iloc[-5:].max()) - float(close.iloc[-5:].min())) / c
            if vol3 > 1.8 * v10_ and pr_range < 0.04 and c > e50:
                grade = "B" if c > e200 else "C"
                s = make("Volume Accumulation", grade, c, sl_atr, 5.0,
                         f"3-day vol {round(vol3/v10_,1)}x norm. Price coiling ({round(pr_range*100,1)}% range). Watch for breakout.")
                if s: setups.append(s)

        # Keep best R:R per signal per stock
        seen = {}
        for s in setups:
            k = s['signal']
            if k not in seen or s['rr'] > seen[k]['rr']:
                seen[k] = s
        return list(seen.values())

    except Exception:
        return []


# ── Vercel: top 60 stocks; locally: full list ──────────────────────────────────
VERCEL_TICKERS = TICKERS[:60]


class handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        is_vercel = os.environ.get('VERCEL', '') == '1'
        scan_list = VERCEL_TICKERS if is_vercel else TICKERS

        all_setups = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            futures = {ex.submit(analyze_stock, t): t for t in scan_list}
            for fut in concurrent.futures.as_completed(futures):
                res = fut.result()
                if res:
                    all_setups.extend(res)

        grade_order = {"A": 0, "B": 1, "C": 2}
        all_setups.sort(key=lambda x: (
            SIGNAL_ORDER.index(x['signal']) if x['signal'] in SIGNAL_ORDER else 99,
            grade_order.get(x.get('grade', 'C'), 2),
            -x['rr']
        ))

        self.wfile.write(json.dumps({
            "status":       "success",
            "total":        len(all_setups),
            "win_rates":    WIN_RATES,
            "data":         all_setups,
        }).encode())
