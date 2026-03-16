"""
FII & DII Live Data Server  —  by Mr. Chartist
================================================
Local proxy that handles NSE's strict session/cookie requirements.

Usage:
  python server.py           — starts server on http://localhost:5000
  python server.py --fetch   — just prints today's data and exits (debug)

NSE publishes FII/DII data once daily after market close (~5:30 PM IST).
This server fetches once, caches all day, and auto-refreshes after 5:30 PM IST.
"""

import json, time, threading, sys, gzip, io, re
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler

try:
    import requests
    print("[OK] Using requests library (best session handling)")
    HAS_REQUESTS = True
except ImportError:
    import urllib.request as _urllib
    HAS_REQUESTS = False
    print("[WARN] requests not found, using urllib (less reliable)")

PORT      = 5000
NSE_HOME  = "https://www.nseindia.com"
NSE_API   = "https://www.nseindia.com/api/fiidiiTradeReact"
HTML_FILE = "fii_dii_india_flows_dashboard.html"
IST       = timezone(timedelta(hours=5, minutes=30))

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/123.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer":         "https://www.nseindia.com/",
    "Connection":      "keep-alive",
}

# ── GLOBAL CACHE ──────────────────────────────────────────────────────────────
_cache = {
    "data":     None,   # raw list from NSE
    "ts":       0.0,    # epoch of last successful fetch
    "for_date": "",     # date string of cached data
    "error":    None,
}
_lock = threading.Lock()

# ── WHEN TO REFRESH ────────────────────────────────────────────────────────────
def cache_is_fresh():
    """NSE data is once-a-day after market close; no point hammering the API."""
    if not _cache["data"] or not _cache["ts"]:
        return False
    now_ist = datetime.now(IST)
    age_sec = time.time() - _cache["ts"]
    # Market hours: 9:15–15:30 IST. Data available ~17:30–18:00 IST.
    # Once we have today's data after 15:30 IST, it's valid all day.
    if age_sec < 300:          # always fresh if fetched < 5 min ago
        return True
    if now_ist.hour < 15 or (now_ist.hour == 15 and now_ist.minute < 30):
        return age_sec < 3600  # during market: refresh every hour
    return age_sec < 43200     # after market close: keep till midnight

# ── NSE FETCH (requests.Session) ─────────────────────────────────────────────
def fetch_via_requests():
    session = requests.Session()
    session.headers.update(HEADERS)
    print("[FETCH] Calling NSE FII/DII API...")
    api_resp = session.get(NSE_API, timeout=20)
    if api_resp.status_code != 200:
        raise ConnectionError(f"NSE API returned {api_resp.status_code}: {api_resp.text[:200]}")
    data = api_resp.json()
    if not isinstance(data, list) or not data:
        raise ValueError(f"Unexpected response: {str(data)[:200]}")
    return data


# ── NSE FETCH (urllib fallback) ───────────────────────────────────────────────
def fetch_via_urllib():
    import urllib.request, http.cookiejar
    jar    = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = list(HEADERS.items())

    print("[FETCH] Warming up NSE session via urllib...")
    opener.open("https://www.nseindia.com/market-data/fii-dii-activity", timeout=15)
    time.sleep(1.5)

    print("[FETCH] Calling NSE FII/DII API via urllib...")
    with opener.open(NSE_API, timeout=15) as r:
        raw = r.read()
        try:
            raw = gzip.decompress(raw)
        except Exception:
            pass
        return json.loads(raw.decode("utf-8"))


# ── MAIN FETCH DISPATCHER ────────────────────────────────────────────────────
def do_fetch():
    if HAS_REQUESTS:
        return fetch_via_requests()
    return fetch_via_urllib()


def fetch_nse_data():
    """Fetch with caching. Returns (data_list, error_str)."""
    if cache_is_fresh():
        return _cache["data"], None

    try:
        data = do_fetch()
        with _lock:
            _cache["data"]     = data
            _cache["ts"]       = time.time()
            _cache["for_date"] = data[0].get("date", "") if data else ""
            _cache["error"]    = None
        ts = datetime.now(IST).strftime("%H:%M:%S IST")
        print(f"[{ts}] ✅  NSE data fetched — {len(data)} rows | date: {_cache['for_date']}")
        return data, None

    except Exception as exc:
        err = str(exc)
        print(f"[WARN] NSE fetch failed: {err}")
        with _lock:
            _cache["error"] = err
        return _cache["data"], err   # serve stale cache if available


