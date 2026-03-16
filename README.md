# 📊 FII & DII Data — India Institutional Flow Tracker

> **Track exactly what Foreign & Domestic big money is doing in the Indian stock market — updated live every day after market close.**

Built by [Mr. Chartist](https://twitter.com/mr_chartist) · Free · Open Source · No login required

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Twitter Follow](https://img.shields.io/twitter/follow/mr_chartist?style=social)](https://twitter.com/mr_chartist)

---

## 🤔 What Is This?

This is a **dashboard** that shows you:
- **FII (Foreign Institutional Investors)** — Are foreigners buying or selling Indian stocks today?
- **DII (Domestic Institutional Investors)** — Are Indian mutual funds & institutions buying or selling?
- Historical data going back **14 years**
- Visual patterns, streaks, heatmaps, and charts — all in one place

**Why does this matter?** When FIIs sell heavily, markets usually fall. When DIIs absorb that selling, it cushions the fall. This dashboard tells you exactly who is doing what, in real-time.

---

## 🚀 How to Use It (Step-by-Step for Everyone)

You do **not** need to be a programmer. Follow these steps exactly.

### Step 1 — Download the Project

Click the green **"Code"** button on this page → **"Download ZIP"** → Extract it to any folder on your computer (e.g., `D:\FII-DII-Data`).

*Or if you know Git:*
```
git clone https://github.com/MrChartist/fii-dii-data.git
```

---

### Step 2 — Install Python (One-time only)

Python is the engine that fetches live data from NSE. You only do this once.

1. Go to 👉 **https://www.python.org/downloads/**
2. Click **"Download Python"** (the big yellow button)
3. Run the installer
4. ⚠️ **IMPORTANT:** On the first screen, check the box that says **"Add Python to PATH"** before clicking Install

![Python Install Screenshot](docs/python_install_tip.png)

---

### Step 3 — Install the Data Fetcher (One-time only)

1. Open the folder where you extracted the project
2. In the address bar of the folder, type `cmd` and press Enter — a black window opens
3. Copy-paste this command and press Enter:

```
pip install requests
```

Wait for it to finish (takes ~10 seconds). You'll see "Successfully installed".

---

### Step 4 — Start the Live Data Server

Every time you want to use the dashboard:

1. Go to your project folder
2. **Double-click `start.bat`**

A black window will appear saying **"Server live at http://localhost:5000"** — keep this window open while using the dashboard.

> 💡 **Windows users:** After the first time, this starts automatically when you log in to your computer. You don't need to double-click it again after a restart.

---

### Step 5 — Open the Dashboard

Open your browser (Chrome, Edge, Firefox) and go to:

**➡️ http://localhost:5000**

Bookmark this link. That's your dashboard — always open this, not the HTML file directly.

---

## 🟢 Understanding the Status Pill (Top Right)

| What You See | What It Means |
|---|---|
| 🟢 **LIVE • Refresh in 04:55** | ✅ Today's real data from NSE. Auto-refreshes every 5 minutes |
| 🟡 **LOCAL ARCHIVE** | Markets are closed or data not yet published. Shows last known data |
| 🔴 **NSE BLOCKED** | Server is not running. Double-click `start.bat` to fix this |

---

## 📊 What's On the Dashboard

### Hero Section (Top)
- **FII Net** — Total net buying/selling by foreign investors today (in ₹ Crore)
- **DII Net** — Total net buying/selling by domestic funds today
- **Combined Liquidity** — The net overall impact on market liquidity
- **Flow Strength Meter** — Shows who is the bigger force today (FII or DII)

### FII Streak Counter
How many consecutive days FIIs have been on the same side:
- 🔴 **5+ days selling** = market under pressure, possible oversold bounce coming
- 🟢 **5+ days buying** = strong foreign re-entry signal

### Tabs at the Bottom

| Tab | What's Inside |
|---|---|
| **Databases & Matrices** | Daily, Weekly, Monthly & Annual data tables with smart filters |
| **Visual Flow Heatmaps** | 45-day color grid — spot patterns at a glance |
| **Historical Charts** | 12-month bar chart & 14-year cumulative divergence chart |
| **Documentation** | Full feature guide |

### Smart Filters (in the Daily table)
- **FII Bloodbath** — Only days where FIIs sold more than ₹5,000 Cr (the really bad days)
- **DII Absorption** — Days where DIIs bought more than ₹5,000 Cr (strong domestic defense)
- **Extreme Divergence** — FII sold ≥₹8,000 Cr AND DII bought ≥₹8,000 Cr (structural rotation — rare and very significant)

---

## 💾 Exporting & Sharing

- **📷 Export any card** — Hover over any card → click the 📷 camera icon → saves as PNG with watermark
- **📸 Snapshot Full Page** — Header button → saves the entire dashboard as one image
- **𝕏 Post to X** — Pre-fills a tweet with today's flow data. One click to share your analysis

---

## ❓ Common Questions

**"The black window (server) disappeared — dashboard isn't loading"**
→ Just double-click `start.bat` again to restart it.

**"It says LOCAL ARCHIVE, not LIVE"**
→ NSE only publishes FII/DII data after market close (~5:30–6:00 PM IST). If it's before that, local archive is correct and expected.

**"I see data from a few days ago, but today's isn't there"**
→ Check if the server is running (the black window). If it is, click **Force Sync** in the top-right.

**"Can I use this on my phone?"**
→ The dashboard is mobile-responsive, but the live server needs to run on a PC/laptop. You can open `http://YOUR-PC-IP:5000` on your phone if both are on the same WiFi.

**"Is my data safe? Does this send anything to the internet?"**
→ The only external request is fetching data FROM NSE India's public API. Nothing from your computer is ever sent anywhere.

---

## 🛠️ For Technical Users

### How the Live Sync Works
`server.py` is a lightweight local web server (no cloud, no backend) that:
1. Creates a browser-like session with proper cookies & headers
2. Calls `https://www.nseindia.com/api/fiidiiTradeReact`
3. Caches the result — refreshes automatically after 5:30 PM IST each day
4. Serves the dashboard at `http://localhost:5000`

### Tech Stack
| Technology | Purpose |
|---|---|
| Vanilla HTML/CSS/JS | Dashboard UI — zero dependencies, no build step |
| Python + requests | Local proxy server with NSE session handling |
| Chart.js | Interactive historical charts |
| html2canvas | High-DPI widget snapshot export |
| NSE India Public API | Live FII/DII data source |

### Files
| File | Purpose |
|---|---|
| `fii_dii_india_flows_dashboard.html` | The entire dashboard UI |
| `server.py` | Live data server (run this!) |
| `start.bat` | Windows one-click launcher |
| `requirements.txt` | Python dependencies (`pip install -r requirements.txt`) |

---

## 🤝 Contributing

PRs and issues are very welcome!

Ideas:
- [ ] Mac/Linux auto-start script
- [ ] Nifty 50 overlay on flow charts
- [ ] GitHub Actions to auto-update embedded data daily
- [ ] Export to CSV from data matrix
- [ ] Sector-wise FII flow breakdown

---

## 📜 License

MIT — use it, fork it, share it freely. Attribution appreciated.

---

## 👋 Author

Made with ❤️ by [Mr. Chartist](https://twitter.com/mr_chartist)

If this helps your trading, a ⭐ star on GitHub means a lot!

---

*⚠️ Disclaimer: This tool is for educational and informational purposes only. Not financial advice. Always do your own research.*
