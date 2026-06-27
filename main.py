

from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "NSE Alert Bot is Live"

import threading
def run():
  app.run(host='0.0.0.0', port=8080)
threading.Thread(target=run).start()

"""



NSE Stock News Scanner

Polls multiple RSS feeds and sends Telegram alerts for your watchlist.
"""

import os
import sys
import json
import time
import threading
import requests
import feedparser
from datetime import datetime
from html import unescape
import re

# ============================================================
# CONFIG
# ============================================================

WATCHLIST_FILE = "watchlist.json"

WATCHLIST = {
    "RELIANCE": ["Reliance Industries", "RIL"],
    "TCS": ["Tata Consultancy Services", "TCS"],
    "HDFCBANK": ["HDFC Bank"],
    "INFY": ["Infosys"],
    "ICIBANK": ["ICICI Bank"],
    "SBIN": ["State Bank of India", "SBI"],
    "TATAMOTORS": ["Tata Motors"],
    "ADANIENT": ["Adani Enterprises"],
    "ADANIPORTS": ["Adani Ports"],
    "BAJFINANCE": ["Baj Finance"],
    "360ONE": ["360 ONE WAM", "360 One Wam", "IIFL Wealth"],
    "ABB": ["ABB India"],
    "ABCAPITAL": ["Aditya Birla Capital"],
    "ADANIENSOL": ["Adani Energy Solutions"],
    "ADANIGREEN": ["Adani Green Energy"],
    "ADANIPOWER": ["Adani Power"],
    "ALKEM": ["Alkem Laboratories"],
    "AMBER": ["Amber Enterprises"],
    "AMBUJACEM": ["Ambuja Cements"],
    "ANGELONE": ["Angel One"],
    "APLAPOLLO": ["APL Apollo Tubes"],
    "APOLLOHOSP": ["Apollo Hospitals"],
    "ASHOKLEY": ["Ashok Leyland"],
    "ASIANPAINT": ["Asian Paints"],
    "ASTRAL": ["Astral Ltd", "Astral Pipes"],
    "AUBANK": ["AU Small Finance Bank"],
    "AUROPHARMA": ["Aurobindo Pharma"],
    "AXISBANK": ["Axis Bank"],
    "BAJAJ-AUTO": ["Baj Auto"],
    "BAJAJFINSV": ["Baj Finserv"],
    "BAJAJHLDNG": ["Baj Holdings"],
    "BANDHANBNK": ["Bandhan Bank"],
    "BANKBARODA": ["Bank of Baroda"],
    "BANKINDIA": ["Bank of India"],
    "BDL": ["Bharat Dynamics"],
    "BEL": ["Bharat Electronics"],
    "BHARATFORG": ["Bharat Forge"],
    "BHARTIARTL": ["Bharti Airtel", "Airtel"],
    "BHEL": ["Bharat Heavy Electricals"],
    "BIOCON": ["Biocon"],
    "BLUESTARCO": ["Blue Star"],
    "BOSCHLTD": ["Bosch Ltd", "Bosch India"],
    "BPCL": ["Bharat Petroleum", "BPCL"],
    "BRITANNIA": ["Britannia Industries"],
    "BSE": ["BSE Ltd", "Bombay Stock Exchange"],
    "CAMS": ["Computer Age Management Services", "CAMS"],
    "CANBK": ["Canara Bank"],
    "CDSL": ["Central Depository Services", "CDSL"],
    "CGPOWER": ["CG Power", "CG Power and Industrial Solutions"],
    "CHOLAFIN": ["Cholamandalam Investment", "Chola Finance"],
    "CIPLA": ["Cipla"],
    "COALINDIA": ["Coal India"],
    "COCHINSHIP": ["Cochin Shipyard"],
    "COFORGE": ["Coforge"],
    "COLPAL": ["Colgate-Palmolive", "Colgate Palmolive India"],
    "CONCOR": ["Container Corporation of India", "Concor"],
    "CROMPTON": ["Crompton Greaves Consumer", "Crompton Consumer"],
    "CUMMINSIND": ["Cummins India"],
    "DABUR": ["Dabur India"],
    "DALBHARAT": ["Dalmia Bharat"],
    "DELHIVERY": ["Delhivery"],
    "DIVISLAB": ["Divi's Laboratories", "Divis Labs"],
    "DIXON": ["Dixon Technologies"],
    "DLF": ["DLF Ltd"],
    "DMART": ["Avenue Supermarts", "DMart"],
    "DRREDDY": ["Dr Reddy's Laboratories", "Dr Reddys"],
    "EICHERMOT": ["Eicher Motors"],
    "ETERNAL": ["Eternal Ltd", "Zomato"],
    "EXIDEIND": ["Exide Industries"],
    "FEDERALBNK": ["Federal Bank"],
    "FORCEMOT": ["Force Motors"],
    "FORTIS": ["Fortis Healthcare"],
    "GAIL": ["GAIL India", "Gas Authority of India"],
    "GLENMARK": ["Glenmark Pharmaceuticals"],
    "GMRAIRPORT": ["GMR Airports", "GMR Infrastructure"],
    "GODFRYPHLP": ["Godfrey Phillips"],
    "GODREJCP": ["Godrej Consumer Products"],
    "GODREJPROP": ["Godrej Properties"],
    "GRASIM": ["Grasim Industries"],
    "GVT&D": ["GE Vernova T&D", "GE T&D India"],
    "HAL": ["Hindustan Aeronautics"],
    "HAVELLS": ["Havells India"],
    "HCLTECH": ["HCL Technologies"],
    "HDFCAMC": ["HDFC Asset Management", "HDFC AMC"],
    "HDFCLIFE": ["HDFC Life Insurance", "HDFC Life"],
    "HEROMOTOCO": ["Hero MotoCorp"],
    "HINDALCO": ["Hindalco Industries"],
    "HINDPETRO": ["Hindustan Petroleum", "HPCL"],
    "HINDUNILVR": ["Hindustan Unilever", "HUL"],
    "HINDZINC": ["Hindustan Zinc"],
    "HYUNDAI": ["Hyundai Motor India"],
    "ICIGI": ["ICICI Lombard", "ICICI General Insurance"],
    "ICIPRULI": ["ICICI Prudential Life Insurance", "ICICI Pru Life"],
    "IDEA": ["Vodafone Idea", "Vi"],
    "IDFCFIRSTB": ["IDFC First Bank"],
    "IEX": ["Indian Energy Exchange"],
    "INDHOTEL": ["Indian Hotels Company", "Taj Hotels"],
    "INDIANB": ["Indian Bank"],
    "INDIGO": ["IndiGo", "InterGlobe Aviation"],
    "INDUSINDBK": ["IndusInd Bank"],
    "INDUSTOWER": ["Indus Towers"],
    "INOXWIND": ["Inox Wind"],
    "IOC": ["Indian Oil Corporation", "IOCL"],
    "IREDA": ["Indian Renewable Energy Development Agency", "IREDA"],
    "IRFC": ["Indian Railway Finance Corporation"],
    "ITC": ["ITC Ltd", "ITC Limited"],
    "JINDALSTEL": ["Jindal Steel and Power", "Jindal Steel & Power"],
    "JIOFIN": ["Jio Financial Services"],
    "JSWENERGY": ["JSW Energy"],
    "JSWSTEEL": ["JSW Steel"],
    "JUBLFOOD": ["Jubilant FoodWorks", "Jubilant Foodworks"],
    "KALYANKJIL": ["Kalyan Jewellers"],
    "KAYNES": ["Kaynes Technology"],
    "KEI": ["KEI Industries"],
    "KFINTECH": ["KFin Technologies"],
    "KOTAKBANK": ["Kotak Mahindra Bank", "Kotak Bank"],
    "KPITTECH": ["KPIT Technologies"],
    "LAURUSLABS": ["Laurus Labs"],
    "LICHSGFIN": ["LIC Housing Finance"],
    "LICI": ["Life Insurance Corporation", "LIC"],
    "LODHA": ["Macrotech Developers", "Lodha Group"],
    "LT": ["Larsen & Toubro", "Larsen and Toubro", "L&T"],
    "LTF": ["L&T Finance"],
    "LTM": ["LTIMindtree", "L&T Mindtree"],
    "LUPIN": ["Lupin Ltd"],
    "M&M": ["Mahindra & Mahindra", "Mahindra and Mahindra"],
    "MANAPPURAM": ["Manappuram Finance"],
    "MANKIND": ["Mankind Pharma"],
    "MARICO": ["Marico Ltd"],
    "MARUTI": ["Maruti Suzuki"],
    "MAXHEALTH": ["Max Healthcare"],
    "MAZDOCK": ["Mazagon Dock Shipbuilders", "Mazagon Dock"],
    "MCX": ["Multi Commodity Exchange", "MCX India"],
    "MFSL": ["Max Financial Services"],
    "MOTHERSON": ["Samvardhana Motherson", "Motherson Sumi"],
    "MOTILALOFS": ["Motilal Oswal Financial Services", "Motilal Oswal"],
    "MPHASIS": ["Mphasis"],
    "MUTHOOTFIN": ["Muthoot Finance"],
    "NAM-INDIA": ["Nippon Life India Asset Management", "Nippon India AMC"],
    "NATIONALUM": ["National Aluminium Company", "Nalco"],
    "NAUKRI": ["Info Edge", "Naukri.com"],
    "NBCC": ["NBCC India", "National Buildings Construction Corporation"],
    "NESTLEIND": ["Nestle India"],
    "NHPC": ["NHPC Ltd"],
    "NMDC": ["NMDC Ltd"],
    "NTPC": ["NTPC Ltd"],
    "NUVAMA": ["Nuvama Wealth Management"],
    "NYKAA": ["FSN E-Commerce", "Nykaa"],
    "OBEROIRLTY": ["Oberoi Realty"],
    "OFSS": ["Oracle Financial Services Software", "Oracle Financial Services"],
    "OIL": ["Oil India"],
    "ONGC": ["Oil and Natural Gas Corporation", "ONGC"],
    "PAGEIND": ["Page Industries", "Jockey India"],
    "PATANJALI": ["Patanjali Foods"],
    "PAYTM": ["Paytm", "One97 Communications"],
    "PERSISTENT": ["Persistent Systems"],
    "PETRONET": ["Petronet LNG"],
    "PFC": ["Power Finance Corporation"],
    "PGEL": ["PG Electroplast"],
    "PHOENIXLTD": ["Phoenix Mills"],
    "PIDILITIND": ["Pidilite Industries"],
    "PIIND": ["PI Industries"],
    "PNB": ["Punjab National Bank"],
    "PNBHOUSING": ["PNB Housing Finance"],
    "POLICYBZR": ["PB Fintech", "Policybazaar"],
    "POLYCAB": ["Polycab India"],
    "POWERGRID": ["Power Grid Corporation"],
    "POWERINDIA": ["Hitachi Energy India", "Power India"],
    "PREMIERENE": ["Premier Energies"],
    "PRESTIGE": ["Prestige Estates"],
    "RADICO": ["Radico Khaitan"],
    "RBLBANK": ["RBL Bank"],
    "RECLTD": ["REC Ltd", "Rural Electrification Corporation"],
    "RVNL": ["Rail Vikas Nigam"],
    "SAIL": ["Steel Authority of India"],
    "SAMMAANCAP": ["Sammaan Capital", "Indiabulls Housing Finance"],
    "SBICARD": ["SBI Cards", "SBI Cards and Payment Services"],
    "SBILIFE": ["SBI Life Insurance"],
    "SHREECEM": ["Shree Cement"],
    "SHRIRAMFIN": ["Shriram Finance"],
    "SIEMENS": ["Siemens India", "Siemens Ltd"],
    "SOLARINDS": ["Solar Industries"],
    "SONACOMS": ["Sona BLW Precision Forgings", "Sona Comstar"],
    "SRF": ["SRF Ltd"],
    "SUNPHARMA": ["Sun Pharma", "Sun Pharmaceutical"],
    "SUPREMEIND": ["Supreme Industries"],
    "SUZLON": ["Suzlon Energy"],
    "SWIGGY": ["Swiggy"],
    "TATACONSUM": ["Tata Consumer Products"],
    "TATAELXSI": ["Tata Elxsi"],
    "TATAPOWER": ["Tata Power"],
    "TATASTEEL": ["Tata Steel"],
    "TECHM": ["Tech Mahindra"],
    "TIINDIA": ["Tube Investments of India", "TI India"],
    "TITAN": ["Titan Company"],
    "TMPV": ["Tata Motors Passenger Vehicles", "TMPV"],
    "TORNTPHARM": ["Torrent Pharmaceuticals"],
    "TRENT": ["Trent Ltd"],
    "TVSMOTOR": ["TVS Motor Company"],
    "ULTRACEMCO": ["UltraTech Cement"],
    "UNIONBANK": ["Union Bank of India"],
    "UNITDSPR": ["United Spirits"],
    "UNOMINDA": ["UNO Minda"],
    "UPL": ["UPL Ltd"],
    "VBL": ["Varun Beverages"],
    "VEDL": ["Vedanta Ltd"],
    "VMM": ["Vishal Mega Mart"],
    "VOLTAS": ["Voltas Ltd"],
    "WAAREEENER": ["Waaree Energies"],
    "WIPRO": ["Wipro Ltd"],
    "YESBANK": ["Yes Bank"],
    "ZYDUSLIFE": ["Zydus Lifesciences"]
}

