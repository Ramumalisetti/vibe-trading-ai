"""
Local API Server — Full Nifty 500 + F&O Universe (200 stocks)
Run this on your computer every morning before market hours.
Access the scanner at: http://localhost:3000
"""
from http.server import HTTPServer
from api.scan import handler, analyze_stock, TICKERS
import concurrent.futures, json

# ── Extend the ticker list for local full-universe scan ──────────────────────
FULL_TICKERS = TICKERS + [
    # Nifty Next 50 / Midcap F&O
    "BHEL.NS","BEL.NS","IRFC.NS","PFC.NS","RECLTD.NS","GAIL.NS",
    "SAIL.NS","NMDC.NS","AMBUJACEM.NS","PNB.NS","BANKBARODA.NS","CANBK.NS",
    "DLF.NS","GODREJCP.NS","DABUR.NS","COLPAL.NS","MARICO.NS","PIDILITIND.NS",
    "HAVELLS.NS","VOLTAS.NS","SIEMENS.NS","ABB.NS","CUMMINSIND.NS","ASHOKLEY.NS",
    "TVSMOTOR.NS","TATACOMM.NS","PERSISTENT.NS","COFORGE.NS","MPHASIS.NS",
    "SRF.NS","ASTRAL.NS","DIXON.NS","POLYCAB.NS","TATAPOWER.NS",
    "ATGL.NS","PETRONET.NS","INDHOTEL.NS","CHOLAFIN.NS","MUTHOOTFIN.NS",
    "IDFCFIRSTB.NS","BANDHANBNK.NS","FEDERALBNK.NS","RBLBANK.NS","AUBANK.NS",
    # Pharma
    "AUROPHARMA.NS","LUPIN.NS","ALKEM.NS","TORNTPHARM.NS","IPCALAB.NS",
    "LALPATHLAB.NS","METROPOLIS.NS","FORTIS.NS","MAXHEALTH.NS",
    # IT
    "LTTS.NS","CYIENT.NS","KPITTECH.NS","TATAELXSI.NS","NAUKRI.NS",
    # Auto
    "EXIDEIND.NS","MOTHERSON.NS","BOSCHLTD.NS","BHARATFORG.NS",
    # Infra / Capital Goods
    "CESC.NS","THERMAX.NS","NCC.NS","NBCC.NS","RVNL.NS","IRCON.NS",
    # Metals
    "HINDZINC.NS","NATIONALUM.NS","MOIL.NS","AIAENG.NS","RATNAMANI.NS",
    # Real Estate
    "GODREJPROP.NS","PRESTIGE.NS","PHOENIX.NS","BRIGADE.NS","SOBHA.NS",
    # Chemicals
    "DEEPAKNITR.NS","GNFC.NS","ALKYLAMINE.NS","VINATIORGA.NS","NAVINFLUOR.NS",
    # Others
    "VEDL.NS","HDFCAMC.NS","NIPPONLIFE.NS","SHRIRAMFIN.NS","LODHA.NS","JIOFIN.NS",
]
FULL_TICKERS = list(dict.fromkeys(FULL_TICKERS))  # deduplicate


class FullHandler(handler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        all_setups = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
            for res in concurrent.futures.as_completed(
                    {ex.submit(analyze_stock, t): t for t in FULL_TICKERS}):
                if res.result(): all_setups.extend(res.result())

        priority = {'RSI Divergence + Vol Spike':0,'DEMA Momentum Spike':1,
                    'Pullback to Value':2,'Darvas Breakout':3}
        all_setups.sort(key=lambda x: (priority.get(x['strategy'],9), -x['rr']))

        payload = json.dumps({"status":"success","data":all_setups}).encode()
        self.wfile.write(payload)
        print(f"✅ Scan complete. {len(all_setups)} setups found across {len(FULL_TICKERS)} stocks.")


if __name__ == "__main__":
    print(f"🚀 Vibe Trading AI — Full Universe Server")
    print(f"📊 Scanning {len(FULL_TICKERS)} stocks (Nifty 500 + F&O)")
    print(f"🌐 Open your browser at: http://localhost:3000")
    print(f"⏳ First scan will take 30-60 seconds...\n")
    server = HTTPServer(('localhost', 5000), FullHandler)
    server.serve_forever()
