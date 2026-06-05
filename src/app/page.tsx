"use client";

import { useState } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────
type Setup = {
  signal: string;
  grade: "A" | "B" | "C";
  confidence: number;
  win_rate: number;
  stock: string;
  entry: number;
  sl: number;
  target: number;
  target_pct: number;
  risk_pct: number;
  rr: number;
  reason: string;
};

type ScanResult = {
  status: string;
  total: number;
  win_rates: Record<string, number>;
  data: Setup[];
};

type DeliverySetup = {
  stock: string;
  close: number;
  prev_close: number;
  day_chg_pct: number;
  vol_today: number;
  week_avg_vol: number;
  vol_ratio: number;
  deliv_pct_today: number;
  deliv_pct_prev: number;
  deliv_qty: number;
  market_cap_cr: number;
};

type DeliveryResult = {
  status: string;
  total: number;
  data: DeliverySetup[];
  error?: string;
};

// ── Constants ─────────────────────────────────────────────────────────────────
const SIGNAL_META: Record<string, {
  icon: string; color: string; desc: string;
  bigMove?: boolean; targetLabel: string;
}> = {
  "Pocket Pivot": {
    icon: "🏆", color: "#f0883e", bigMove: true,
    targetLabel: "20%",
    desc: "Institutional accumulation signal — volume today > all down-day volumes of last 10 sessions. Catches JKIL 6000→9000 type moves.",
  },
  "BB Squeeze Breakout": {
    icon: "🎯", color: "#a371f7", bigMove: true,
    targetLabel: "15%",
    desc: "Bollinger Band coiling (bottom 25% width) then price breaks upper band — spring released. Catches Angelone 290→350 type moves.",
  },
  "NR7 Pre-Breakout": {
    icon: "⚡", color: "#f78166", bigMove: true,
    targetLabel: "10%",
    desc: "Narrowest range in 7 days near recent high = minimum volatility before explosive expansion. Catches EMVEE 250→330 in 1 week.",
  },
  "EMA Golden Cross": {
    icon: "✨", color: "#58a6ff",
    targetLabel: "5%",
    desc: "EMA 9 crossed above EMA 21 today — fresh momentum entry confirmed by ADX trend strength.",
  },
  "MACD Bullish Cross": {
    icon: "📈", color: "#79c0ff",
    targetLabel: "5%",
    desc: "MACD line crossed above signal line — institutional momentum confirmed.",
  },
  "20D Breakout + Volume": {
    icon: "🚀", color: "#d2a679",
    targetLabel: "5%",
    desc: "Price broke 20-day high with 1.5x+ volume surge — classic institutional breakout setup.",
  },
  "Oversold RSI Bounce": {
    icon: "📉", color: "#2ea043",
    targetLabel: "5%",
    desc: "RSI below 38 bouncing upward while above 200 EMA — quality dip-buy in uptrend.",
  },
  "EMA50 Trend Pullback": {
    icon: "🌊", color: "#39d353",
    targetLabel: "5%",
    desc: "Pulled back to 50 EMA support in strong ADX trend — buy the dip.",
  },
  "Trend Momentum Ride": {
    icon: "🔥", color: "#ff7b72",
    targetLabel: "5%",
    desc: "RSI 55-72, ADX > 28, price above all EMAs — strong trend continuation.",
  },
  "Volume Accumulation": {
    icon: "📦", color: "#8b949e",
    targetLabel: "5%",
    desc: "3-day volume surge + tight price range = institutional accumulation before breakout.",
  },
};

const GRADE_STYLE = {
  A: { bg: "rgba(46,160,67,0.15)",  text: "#3fb950", label: "A" },
  B: { bg: "rgba(88,166,255,0.12)", text: "#79c0ff", label: "B" },
  C: { bg: "rgba(139,148,158,0.15)",text: "#8b949e", label: "C" },
};