RSS_FEEDS = {
    "ET Markets": "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms",
    "ET Top Stories": "https://economictimes.indiatimes.com/rssfeedsdefault.cms",
    "Moneycontrol Latest": "https://www.moneycontrol.com/rss/latestnews.xml",
    "Business Standard Markets": "https://www.business-standard.com/rss/markets-106.rss",
    "LiveMint Markets": "https://www.livemint.com/rss/markets",
    "CNBC TV18 Market": "https://www.cnbctv18.com/commonfeeds/v1/cne/rss/market.xml",
}

POLL_INTERVAL_SEC = 75
HTTP_TIMEOUT = (5, 10)
SEEN_CACHE_FILE = "news_seen_cache.json"
MAX_SEEN_CACHE = 2000
DASHBOARD_MAX_ROWS = 18
MAX_CONSECUTIVE_FAILS = 5

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

#...baki ka pura code wahi rahega jo tune bheja hai...
# [Lock, state, functions, main] sab same rakh de bas upar wala WATCHLIST replace kar de

lock = threading.Lock()
matches = []
seen_links = set()
feed_status = {}
feed_fail_counts = {}
stop_event = threading.Event()
telegram_queue = []
telegram_lock = threading.Lock()

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and data:
                return data
        except Exception as e:
            print(f"[warn] failed to load {WATCHLIST_FILE}: {e}; using inline WATCHLIST")
    return WATCHLIST

