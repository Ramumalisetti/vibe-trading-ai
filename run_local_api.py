"""
Local API Server — Full Nifty 500 Universe
Run this before using the dashboard locally.
Dashboard: http://localhost:3000
"""
from http.server import HTTPServer
from api.scan import handler, analyze_stock, TICKERS, SIGNAL_ORDER, WIN_RATES
import concurrent.futures, json

FULL_TICKERS = list(dict.fromkeys(TICKERS))


class FullHandler(handler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        all_setups = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
            futures = {ex.submit(analyze_stock, t): t for t in FULL_TICKERS}
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

        payload = json.dumps({
            "status":    "success",
            "total":     len(all_setups),
            "win_rates": WIN_RATES,
            "data":      all_setups,
        }).encode()
        self.wfile.write(payload)
        print(f"✅ Scan complete — {len(all_setups)} setups across {len(FULL_TICKERS)} stocks.")


if __name__ == "__main__":
    total = len(FULL_TICKERS)
    print("")
    print("══════════════════════════════════════════════")
    print("    Vibe Trading AI — Pre-Rally AI Scanner")
    print("══════════════════════════════════════════════")
    print(f"  Universe  : {total} Nifty 500 stocks")
    print(f"  Signals   : 10 (inc. Pocket Pivot, BB Squeeze, NR7)")
    print(f"  Stop Loss : 1.5× ATR (dynamic)")
    print(f"  Min R:R   : 1.2×")
    print(f"  Dashboard : http://localhost:3000")
    print("══════════════════════════════════════════════")
    print("")
    server = HTTPServer(('localhost', 5000), FullHandler)
    server.serve_forever()
