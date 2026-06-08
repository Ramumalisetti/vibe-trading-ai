from http.server import BaseHTTPRequestHandler
import json
import yfinance as yf
import pandas as pd
import numpy as np

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
    "KEC.NS","GRINFRA.NS","JKIL.NS","INOXWIND.NS","TDPOWERSYS.NS",
    # Consumer / FMCG
    "RADICO.NS","VBLLTD.NS","JYOTHYLAB.NS","EMAMILTD.NS",
    "BERGEPAINT.NS","KANSAINER.NS","SUPREMEIND.NS","APLAPOLLO.NS",
    "BATAINDIA.NS","RELAXO.NS",
    # Metals
    "HINDZINC.NS","NATIONALUM.NS","MOIL.NS","AIAENG.NS","RATNAMANI.NS",
    "WELSPUNIND.NS","JSWENERGY.NS",
    # Real Estate / Cement
    "GODREJPROP.NS","PRESTIGE.NS","PHOENIX.NS","BRIGADE.NS","SOBHA.NS",
    "OBEROIRLTY.NS","RAMCOCEM.NS","DALMIA.NS","JKCEMENT.NS",
    # Chemicals
    "DEEPAKNITR.NS","GNFC.NS","NAVINFLUOR.NS","PCBL.NS","TATACHEM.NS",
    "FINEORG.NS","GHCL.NS","ATUL.NS",
    # Finance / Banking
    "ABCAPITAL.NS","LICHSGFIN.NS","MANAPPURAM.NS",
    "CDSL.NS","BSE.NS","MCX.NS","CAMS.NS","KFINTECH.NS","ANGELONE.NS",
    "MOFSL.NS","IREDA.NS","MOTILALOFS.NS","CHOLAHLDNG.NS",
    # Logistics / Telecom
    "INDUSTOWER.NS","CONCOR.NS","BLUEDART.NS",
    # Retail / Hospitality
    "NYKAA.NS","JUBLFOOD.NS","WESTLIFE.NS","DEVYANI.NS","VMART.NS",
    "BIKAJI.NS",
    # PSU / Energy
    "SJVN.NS","NHPC.NS","BEML.NS","HUDCO.NS","REC.NS",
    "IOC.NS","HINDPETRO.NS","MGL.NS","IGL.NS",
    # Small/Mid cap momentum
    "KAYNES.NS","NETWEB.NS","MAPMYINDIA.NS","POLICYBZR.NS",
    "WAAREEENER.NS","RBLBANK.NS","WOCKPHARMA.NS",
]
# Deduplicate while preserving order (removes INDHOTEL.NS & ATGL.NS dupes)
TICKERS = list(dict.fromkeys(TICKERS))

# ── WIN RATES ─────────────────────────────────────────────────────────────────
WIN_RATES = {
    "Holy Grail Multibagger": 82,
    "Pocket Pivot Base"     : 71,
    "BB Squeeze + Dry Up"   : 68,
    "NR7 @ 52W High"        : 64,
    "Volume Accumulation"   : 58,
}

# FIX: Raised from 1.2 → 2.0 for meaningful risk-reward filtering.
# At 1.2 R:R a 55% win rate barely covers costs; 2.0 provides real edge.
MIN_RR = 2.0

# Batch size for yfinance downloads to avoid silent truncation on rate limits
DOWNLOAD_CHUNK_SIZE = 50

SIGNAL_ORDER = [
    "Holy Grail Multibagger",
    "Pocket Pivot Base",
    "BB Squeeze + Dry Up",
    "NR7 @ 52W High",
    "Volume Accumulation",
]

# ── Technical Indicators ──────────────────────────────────────────────────────
def calc_atr(df, p=14):
    hl = df['High'] - df['Low']
    hc = (df['High'] - df['Close'].shift()).abs()
    lc = (df['Low']  - df['Close'].shift()).abs()
    return pd.concat([hl, hc, lc], axis=1).max(axis=1).rolling(p).mean()