def build_matcher(watchlist):
    patterns = []
    for symbol, aliases in watchlist.items():
        all_names = set(aliases) | {symbol}
        escaped = sorted((re.escape(a) for a in all_names if a.strip()), key=len, reverse=True)
        if not escaped:
            continue
        pattern = re.compile(r"\b(" + "|".join(escaped) + r")\b", re.IGNORECASE)
        patterns.append((symbol, pattern))
    return patterns

def load_seen_cache():
    if os.path.exists(SEEN_CACHE_FILE):
        try:
            with open(SEEN_CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return set(data.get("seen", []))
        except Exception:
            return set()
    return set()

def save_seen_cache():
    try:
        with lock:
            trimmed = list(seen_links)[-MAX_SEEN_CACHE:]
        with open(SEEN_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"seen": trimmed}, f)
    except Exception as e:
        print(f"[warn] couldn't save seen cache: {e}")

def clean_text(raw):
    if not raw:
        return ""
    text = unescape(raw)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def fetch_feed_entries(name, url):
    resp = requests.get(url, timeout=HTTP_TIMEOUT, headers={"User-Agent": "Mozilla/5.0 (NewsScanner/1.0)"})
    resp.raise_for_status()
    parsed = feedparser.parse(resp.content)
    return parsed.entries or []