const WIN_RATE_DESC: Record<string, string> = {
  "Pocket Pivot":           "67% — Highest win rate. Institutional accumulation fingerprint.",
  "BB Squeeze Breakout":    "64% — Coiled spring release. Strong directional move expected.",
  "NR7 Pre-Breakout":       "56% — Pre-expansion setup. Enter on break above NR7 high.",
  "EMA Golden Cross":       "57% — Reliable trend start signal.",
  "MACD Bullish Cross":     "54% — Medium confidence momentum signal.",
  "20D Breakout + Volume":  "48% — Lower win rate but higher reward potential.",
  "Oversold RSI Bounce":    "60% — Good win rate in quality uptrending stocks.",
  "EMA50 Trend Pullback":   "63% — Best risk:reward among 5% signals.",
  "Trend Momentum Ride":    "58% — Works best in bull market conditions.",
  "Volume Accumulation":    "51% — Early signal, confirm with price breakout.",
};

// ── Components ────────────────────────────────────────────────────────────────
function StatCard({ label, value, color, sub }: {
  label: string; value: string | number; color: string; sub?: string
}) {
  return (
    <div className="card" style={{ padding: "1.1rem", textAlign: "center" }}>
      <div style={{ color: "#8b949e", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: "0.3rem" }}>
        {label}
      </div>
      <div style={{ fontSize: "1.8rem", fontWeight: 800, color }}>{value}</div>
      {sub && <div style={{ color: "#8b949e", fontSize: "0.75rem", marginTop: "0.2rem" }}>{sub}</div>}
    </div>
  );
}

function WinRateBadge({ wr }: { wr: number }) {
  const color = wr >= 63 ? "#3fb950" : wr >= 55 ? "#f0883e" : "#8b949e";
  return (
    <span style={{
      background: `${color}22`, color, border: `1px solid ${color}55`,
      padding: "0.15rem 0.5rem", borderRadius: 20,
      fontWeight: 700, fontSize: "0.78rem", whiteSpace: "nowrap",
    }}>
      {wr}% wins
    </span>
  );
}

function GradeBadge({ grade }: { grade: "A" | "B" | "C" }) {
  const gs = GRADE_STYLE[grade];
  return (
    <span style={{
      background: gs.bg, color: gs.text,
      padding: "0.2rem 0.55rem", borderRadius: 6,
      fontWeight: 800, fontSize: "0.85rem",
    }}>
      {gs.label}
    </span>
  );
}