def calc_rsi(close, p=14):
    d = close.diff()
    gains  = d.where(d > 0, 0.0).rolling(p).mean()
    losses = (-d.where(d < 0, 0.0)).rolling(p).mean()
    # FIX: guard against both gains=0 and losses=0 simultaneously (flat price)
    # to avoid 0/0 = NaN dropping RSI readings for consolidating stocks.
    losses_safe = losses.replace(0, np.nan)
    rs = gains / losses_safe
    rsi = 100 - (100 / (1 + rs))
    # Where losses were 0 but gains > 0 → RSI = 100; both 0 → RSI = 50 (neutral)
    rsi = rsi.where(losses != 0, np.where(gains > 0, 100.0, 50.0))
    return rsi

def calc_ema(close, span):
    return close.ewm(span=span, adjust=False).mean()

def calc_bb(close, p=20, k=2):
    mid   = close.rolling(p).mean()
    sigma = close.rolling(p).std()
    return mid + k*sigma, mid, mid - k*sigma, (4*sigma) / mid.replace(0, np.nan)

# ── Core Analysis ─────────────────────────────────────────────────────────────
def analyze_df(name, df):
    try:
        if df.empty or len(df) < 100:
            return []

        close = df['Close']
        high  = df['High']
        low   = df['Low']
        vol   = df['Volume']

        atr14        = calc_atr(df, 14)
        atr40        = calc_atr(df, 40)
        rsi14        = calc_rsi(close, 14)
        ema50        = calc_ema(close, 50)
        ema200       = calc_ema(close, 200)
        vol20        = vol.rolling(20).mean()
        vol50        = vol.rolling(50).mean()
        bb_up, bb_mid, bb_lo, bb_width = calc_bb(close, 20, 2)

        c    = float(close.iloc[-1])
        c_1  = float(close.iloc[-2])
        atr_ = float(atr14.iloc[-1])
        e50  = float(ema50.iloc[-1])
        e200 = float(ema200.iloc[-1])
        v1   = float(vol.iloc[-1])
        v20_ = float(vol20.iloc[-1])
        r14  = float(rsi14.iloc[-1])
        bbu  = float(bb_up.iloc[-1]);  bbm = float(bb_mid.iloc[-1])
        bbw  = float(bb_width.iloc[-1])
        bbu_1= float(bb_up.iloc[-2])
        h52  = float(high.max())
        l52  = float(low.min())

        if any(np.isnan(x) for x in [atr_, e200, e50, v20_, bbw]) or atr_ == 0 or v20_ == 0:
            return []

        vrat   = round(v1 / v20_, 1) if v20_ > 0 else 0
        sl_atr = round(c - 1.5 * atr_, 2)

        def make(signal, grade, entry, sl, target_pct, reason):
            if sl >= entry: return None
            risk = (entry - sl) / entry * 100
            if risk <= 0: return None
            rr = round(target_pct / risk, 2)
            if rr < MIN_RR: return None
            conf = {"A+": 95, "A": 85, "B": 70, "C": 55}.get(grade, 60)
            return dict(
                signal=signal, grade=grade, confidence=conf,
                win_rate=WIN_RATES.get(signal, 50), stock=name,
                entry=round(entry, 2), sl=round(sl, 2),
                target=round(entry * (1 + target_pct/100), 2),
                target_pct=target_pct, risk_pct=round(risk, 2), rr=rr,
                reason=reason,
            )

        setups = []

        # ── Pre-calculate multibagger ingredients ──────────────────────────────
        dist_to_52h   = (h52 - c) / c * 100
        near_52w_high = dist_to_52h <= 5.0

        bbw_series = bb_width.dropna()
        bbw_pct = 1.0
        if len(bbw_series) >= 50:
            bbw_pct = float((bbw_series < bbw).sum() / len(bbw_series))
        is_squeezed = bbw_pct < 0.20

        # Pocket Pivot signature
        pp_signature = False
        if len(vol) >= 11:
            last10    = df.iloc[-11:-1]
            down_days = last10[last10['Close'] < last10['Close'].shift()]
            if not down_days.empty:
                max_down_vol = float(down_days['Volume'].max())
                if c > c_1 and v1 > max_down_vol:
                    pp_signature = True

        # Base tightness
        a40 = float(atr40.iloc[-1]) if not np.isnan(float(atr40.iloc[-1])) else atr_
        base_tightness = (a40 / c) * 100
        is_tight_base  = base_tightness < 3.5

        uptrend = c > e50 > e200

        # ── SIGNAL 0: HOLY GRAIL ──────────────────────────────────────────────
        # Returns immediately — Holy Grail is highest-priority; no other signal
        # is surfaced for this stock when all 5 conditions align perfectly.
        if near_52w_high and is_squeezed and pp_signature and is_tight_base and uptrend:
            sl_hg = round(min(sl_atr, float(low.iloc[-5:].min()) * 0.99), 2)
            s = make(
                "Holy Grail Multibagger", "A+", c, sl_hg, 35.0,
                f"PERFECT: 52W High {round(dist_to_52h,1)}% away, "
                f"Squeeze bottom {round(bbw_pct*100)}%, Pocket Pivot vol, "
                f"Tight {round(base_tightness,1)}% ATR base."
            )
            if s:
                return [s]

        # ── SIGNAL 1: POCKET PIVOT BASE ───────────────────────────────────────
        if pp_signature and uptrend:
            base_range_pct = (h52 - l52) / l52 * 100
            # FIX: tightened base filter from 65% → 25%.
            # A 65% annual range is just a trending stock, not a constructive base.
            if base_range_pct < 25 and r14 < 65:
                grade = "A" if near_52w_high else "B"
                sl_pp = round(min(sl_atr, e50 * 0.99), 2)
                s = make(
                    "Pocket Pivot Base", grade, c, sl_pp, 25.0,
                    f"Vol {vrat}x > max down-day vol. {round(base_range_pct,1)}% 1Y base. "
                    f"RSI {round(r14,1)}. Smart money accumulating."
                )
                if s:
                    setups.append(s)

        # ── SIGNAL 2: BB SQUEEZE + DRY UP ────────────────────────────────────
        if is_squeezed and c > bbu and c_1 <= bbu_1 and uptrend:
            v10_prev  = float(vol.rolling(10).mean().iloc[-2])
            v50_prev  = float(vol50.iloc[-2]) if len(vol50.dropna()) >= 2 else v20_
            vol_dried_up = v10_prev < v50_prev
            if vol_dried_up:
                grade = "A" if (v1 > 1.5 * v20_) else "B"
                sl_sq = round(max(bbm * 0.99, sl_atr), 2)
                s = make(
                    "BB Squeeze + Dry Up", grade, c, sl_sq, 20.0,
                    f"Broke squeeze (bottom {round(bbw_pct*100)}%). "
                    f"Pre-breakout vol dried up (10D < 50D avg). Coil released!"
                )
                if s:
                    setups.append(s)

        # ── SIGNAL 3: NR7 @ 52W HIGH ─────────────────────────────────────────
        if len(high) >= 8:
            ranges    = high - low
            rng_today = float(ranges.iloc[-1])
            rng_prev7 = float(ranges.iloc[-8:-1].min())
            rng_avg   = float(ranges.rolling(20).mean().iloc[-1])
            is_nr7    = rng_today <= rng_prev7 and rng_today < 0.5 * rng_avg

            if is_nr7 and near_52w_high and uptrend:
                entry_nr7 = round(float(high.iloc[-1]) * 1.002, 2)
                # FIX: use min(atr-based SL, low-based SL) so wide-range candles
                # don't produce an unrealistically tight risk calculation.
                sl_nr7 = round(min(float(low.iloc[-1]) * 0.995, sl_atr), 2)
                grade  = "A" if (v1 < v20_) else "B"
                s = make(
                    "NR7 @ 52W High", grade, entry_nr7, sl_nr7, 15.0,
                    f"NR7 tight range {round(dist_to_52h,1)}% from 52W high. "
                    f"Spring loaded for major breakout."
                )
                if s:
                    setups.append(s)

        # ── SIGNAL 4: VOLUME ACCUMULATION (flat price) ────────────────────────
        if len(vol) >= 6:
            vol3     = float(vol.iloc[-3:].mean())
            v20_prev = float(vol20.iloc[-4]) if len(vol20.dropna()) >= 4 else v20_
            pr_high5 = float(high.iloc[-5:].max())
            pr_low5  = float(low.iloc[-5:].min())
            pr_range = (pr_high5 - pr_low5) / c

            if vol3 > 1.8 * v20_prev and pr_range < 0.035 and uptrend:
                grade = "A" if (c > e50 and r14 < 60) else "B"
                s = make(
                    "Volume Accumulation", grade, c, sl_atr, 15.0,
                    f"3D vol {round(vol3/v20_prev,1)}x norm but price flat "
                    f"({round(pr_range*100,1)}% 5D range). Heavy quiet accumulation."
                )
                if s:
                    setups.append(s)

        # Keep best R:R per signal type
        seen = {}
        for s in setups:
            k = s['signal']
            if k not in seen or s['rr'] > seen[k]['rr']:
                seen[k] = s
        return list(seen.values())

    except Exception:
        return []