def poll_once(matcher):
    for name, url in RSS_FEEDS.items():
        if stop_event.is_set():
            return
        with lock:
            already_dead = feed_status.get(name, {}).get("dead", False)
        if already_dead:
            continue
        try:
            entries = fetch_feed_entries(name, url)
            with lock:
                feed_fail_counts[name] = 0
                feed_status[name] = {"ok": True, "last_poll": datetime.now().strftime("%H:%M:%S"), "items": len(entries), "error": "", "dead": False}
            process_entries(name, entries, matcher)
        except Exception as e:
            with lock:
                fails = feed_fail_counts.get(name, 0) + 1
                feed_fail_counts[name] = fails
                is_dead = fails >= MAX_CONSECUTIVE_FAILS
                feed_status[name] = {"ok": False, "last_poll": datetime.now().strftime("%H:%M:%S"), "items": 0, "error": str(e)[:60], "dead": is_dead}

def process_entries(source_name, entries, matcher):
    for entry in entries:
        link = entry.get("link", "")
        if not link:
            continue
        with lock:
            already_seen = link in seen_links
        if already_seen:
            continue
        title = clean_text(entry.get("title", ""))
        summary = clean_text(entry.get("summary", "") or entry.get("description", ""))
        haystack = f"{title} {summary}"
        hit_symbols = []
        for symbol, pattern in matcher:
            if pattern.search(haystack):
                hit_symbols.append(symbol)
        with lock:
            seen_links.add(link)
        if not hit_symbols:
            continue
        published = entry.get("published", "") or entry.get("updated", "")
        record = {"time": datetime.now().strftime("%H:%M:%S"), "symbols": hit_symbols, "source": source_name, "title": title, "link": link, "published": published}
        with lock:
            matches.append(record)
            if len(matches) > 500:
                matches.pop(0)
        with telegram_lock:
            telegram_queue.append(record)