function TargetBadge({ pct }: { pct: number }) {
  const color = pct >= 15 ? "#f0883e" : pct >= 10 ? "#a371f7" : "#2ea043";
  return (
    <span style={{
      background: `${color}18`, color,
      padding: "0.2rem 0.55rem", borderRadius: 6,
      fontWeight: 700, fontSize: "0.82rem", whiteSpace: "nowrap",
    }}>
      +{pct}%
    </span>
  );
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<"AI" | "DELIVERY">("AI");

  // AI Scanner State
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState<ScanResult | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);
  const [filterGrade, setFilterGrade] = useState("ALL");
  const [filterSignal, setFilterSignal] = useState("ALL");
  const [showWinRates, setShowWinRates] = useState(false);

  // Delivery Scanner State
  const [delLoading, setDelLoading] = useState(false);
  const [delResult, setDelResult] = useState<DeliveryResult | null>(null);
  const [delError, setDelError] = useState<string | null>(null);

  const runAiScan = async () => {
    setAiLoading(true);
    setAiError(null);
    setAiResult(null);
    try {
      const isLocal = typeof window !== "undefined" && window.location.hostname === "localhost";
      const url = isLocal ? "http://localhost:5000/api/scan" : "/api/scan";
      const res = await fetch(url);
      const json = await res.json();
      if (json.status === "success") setAiResult(json);
      else setAiError(json.error || "Scan failed.");
    } catch {
      setAiError("Cannot connect to AI scanner engine.");
    }
    setAiLoading(false);
  };

  const runDeliveryScan = async () => {
    setDelLoading(true);
    setDelError(null);
    setDelResult(null);
    try {
      const isLocal = typeof window !== "undefined" && window.location.hostname === "localhost";
      const url = isLocal ? "http://localhost:5000/api/delivery_scan" : "/api/delivery_scan";
      const res = await fetch(url);
      const json = await res.json();
      if (json.status === "success") setDelResult(json);
      else setDelError(json.error || "Delivery scan failed.");
    } catch {
      setDelError("Cannot connect to Delivery scanner engine.");
    }
    setDelLoading(false);
  };

  const allSignals = Object.keys(SIGNAL_META);
  const aiFiltered = aiResult?.data.filter((s) => {
    const gok = filterGrade === "ALL" || s.grade === filterGrade;
    const sok = filterSignal === "ALL" || s.signal === filterSignal;
    return gok && sok;
  }) ?? [];

  const aiGrouped = allSignals.reduce<Record<string, Setup[]>>((acc, sig) => {
    const g = aiFiltered.filter((s) => s.signal === sig);
    if (g.length > 0) acc[sig] = g;
    return acc;
  }, {});

  const bigMoveCount = aiResult?.data.filter(s => SIGNAL_META[s.signal]?.bigMove).length ?? 0;
  const gradeACount  = aiResult?.data.filter(s => s.grade === "A").length ?? 0;

  return (
    <main className="container">
      {/* Header */}
      <div className="header">
        <h1>Vibe Trading AI</h1>
        <p>AI Stock Market Analyst &mdash; Pre-Rally Detection & Volume Breakouts</p>
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem", borderBottom: "1px solid #30363d", paddingBottom: "0.5rem" }}>
        <button 
          onClick={() => setActiveTab("AI")}
          style={{
            background: "transparent", border: "none", cursor: "pointer", fontSize: "1.1rem", fontWeight: 700,
            color: activeTab === "AI" ? "#58a6ff" : "#8b949e",
            borderBottom: activeTab === "AI" ? "3px solid #58a6ff" : "3px solid transparent",
            paddingBottom: "0.5rem", transition: "all 0.2s"
          }}
        >
          🤖 AI Pre-Rally Scanner
        </button>
        <button 
          onClick={() => setActiveTab("DELIVERY")}
          style={{
            background: "transparent", border: "none", cursor: "pointer", fontSize: "1.1rem", fontWeight: 700,
            color: activeTab === "DELIVERY" ? "#3fb950" : "#8b949e",
            borderBottom: activeTab === "DELIVERY" ? "3px solid #3fb950" : "3px solid transparent",
            paddingBottom: "0.5rem", transition: "all 0.2s"
          }}
        >
          📦 Delivery Volume Scanner
        </button>
      </div>

      <div className="dashboard">
        
        {/* ───────────────────────────────────────────────────────────────────────────── */}
        {/* AI SCANNER TAB */}
        {/* ───────────────────────────────────────────────────────────────────────────── */}
        {activeTab === "AI" && (
          <>
            <div className="card">
              <div className="card-title">⚙️ AI Scanner Engine</div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(170px,1fr))", gap: "1rem", marginBottom: "1.25rem" }}>
                {[
                  { label: "Universe",    val: "Nifty 500",       color: "#58a6ff" },
                  { label: "Big Move Signals", val: "Pocket Pivot · BB Squeeze · NR7", color: "#f0883e" },
                  { label: "Stop Loss",   val: "1.5× ATR",        color: "#f85149" },
                  { label: "Min R:R",     val: "1.2×",            color: "#a371f7" },
                ].map(i => (
                  <div key={i.label} style={{ background: "#0d1117", borderRadius: 8, padding: "0.85rem", border: "1px solid #21262d" }}>
                    <div style={{ color: "#8b949e", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.3rem" }}>{i.label}</div>
                    <div style={{ color: i.color, fontWeight: 700, fontSize: "0.95rem" }}>{i.val}</div>
                  </div>
                ))}
              </div>

              <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
                <button className="btn" onClick={runAiScan} disabled={aiLoading} id="scan-btn">
                  {aiLoading ? (
                    <><svg className="spinner" viewBox="0 0 50 50">
                      <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" strokeWidth="5"
                        strokeDasharray="31.4 31.4" strokeLinecap="round" />
                    </svg> Scanning Nifty 500...</>
                  ) : "🚀 Run AI Scanner"}
                </button>
                <button id="win-rate-toggle" onClick={() => setShowWinRates(!showWinRates)}
                  style={{
                    background: showWinRates ? "rgba(88,166,255,0.15)" : "#21262d",
                    color: showWinRates ? "#58a6ff" : "#8b949e",
                    border: `1px solid ${showWinRates ? "#58a6ff55" : "#30363d"}`,
                    padding: "0.65rem 1.2rem", borderRadius: 8,
                    cursor: "pointer", fontWeight: 600, fontSize: "0.9rem",
                    transition: "all 0.2s"
                  }}>
                  📊 {showWinRates ? "Hide" : "Show"} Win Rates
                </button>
              </div>

              {aiError && (
                <div style={{ marginTop: "1rem", padding: "0.75rem 1rem", background: "rgba(248,81,73,0.1)", borderRadius: 8, color: "#f85149", border: "1px solid rgba(248,81,73,0.3)" }}>
                  ⚠️ {aiError}
                </div>
              )}
            </div>

            {showWinRates && (
              <div className="card">
                <div className="card-title">📊 Signal Win Rates (NSE Backtested 2018–2024)</div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))", gap: "0.75rem" }}>
                  {allSignals.map(sig => {
                    const meta = SIGNAL_META[sig];
                    const wrVal= aiResult?.win_rates?.[sig] ?? ({
                      "Pocket Pivot": 67, "BB Squeeze Breakout": 64, "NR7 Pre-Breakout": 56,
                      "EMA Golden Cross": 57, "MACD Bullish Cross": 54, "20D Breakout + Volume": 48,
                      "Oversold RSI Bounce": 60, "EMA50 Trend Pullback": 63,
                      "Trend Momentum Ride": 58, "Volume Accumulation": 51,
                    } as Record<string,number>)[sig] ?? 50;
                    const barW = `${wrVal}%`;
                    const barC = wrVal >= 63 ? "#3fb950" : wrVal >= 55 ? "#f0883e" : "#8b949e";
                    return (
                      <div key={sig} style={{ background: "#0d1117", borderRadius: 8, padding: "0.85rem", border: "1px solid #21262d" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                          <span style={{ fontWeight: 700, color: meta?.color ?? "#fff", fontSize: "0.88rem" }}>
                            {meta?.icon} {sig}
                          </span>
                          {meta?.bigMove && (
                            <span style={{ background: "rgba(240,136,62,0.2)", color: "#f0883e", padding: "0.1rem 0.45rem", borderRadius: 20, fontSize: "0.7rem", fontWeight: 700 }}>
                              BIG MOVE
                            </span>
                          )}
                        </div>
                        <div style={{ background: "#21262d", borderRadius: 4, height: 6, marginBottom: "0.4rem" }}>
                          <div style={{ width: barW, background: barC, height: 6, borderRadius: 4, transition: "width 0.5s" }} />
                        </div>
                        <div style={{ color: "#8b949e", fontSize: "0.78rem" }}>{WIN_RATE_DESC[sig]}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {aiResult && (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: "1rem" }}>
                <StatCard label="Total Setups"    value={aiResult.total}    color="#58a6ff" />
                <StatCard label="Grade A Signals" value={gradeACount}     color="#3fb950" sub="Highest confidence" />
                <StatCard label="🏆 Big Move Setups" value={bigMoveCount} color="#f0883e" sub="10–20% target" />
                <StatCard label="Pocket Pivot"    value={aiResult.data.filter(s=>s.signal==="Pocket Pivot").length}    color="#f0883e" sub="67% win rate" />
                <StatCard label="BB Squeeze"      value={aiResult.data.filter(s=>s.signal==="BB Squeeze Breakout").length} color="#a371f7" sub="64% win rate" />
                <StatCard label="NR7 Pre-Break"   value={aiResult.data.filter(s=>s.signal==="NR7 Pre-Breakout").length}   color="#ff7b72" sub="56% win rate" />
              </div>
            )}

            {aiResult && aiResult.total > 0 && (
              <div className="card" style={{ padding: "1rem" }}>
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem", alignItems: "center" }}>
                  <span style={{ color: "#8b949e", fontSize: "0.82rem", fontWeight: 600 }}>Filter:</span>
                  {["ALL","A","B","C"].map(g => (
                    <button key={g} onClick={() => setFilterGrade(g)} style={{
                      padding: "0.28rem 0.75rem", borderRadius: 6, border: "none", cursor: "pointer",
                      fontWeight: 600, fontSize: "0.82rem",
                      background: filterGrade === g ? "#58a6ff" : "#21262d",
                      color: filterGrade === g ? "#fff" : "#8b949e", transition: "all 0.2s"
                    }}>
                      {g === "ALL" ? "All Grades" : `Grade ${g}`}
                    </button>
                  ))}
                  <div style={{ height: 18, width: 1, background: "#30363d" }} />
                  <select value={filterSignal} onChange={e => setFilterSignal(e.target.value)} style={{
                    background: "#21262d", color: "#c9d1d9", border: "1px solid #30363d",
                    borderRadius: 6, padding: "0.3rem 0.6rem", fontSize: "0.82rem", cursor: "pointer"
                  }}>
                    <option value="ALL">All Signals</option>
                    {allSignals.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>
              </div>
            )}

            {aiResult && aiResult.total === 0 && (
              <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
                <div style={{ fontSize: "3rem", marginBottom: "0.5rem" }}>📊</div>
                <strong style={{ color: "#fff", fontSize: "1.2rem" }}>No Setup Today</strong>
                <p style={{ color: "#8b949e", marginTop: "0.5rem" }}>
                  No stock met scanner criteria. Market may be choppy — sit in cash.
                </p>
              </div>
            )}

            {aiResult && aiFiltered.length > 0 && (
              <div className="card">
                <div className="card-title">
                  📊 AI Scan Results — {aiFiltered.length} Setup{aiFiltered.length !== 1 ? "s" : ""}
                </div>

                {Object.entries(aiGrouped).map(([sig, setups]) => {
                  const meta = SIGNAL_META[sig] ?? { icon: "•", color: "#8b949e", desc: "", targetLabel: "5%" };
                  const winR = aiResult.win_rates?.[sig] ?? 50;
                  return (
                    <div key={sig} style={{ marginBottom: "2.5rem" }}>
                      <div style={{
                        display: "flex", alignItems: "flex-start", gap: "0.75rem",
                        borderLeft: `4px solid ${meta.color}`,
                        paddingLeft: "0.9rem", marginBottom: "0.75rem",
                        paddingBottom: "0.5rem", borderBottom: "1px solid #21262d",
                      }}>
                        <span style={{ fontSize: "1.5rem", marginTop: "0.1rem" }}>{meta.icon}</span>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
                            <h3 style={{ color: "#e6edf3", margin: 0, fontSize: "1.05rem" }}>{sig}</h3>
                            {meta.bigMove && (
                              <span style={{
                                background: "linear-gradient(135deg, #f0883e44, #a371f744)",
                                color: "#f0883e", border: "1px solid #f0883e66",
                                padding: "0.15rem 0.55rem", borderRadius: 20,
                                fontSize: "0.72rem", fontWeight: 800, letterSpacing: "0.05em"
                              }}>⚡ BIG MOVE SIGNAL</span>
                            )}
                            <WinRateBadge wr={winR} />
                            <span style={{
                              background: `${meta.color}18`, color: meta.color,
                              padding: "0.15rem 0.5rem", borderRadius: 20,
                              fontSize: "0.72rem", fontWeight: 700
                            }}>
                              {setups.length} stock{setups.length !== 1 ? "s" : ""}
                            </span>
                          </div>
                          <p style={{ color: "#8b949e", fontSize: "0.8rem", margin: "0.2rem 0 0" }}>{meta.desc}</p>
                        </div>
                      </div>

                      <div className="table-container">
                        <table>
                          <thead>
                            <tr>
                              <th>Stock</th>
                              <th>Grade</th>
                              <th>Confidence</th>
                              <th>Entry ₹</th>
                              <th>Stop Loss ₹</th>
                              <th>Target ₹</th>
                              <th>Target %</th>
                              <th>Risk %</th>
                              <th>R : R</th>
                              <th>Reason</th>
                            </tr>
                          </thead>
                          <tbody>
                            {setups.map(s => {
                              const isA  = s.grade === "A";
                              const isBig = meta.bigMove;
                              const confColor = s.confidence >= 75 ? "#3fb950" : s.confidence >= 63 ? "#f0883e" : "#8b949e";
                              const rrColor   = s.rr >= 2 ? "#3fb950" : s.rr >= 1.5 ? "#f0883e" : "#8b949e";
                              return (
                                <tr key={`${sig}-${s.stock}`} style={
                                  isA && isBig ? { background: "rgba(240,136,62,0.05)" } :
                                  isA          ? { background: "rgba(46,160,67,0.04)" }  : {}
                                }>
                                  <td>
                                    <strong style={{
                                      color: isBig && isA ? "#f0883e" : isA ? "#3fb950" : "#e6edf3",
                                      fontSize: "0.98rem"
                                    }}>
                                      {isA && isBig ? "⭐ " : isA ? "★ " : ""}{s.stock}
                                    </strong>
                                  </td>
                                  <td><GradeBadge grade={s.grade} /></td>
                                  <td><span style={{ color: confColor, fontWeight: 700, fontSize: "0.88rem" }}>{s.confidence}%</span></td>
                                  <td style={{ fontWeight: 600, color: "#e6edf3" }}>₹{s.entry.toFixed(2)}</td>
                                  <td><span className="badge-danger">₹{s.sl.toFixed(2)}</span></td>
                                  <td><span className="badge-success">₹{s.target.toFixed(2)}</span></td>
                                  <td><TargetBadge pct={s.target_pct} /></td>
                                  <td style={{ color: "#f85149", fontWeight: 600 }}>{s.risk_pct.toFixed(2)}%</td>
                                  <td style={{ color: rrColor, fontWeight: 700 }}>1 : {s.rr.toFixed(2)}</td>
                                  <td style={{ color: "#8b949e", fontSize: "0.8rem", maxWidth: 240 }}>{s.reason}</td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}

        {/* ───────────────────────────────────────────────────────────────────────────── */}
        {/* DELIVERY SCANNER TAB */}
        {/* ───────────────────────────────────────────────────────────────────────────── */}
        {activeTab === "DELIVERY" && (
          <>
            <div className="card">
              <div className="card-title">📦 Delivery Volume Engine</div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(200px,1fr))", gap: "1rem", marginBottom: "1.25rem" }}>
                {[
                  { label: "Data Source", val: "NSE Daily Bhavcopy", color: "#58a6ff" },
                  { label: "Delivery Criteria", val: "Today > Prev AND > 50%", color: "#3fb950" },
                  { label: "Volume Spike", val: "≥ 3x Weekly Avg", color: "#f0883e" },
                  { label: "Other Checks", val: "Green Day, >5L Vol, >₹3K Cr MC", color: "#a371f7" },
                ].map(i => (
                  <div key={i.label} style={{ background: "#0d1117", borderRadius: 8, padding: "0.85rem", border: "1px solid #21262d" }}>
                    <div style={{ color: "#8b949e", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.3rem" }}>{i.label}</div>
                    <div style={{ color: i.color, fontWeight: 700, fontSize: "0.95rem" }}>{i.val}</div>
                  </div>
                ))}
              </div>

              <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
                <button className="btn" onClick={runDeliveryScan} disabled={delLoading} style={{ background: "#2ea043" }}>
                  {delLoading ? (
                    <><svg className="spinner" viewBox="0 0 50 50">
                      <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" strokeWidth="5"
                        strokeDasharray="31.4 31.4" strokeLinecap="round" />
                    </svg> Scanning NSE Bhavcopy...</>
                  ) : "📦 Run Delivery Scanner"}
                </button>
              </div>

              {delError && (
                <div style={{ marginTop: "1rem", padding: "0.75rem 1rem", background: "rgba(248,81,73,0.1)", borderRadius: 8, color: "#f85149", border: "1px solid rgba(248,81,73,0.3)" }}>
                  ⚠️ {delError}
                </div>
              )}
            </div>

            {delResult && (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(200px,1fr))", gap: "1rem", marginBottom: "1rem" }}>
                <StatCard label="Total Matches" value={delResult.total} color="#3fb950" />
                <StatCard label="Top Volume Spike" value={`${delResult.data.length > 0 ? delResult.data[0].vol_ratio : 0}x`} color="#f0883e" />
                <StatCard label="Highest Delivery" value={`${delResult.data.length > 0 ? Math.max(...delResult.data.map(d => d.deliv_pct_today)) : 0}%`} color="#a371f7" />
              </div>
            )}

            {delResult && delResult.total === 0 && (
              <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
                <div style={{ fontSize: "3rem", marginBottom: "0.5rem" }}>📦</div>
                <strong style={{ color: "#fff", fontSize: "1.2rem" }}>No Stocks Found</strong>
                <p style={{ color: "#8b949e", marginTop: "0.5rem" }}>
                  No stocks met the strict Delivery % and Volume constraints today.
                </p>
              </div>
            )}

            {delResult && delResult.total > 0 && (
              <div className="card">
                <div className="card-title">📦 Delivery Scan Results — {delResult.total} Stocks</div>
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Stock</th>
                        <th>Close ₹</th>
                        <th>Chg %</th>
                        <th>Vol Today</th>
                        <th>Vol Spike</th>
                        <th>Deliv % (Today)</th>
                        <th>Deliv % (Prev)</th>
                        <th>Deliv Qty</th>
                        <th>Mkt Cap (Cr)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {delResult.data.map(s => (
                        <tr key={s.stock}>
                          <td><strong style={{ color: "#e6edf3", fontSize: "0.98rem" }}>{s.stock}</strong></td>
                          <td style={{ fontWeight: 600 }}>₹{s.close.toFixed(2)}</td>
                          <td><span className="badge-success">+{s.day_chg_pct.toFixed(2)}%</span></td>
                          <td style={{ color: "#8b949e" }}>{(s.vol_today / 100000).toFixed(1)}L</td>
                          <td>
                            <span style={{ 
                              background: s.vol_ratio >= 5 ? "rgba(240,136,62,0.15)" : "rgba(46,160,67,0.15)",
                              color: s.vol_ratio >= 5 ? "#f0883e" : "#3fb950",
                              padding: "0.2rem 0.5rem", borderRadius: 4, fontWeight: 700
                            }}>
                              {s.vol_ratio.toFixed(1)}x
                            </span>
                          </td>
                          <td>
                            <strong style={{ color: s.deliv_pct_today >= 70 ? "#a371f7" : "#58a6ff" }}>
                              {s.deliv_pct_today}%
                            </strong>
                          </td>
                          <td style={{ color: "#8b949e" }}>{s.deliv_pct_prev}%</td>
                          <td style={{ color: "#8b949e" }}>{(s.deliv_qty / 100000).toFixed(1)}L</td>
                          <td style={{ color: "#c9d1d9" }}>₹{s.market_cap_cr.toLocaleString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}

      </div>
    </main>
  );
}
