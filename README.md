# 🚀 Vibe Trading AI — NSE Multi-Strategy Scanner

An institutional-grade, quantitative stock scanner for the Indian stock market (NSE), built with **Next.js** (frontend) and **Python** (serverless backend), deployable to Vercel.

## 🧠 Strategies

| Strategy | Confidence | Target | Description |
|---|---|---|---|
| 💎 RSI Divergence + Vol Spike | **77.8%** | 50%+ (Multibagger) | Price lower low, RSI higher low, 2.5x institutional volume |
| ⚡ DEMA Momentum Spike | 61.0% | 3% | DEMA 9 > EMA 21 with volume dry-up then spike |
| 📉 Pullback to Value | 64.4% | 3% | Near 50DMA with RSI < 55 in an uptrend |
| 🚀 Darvas Breakout | 44.6% | 3% | Above 50-day high with 2x volume |

## 📊 Backtest Results (3-Year, Nifty 500)
- **Win Rate** (best strategy): 77.8%
- **Avg Return per trade**: +0.70%
- **Target**: 3% fixed or 50%+ (multibagger)
- **Stop Loss**: 1.5–2.0x ATR

## 🛠️ Tech Stack
- **Frontend**: Next.js 16, TypeScript, Vanilla CSS
- **Backend**: Python Serverless Function (Vercel)
- **Data**: `yfinance` (Yahoo Finance API)
- **Indicators**: DEMA, EMA, RSI, ATR, Volume

## 🚀 Run Locally

### Step 1: Start the Python API
```bash
pip install yfinance pandas numpy
python run_local_api.py
```

### Step 2: Start the Next.js Frontend
```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) and click **Run AI Scanner**.

## 🌐 Deploy to Vercel

1. Push this repo to GitHub
2. Go to [vercel.com/new](https://vercel.com/new)
3. Import your GitHub repository
4. Vercel auto-detects Next.js + Python — click **Deploy**

## ⚠️ Disclaimer
This tool is for **educational and research purposes only**. It does not constitute financial advice. Always conduct your own due diligence before trading.