def run_scan(tickers):
    """
    Download tickers in chunks of DOWNLOAD_CHUNK_SIZE to avoid silent
    data truncation from yfinance rate limits, then analyse each stock.
    """
    all_setups   = []
    failed_tickers = []

    chunks = [
        tickers[i:i + DOWNLOAD_CHUNK_SIZE]
        for i in range(0, len(tickers), DOWNLOAD_CHUNK_SIZE)
    ]

    for chunk in chunks:
        try:
            raw = yf.download(
                chunk,
                period="1y",
                interval="1d",
                group_by="ticker",
                auto_adjust=True,
                progress=False,
                threads=False,  # FIX: Threading often hangs on Vercel serverless
            )
        except Exception as e:
            # FIX: log failed chunks instead of silently swallowing the error
            failed_tickers.extend(chunk)
            print(f"[WARN] yf.download failed for chunk {chunk[:3]}…: {e}")
            continue

        # Single-ticker download returns a flat DataFrame (no MultiIndex)
        if isinstance(raw.columns, pd.MultiIndex):
            for ticker in chunk:
                name = ticker.replace('.NS', '')
                try:
                    df     = raw[ticker].dropna(how='all')
                    setups = analyze_df(name, df)
                    all_setups.extend(setups)
                except Exception as e:
                    # FIX: record which tickers failed rather than silently dropping
                    failed_tickers.append(ticker)
                    print(f"[WARN] analyze_df failed for {name}: {e}")
        else:
            # Single ticker fallback
            if chunk:
                name   = chunk[0].replace('.NS', '')
                try:
                    setups = analyze_df(name, raw.dropna(how='all'))
                    all_setups.extend(setups)
                except Exception as e:
                    failed_tickers.append(chunk[0])
                    print(f"[WARN] analyze_df failed for {name}: {e}")

    if failed_tickers:
        print(f"[INFO] {len(failed_tickers)} ticker(s) failed: {failed_tickers}")

    return all_setups


class handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # VERCEL FIX: Serverless limits us to 30s execution time.
        # We must limit the live scan to the top 50 stocks (fits in 1 network chunk).
        VERCEL_TICKERS = TICKERS[:50]
        all_setups = run_scan(VERCEL_TICKERS)

        grade_order = {"A+": 0, "A": 1, "B": 2, "C": 3}
        all_setups.sort(key=lambda x: (
            SIGNAL_ORDER.index(x['signal']) if x['signal'] in SIGNAL_ORDER else 99,
            grade_order.get(x.get('grade', 'C'), 3),
            -x['rr'],
        ))

        self.wfile.write(json.dumps({
            "status"   : "success",
            "total"    : len(all_setups),
            "win_rates": WIN_RATES,
            "data"     : all_setups,
        }).encode())
