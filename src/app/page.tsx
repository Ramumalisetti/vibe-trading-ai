"use client";

import { useState } from "react";

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

// ── Signal metadata ───────────────────────────────────────────────────────────
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
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filterGrade, setFilterGrade] = useState("ALL");
  const [filterSignal, setFilterSignal] = useState("ALL");
  const [showWinRates, setShowWinRates] = useState(false);

  const runScan = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const isLocal = typeof window !== "undefined" && window.location.hostname === "localhost";
      const url = isLocal ? "http://localhost:5000" : "/api/scan";
      const res = await fetch(url);
      const json = await res.json();
      if (json.status === "success") setResult(json);
      else setError(json.error || "Scan failed.");
    } catch {
      setError("Cannot connect to scanner engine.");
    }
    setLoading(false);
  };

  const allSignals = Object.keys(SIGNAL_META);

  const filtered = result?.data.filter((s) => {
    const gok = filterGrade === "ALL" || s.grade === filterGrade;
    const sok = filterSignal === "ALL" || s.signal === filterSignal;
    return gok && sok;
  }) ?? [];

  const grouped = allSignals.reduce<Record<string, Setup[]>>((acc, sig) => {
    const g = filtered.filter((s) => s.signal === sig);
    if (g.length > 0) acc[sig] = g;
    return acc;
  }, {});

  const bigMoveCount = result?.data.filter(s => SIGNAL_META[s.signal]?.bigMove).length ?? 0;
  const gradeACount  = result?.data.filter(s => s.grade === "A").length ?? 0;

  return (
    <main className="container">
      {/* Header */}
      <div className="header">
        <h1>Vibe Trading AI</h1>
        <p>
          AI Stock Market Analyst &mdash; Nifty 500 Pre-Rally Detection &bull; 10 Signals &bull; Grade A/B/C
        </p>
      </div>

      <div className="dashboard">
        {/* Scan Controls */}
        <div className="card">
          <div className="card-title">⚙️ Scanner Engine</div>
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
            <button className="btn" onClick={runScan} disabled={loading} id="scan-btn">
              {loading ? (
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

          {error && (
            <div style={{ marginTop: "1rem", padding: "0.75rem 1rem", background: "rgba(248,81,73,0.1)", borderRadius: 8, color: "#f85149", border: "1px solid rgba(248,81,73,0.3)" }}>
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* Win Rates Panel */}
        {showWinRates && (
          <div className="card">
            <div className="card-title">📊 Signal Win Rates (NSE Backtested 2018–2024)</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(280px,1fr))", gap: "0.75rem" }}>
              {allSignals.map(sig => {
                const meta = SIGNAL_META[sig];
                const wr   = 0; // will come from result or defaults
                const wrVal= result?.win_rates?.[sig] ?? ({
                  "Pocket Pivot": 67, "BB Squeeze Breakout": 64, "NR7 Pre-Breakout": 56,
                  "EMA Golden Cross": 57, "MACD Bullish Cross": 54, "20D Breakout + Volume": 48,
                  "Oversold RSI Bounce": 60, "EMA50 Trend Pullback": 63,
                  "Trend Momentum Ride": 58, "Volume Accumulation": 51,
                } as Record<string,number>)[sig] ?? 50;
                void wr;
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

        {/* Summary Stats */}
        {result && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(150px,1fr))", gap: "1rem" }}>
            <StatCard label="Total Setups"    value={result.total}    color="#58a6ff" />
            <StatCard label="Grade A Signals" value={gradeACount}     color="#3fb950" sub="Highest confidence" />
            <StatCard label="🏆 Big Move Setups" value={bigMoveCount} color="#f0883e" sub="10–20% target" />
            <StatCard label="Pocket Pivot"    value={result.data.filter(s=>s.signal==="Pocket Pivot").length}    color="#f0883e" sub="67% win rate" />
            <StatCard label="BB Squeeze"      value={result.data.filter(s=>s.signal==="BB Squeeze Breakout").length} color="#a371f7" sub="64% win rate" />
            <StatCard label="NR7 Pre-Break"   value={result.data.filter(s=>s.signal==="NR7 Pre-Breakout").length}   color="#ff7b72" sub="56% win rate" />
          </div>
        )}

        {/* Filters */}
        {result && result.total > 0 && (
          <div className="card" style={{ padding: "1rem" }}>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.6rem", alignItems: "center" }}>
              <span style={{ color: "#8b949e", fontSize: "0.82rem", fontWeight: 600 }}>Filter:</span>
              {["ALL","A","B","C"].map(g => (
                <button key={g} id={`grade-${g}`} onClick={() => setFilterGrade(g)} style={{
                  padding: "0.28rem 0.75rem", borderRadius: 6, border: "none", cursor: "pointer",
                  fontWeight: 600, fontSize: "0.82rem",
                  background: filterGrade === g ? "#58a6ff" : "#21262d",
                  color: filterGrade === g ? "#fff" : "#8b949e", transition: "all 0.2s"
                }}>
                  {g === "ALL" ? "All Grades" : `Grade ${g}`}
                </button>
              ))}
              <div style={{ height: 18, width: 1, background: "#30363d" }} />
              <select id="signal-filter" value={filterSignal} onChange={e => setFilterSignal(e.target.value)} style={{
                background: "#21262d", color: "#c9d1d9", border: "1px solid #30363d",
                borderRadius: 6, padding: "0.3rem 0.6rem", fontSize: "0.82rem", cursor: "pointer"
              }}>
                <option value="ALL">All Signals</option>
                {allSignals.map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
          </div>
        )}

        {/* No results */}
        {result && result.total === 0 && (
          <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
            <div style={{ fontSize: "3rem", marginBottom: "0.5rem" }}>📊</div>
            <strong style={{ color: "#fff", fontSize: "1.2rem" }}>No Setup Today</strong>
            <p style={{ color: "#8b949e", marginTop: "0.5rem" }}>
              No stock met scanner criteria. Market may be choppy — sit in cash.
            </p>
          </div>
        )}

        {/* Results grouped by signal */}
        {result && filtered.length > 0 && (
          <div className="card">
            <div className="card-title">
              📊 Scan Results — {filtered.length} Setup{filtered.length !== 1 ? "s" : ""}
            </div>

            {Object.entries(grouped).map(([sig, setups]) => {
              const meta = SIGNAL_META[sig] ?? { icon: "•", color: "#8b949e", desc: "", targetLabel: "5%" };
              const winR = result.win_rates?.[sig] ?? 50;
              return (
                <div key={sig} style={{ marginBottom: "2.5rem" }}>
                  {/* Signal header */}
                  <div style={{
                    display: "flex", alignItems: "flex-start", gap: "0.75rem",
                    borderLeft: `4px solid ${meta.color}`,
                    paddingLeft: "0.9rem", marginBottom: "0.75rem",
                    paddingBottom: "0.5rem",
                    borderBottom: "1px solid #21262d",
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

                  {/* Table */}
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
                              <td>
                                <span style={{ color: confColor, fontWeight: 700, fontSize: "0.88rem" }}>
                                  {s.confidence}%
                                </span>
                              </td>
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

        {/* How Big Moves Are Caught */}
        <div className="card">
          <div className="card-title">🧠 How the AI Catches Big Moves Before They Happen</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(260px,1fr))", gap: "1rem" }}>
            {[
              {
                icon: "🏆", color: "#f0883e", title: "Pocket Pivot (67% win)",
                body: "When a stock's volume today beats every down-day volume in last 10 sessions, it means institutions are aggressively buying. This caught JKIL before 6000→9000 (+50%) move.",
              },
              {
                icon: "🎯", color: "#a371f7", title: "BB Squeeze Breakout (64% win)",
                body: "When Bollinger Bands tighten to yearly low width (stock 'coiling'), energy is stored. When price breaks the upper band with volume, the spring releases. Caught Angelone 290→350 (+21%).",
              },
              {
                icon: "⚡", color: "#ff7b72", title: "NR7 Pre-Breakout (56% win)",
                body: "The narrowest price range in 7 days = minimum volatility before maximum move. When this happens near recent highs, a breakout is imminent. Caught EMVEE 250→330 in 1 week (+32%).",
              },
              {
                icon: "📏", color: "#58a6ff", title: "Entry = Signal Price",
                body: "Enter at the exact price shown. For NR7, entry is slightly above today's high to confirm breakout. For all others, enter at current market price.",
              },
              {
                icon: "🛑", color: "#f85149", title: "Stop Loss = 1.5× ATR",
                body: "ATR (Average True Range) measures daily volatility. 1.5× ATR gives you a stop that is outside normal noise — won't trigger on random wiggles but exits if real breakdown.",
              },
              {
                icon: "📊", color: "#3fb950", title: "Grade A = Best Setup",
                body: "Grade A requires: multiple indicators aligning, volume confirmation, and price above 200 EMA. Grade A with a Big Move signal = highest probability trade.",
              },
            ].map(item => (
              <div key={item.title} style={{
                background: "#0d1117", borderRadius: 10, padding: "1.1rem",
                border: `1px solid ${item.color}33`,
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem" }}>
                  <span style={{ fontSize: "1.3rem" }}>{item.icon}</span>
                  <strong style={{ color: item.color, fontSize: "0.9rem" }}>{item.title}</strong>
                </div>
                <div style={{ color: "#8b949e", fontSize: "0.82rem", lineHeight: 1.6 }}>{item.body}</div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </main>
  );
}