def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML", "disable_web_page_preview": False}, timeout=(5, 10))
    except Exception:
        pass

def telegram_worker():
    while not stop_event.is_set():
        with telegram_lock:
            batch = telegram_queue[:]
            telegram_queue.clear()
        for record in batch:
            symbols = ", ".join(record["symbols"])
            msg = f"📰 <b>{symbols}</b>\n{record['title']}\n<i>{record['source']} • {record['time']}</i>\n{record['link']}"
            send_telegram_message(msg)
            time.sleep(1)
        time.sleep(1)

def poll_worker(matcher):
    while not stop_event.is_set():
        poll_once(matcher)
        save_seen_cache()
        for _ in range(POLL_INTERVAL_SEC):
            if stop_event.is_set():
                return
            time.sleep(1)

RESET = "\x1b[0m"; BOLD = "\x1b[1m"; FG_GREY = "\x1b[90m"; FG_GREEN = "\x1b[32m"; FG_RED = "\x1b[31m"
FG_WHITE = "\x1b[97m"; FG_AMBER = "\x1b[38;5;220m"; FG_CYAN = "\x1b[36m"; BG_AMBER = "\x1b[48;5;220m"; FG_BLACK = "\x1b[30m"
V = "║"; V2 = "│"; H = "═"; TL, TR, BL, BR = "╔", "╗", "╚", "╝"; ML, MR = "╠", "╣"; TERM_WIDTH = 104

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
def visible_len(s): return len(ANSI_RE.sub("", s))
def truncate(text, width): return text if len(text) <= width else text[:max(width - 1, 0)] + "…"
def pad(text, width): return text if len(text) >= width else text + " * (width - len(text))
def hline(width, left, mid, right, fill=H): return f"{FG_GREY}{left}{fill * width}{right}{RESET}"
def panel_line(content, width): return f"{FG_GREY}{V}{RESET}{content}{' ' * max(width - visible_len(content), 0)}{FG_GREY}{V}{RESET}"
def status_dot(status):
    if not status: return f"{FG_GREY}○{RESET}"
    if status.get("dead"): return f"{FG_GREY}✖{RESET}"
    return f"{FG_GREEN}●{RESET}" if status.get("ok") else f"{FG_RED}●{RESET}"

