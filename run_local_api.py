"""
Local API Server — Full Nifty 500 Universe (Bulk Download)
Run this before using the dashboard locally.
Dashboard: http://localhost:3000
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from api.scan import run_scan, TICKERS, SIGNAL_ORDER, WIN_RATES
from api.delivery_scan import run_delivery_scan
import json

FULL_TICKERS = list(dict.fromkeys(TICKERS))


class RouterHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        if self.path.startswith('/api/delivery_scan'):
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
            return

        # /api/scan — bulk download all 500 stocks
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        print(f"  Bulk-downloading {len(FULL_TICKERS)} stocks via yfinance...")
        all_setups = run_scan(FULL_TICKERS)

        grade_order = {"A+": 0, "A": 1, "B": 2, "C": 3}
        all_setups.sort(key=lambda x: (
            SIGNAL_ORDER.index(x['signal']) if x['signal'] in SIGNAL_ORDER else 99,
            grade_order.get(x.get('grade', 'C'), 3),
            -x['rr']
        ))

        payload = json.dumps({
            "status":    "success",
            "total":     len(all_setups),
            "win_rates": WIN_RATES,
            "data":      all_setups,
        }).encode()
        self.wfile.write(payload)
        print(f"  Scan complete: {len(all_setups)} setups found across {len(FULL_TICKERS)} stocks.")


if __name__ == "__main__":
    total = len(FULL_TICKERS)
    print("")
    print("==============================================")
    print("  Vibe Trading AI - Multibagger Scanner")
    print("==============================================")
    print(f"  Universe  : {total} Nifty 500 stocks")
    print(f"  Method    : Bulk download (single API call)")
    print(f"  Endpoints : /api/scan, /api/delivery_scan")
    print(f"  Dashboard : http://localhost:3000")
    print("==============================================")
    print("")
    server = HTTPServer(('localhost', 5000), RouterHandler)
    server.serve_forever()