# ── TRANSFORM → FRONTEND FORMAT ───────────────────────────────────────────────
def transform(raw):
    out = {"date":"","fii_buy":0,"fii_sell":0,"fii_net":0,
           "dii_buy":0,"dii_sell":0,"dii_net":0}
    for row in raw:
        cat = (row.get("category","")).upper()
        if "FII" in cat or "FPI" in cat:
            out["fii_buy"]  = float(row.get("buyValue",0) or 0)
            out["fii_sell"] = float(row.get("sellValue",0) or 0)
            out["fii_net"]  = float(row.get("netValue",0) or 0)
            out["date"]     = row.get("date","")
        elif "DII" in cat:
            out["dii_buy"]  = float(row.get("buyValue",0) or 0)
            out["dii_sell"] = float(row.get("sellValue",0) or 0)
            out["dii_net"]  = float(row.get("netValue",0) or 0)
    return out


# ── BACKGROUND DAILY REFRESH ──────────────────────────────────────────────────
def background_scheduler():
    """
    Check once every minute; re-fetch when:
    - We have no data yet
    - It's after 17:30 IST and our cached date is not today
    """
    while True:
        time.sleep(60)
        now_ist = datetime.now(IST)
        today   = now_ist.strftime("%-d-%b-%Y") if sys.platform != "win32" else now_ist.strftime("%#d-%b-%Y")
        # Trigger fetch after market close (17:30 IST) if date is stale
        if now_ist.hour >= 17 and now_ist.minute >= 30:
            if _cache.get("for_date","").lower() != today.lower() or not cache_is_fresh():
                print(f"[SCHEDULER] Post-market refresh triggered at {now_ist.strftime('%H:%M IST')}")
                fetch_nse_data()


# ── HTTP HANDLER ──────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass  # suppress noise

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(200); self._cors(); self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]

        if path == "/api/fii-dii":
            raw, err = fetch_nse_data()
            if raw:
                payload = transform(raw)
                payload["_source"]     = "live"
                payload["_fetched_at"] = datetime.now(IST).strftime("%d-%b-%Y %H:%M IST")
                payload["_cache_age"]  = int(time.time() - _cache["ts"])
                if err: payload["_warning"] = err
                body = json.dumps(payload).encode()
                self.send_response(200)
                self.send_header("Content-Type","application/json")
                self._cors()
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                body = json.dumps({"error": err or "No data"}).encode()
                self.send_response(503)
                self.send_header("Content-Type","application/json")
                self._cors()
                self.end_headers(); self.wfile.write(body)

        elif path == "/api/status":
            body = json.dumps({
                "running":    True,
                "cached":     _cache["data"] is not None,
                "for_date":   _cache["for_date"],
                "fetched_at": datetime.fromtimestamp(_cache["ts"],IST).strftime("%d-%b-%Y %H:%M IST") if _cache["ts"] else None,
                "cache_age_sec": int(time.time()-_cache["ts"]) if _cache["ts"] else None,
                "last_error": _cache["error"],
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type","application/json")
            self._cors()
            self.end_headers(); self.wfile.write(body)

        else:  # serve the dashboard HTML
            import os
            html = os.path.join(os.path.dirname(os.path.abspath(__file__)), HTML_FILE)
            try:
                with open(html,"rb") as f: body = f.read()
                self.send_response(200)
                self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers(); self.wfile.write(body)
            except FileNotFoundError:
                self.send_response(404); self.end_headers()
                self.wfile.write(b"Dashboard HTML not found.")


# ── ENTRY POINTS ──────────────────────────────────────────────────────────────
def run_server():
    print("=" * 58)
    print("  FII & DII Live Data Server  |  by Mr. Chartist")
    print(f"  Dashboard → http://localhost:{PORT}")
    print(f"  API       → http://localhost:{PORT}/api/fii-dii")
    print(f"  Status    → http://localhost:{PORT}/api/status")
    print("=" * 58)
    now_ist = datetime.now(IST)
    print(f"\n  Current IST: {now_ist.strftime('%d-%b-%Y %H:%M')}")
    print(  "  NSE data:   published once daily after ~17:30 IST")
    print(  "  Auto-refresh: every day after market close\n")

    print("[BOOT] Fetching today's NSE data...")
    fetch_nse_data()

    t = threading.Thread(target=background_scheduler, daemon=True)
    t.start()

    httpd = HTTPServer(("localhost", PORT), Handler)
    print(f"[READY] Server live at http://localhost:{PORT}")
    print("  Press Ctrl+C to stop\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[STOP] Server stopped.")


def debug_fetch():
    """Just fetch and print the data — no server."""
    print("=== DEBUG FETCH (no server) ===")
    raw, err = fetch_nse_data()
    if err: print(f"Error: {err}")
    if raw:
        d = transform(raw)
        print(json.dumps(d, indent=2))
    else:
        print("No data retrieved.")


if __name__ == "__main__":
    if "--fetch" in sys.argv:
        debug_fetch()
    else:
        run_server()