def render_dashboard(watchlist_count):
    with lock: recent = list(reversed(matches[-DASHBOARD_MAX_ROWS:])); statuses = dict(feed_status); total_matches = len(matches)
    live_count = sum(1 for s in statuses.values() if s.get("ok")); dead_count = sum(1 for s in statuses.values() if s.get("dead"))
    err_count = sum(1 for s in statuses.values() if not s.get("ok") and not s.get("dead")); now = datetime.now(); W = TERM_WIDTH; buf = []
    buf.append(hline(W, TL, H, TR)); header = f" {BOLD}{FG_WHITE}◢◤{RESET} {BOLD}{FG_AMBER}NSE NEWS TERMINAL{RESET}"; right = f"{FG_GREY}{now.strftime('%d-%b-%Y %H:%M:%S')}{RESET} {BOLD}{FG_GREEN}●{RESET} {FG_GREEN}LIVE{RESET}"
    buf.append(f"{FG_GREY}{V}{RESET}{header}{' ' * max(W - visible_len(header) - visible_len(right), 1)}{right}{FG_GREY}{V}{RESET}"); buf.append(hline(W, ML, H, MR))
    stats = f" {FG_GREY}WATCHLIST{RESET} {BOLD}{FG_WHITE}{watchlist_count:>4}{RESET} {FG_GREY}FEEDS{RESET} {BOLD}{FG_GREEN}{live_count}{RESET}{FG_GREY}/{len(RSS_FEEDS)}{RESET} {FG_GREY}ERRORS{RESET} {BOLD}{FG_RED if err_count else FG_GREY}{err_count}{RESET} {FG_GREY}DISABLED{RESET} {BOLD}{FG_GREY}{dead_count}{RESET} {FG_GREY}MATCHES{RESET} {BOLD}{FG_AMBER}{total_matches}{RESET} {FG_GREY}POLL{RESET} {BOLD}{FG_CYAN}{POLL_INTERVAL_SEC}s{RESET}"
    buf.append(panel_line(stats, W)); buf.append(hline(W, ML, H, MR))
    left_w, right_w = 30, W - 33; left_lines = [f"{FG_AMBER}{BOLD} DATA FEEDS{RESET}", f"{FG_GREY}{'─' * left_w}{RESET}"]
    for name in RSS_FEEDS: left_lines.append(f"{status_dot(statuses.get(name))} {truncate(name, left_w - 3)}")
    left_lines += [f"{FG_GREY}{'─' * left_w}{RESET}", f"{FG_AMBER}{BOLD} WATCHLIST{RESET}", f"{FG_GREY}{'─' * left_w}{RESET}", f"{FG_GREY} symbols:{RESET} {BOLD}{FG_WHITE}{watchlist_count}{RESET}", f"{FG_GREY} feeds:{RESET} {BOLD}{FG_WHITE}{len(RSS_FEEDS)}{RESET}", f"{FG_GREY} poll:{RESET} {BOLD}{FG_WHITE}{POLL_INTERVAL_SEC}s{RESET}", f"{FG_GREY} telegram:{RESET} {BOLD}{FG_GREEN}ON{RESET}" if TELEGRAM_BOT_TOKEN else f"{FG_GREY} telegram:{RESET} {BOLD}{FG_GREY}OFF{RESET}"]
    right_lines = [f"{FG_AMBER}{BOLD} LIVE NEWS FEED{RESET} {FG_GREY}(watchlist matches){RESET}", f"{FG_GREY}{'─' * right_w}{RESET}"]
    if not recent: right_lines.append(f"{FG_GREY} awaiting watchlist hits…{RESET}")
    else:
        for rec in recent[:10]:
            tag = truncate(",".join(rec["symbols"]), 16); head = f"{FG_GREY}[{rec['time']}]{RESET} {BG_AMBER}{FG_BLACK}{BOLD} {tag} {RESET} {FG_CYAN}{truncate(rec['source'],16)}{RESET}"
            right_lines += [head, f" {FG_WHITE}{truncate(rec['title'], right_w - 2)}{RESET}"]
    for i in range(max(len(left_lines), len(right_lines))):
        l = left_lines[i] if i < len(left_lines) else ""; r = right_lines[i] if i < len(right_lines) else ""
        buf.append(panel_line(f"{l}{' ' * max(left_w - visible_len(l), 0)} {FG_GREY}{V2}{RESET} {r}", W))
    buf.append(hline(W, ML, H, MR)); buf.append(panel_line(f" {FG_GREY}[Ctrl+C] stop [auto-refresh every 2s]{RESET}", W)); buf.append(hline(W, BL, H, BR))
    sys.stdout.write("\x1b[H\x1b[J" + "\n".join(buf) + "\n"); sys.stdout.flush()

def dashboard_loop(watchlist_count):
    while not stop_event.is_set(): render_dashboard(watchlist_count); time.sleep(2)

def main():
    watchlist = load_watchlist(); matcher = build_matcher(watchlist); global seen_links; seen_links = load_seen_cache()
    if not matcher: print("[error] watchlist is empty"); return
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: print("[info] Telegram disabled"); 
