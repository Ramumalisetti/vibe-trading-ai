"use client";

import { useState } from "react";

type Setup = {
  signal: string;
  grade: "A" | "B" | "C";
  confidence: number;
  stock: string;
  entry: number;
  sl: number;
  target: number;
  risk_pct: number;
  rr: number;
  reason: string;
};

type ScanResult = {
  status: string;
  total: number;
  target: string;
  data: Setup[];
};

const SIGNAL_META: Record<string, { icon: string; color: string; desc: string }> = {
  "EMA Golden Cross": {
    icon: "✨",
    color: "#58a6ff",
    desc: "EMA 9 crossed above EMA 21 today — fresh momentum entry with trend confirmation.",
  },
  "MACD Bullish Cross": {
    icon: "⚡",
    color: "#a371f7",
    desc: "MACD line crossed above signal line — institutional momentum confirmed.",
  },
  "20D Breakout + Volume": {
    icon: "🚀",
    color: "#f0883e",
    desc: "Price broke 20-day high with 1.5x+ volume surge — classic institutional breakout.",
  },
  "Oversold RSI Bounce": {
    icon: "🎯",
    color: "#2ea043",
    desc: "RSI below 38 and bouncing in an uptrend — quality dip-buy opportunity.",
  },
  "EMA50 Trend Pullback": {
    icon: "📉",
    color: "#39d353",
    desc: "Pulled back to 50 EMA support in strong trend — buy the dip.",
  },
  "Trend Momentum Ride": {
    icon: "🔥",
    color: "#f78166",
    desc: "RSI 55-72, ADX > 28, above all EMAs — momentum continuation setup.",
  },
  "Volume Accumulation": {
    icon: "📦",
    color: "#d2a679",
    desc: "3-day volume surge with tight price range — institutional accumulation before breakout.",
  },
};

const GRADE_STYLE: Record<string, { bg: string; text: string; label: string }> = {
  A: { bg: "rgba(46,160,67,0.15)",  text: "#2ea043", label: "Grade A" },
  B: { bg: "rgba(88,166,255,0.12)", text: "#58a6ff", label: "Grade B" },
  C: { bg: "rgba(139,148,158,0.15)",text: "#8b949e", label: "Grade C" },
};

function ConfidencePill({ conf }: { conf: number }) {
  const color = conf >= 75 ? "#2ea043" : conf >= 63 ? "#f0883e" : "#8b949e";
  return (
    <span style={{
      background: `${color}22`,
      color,
      padding: "0.2rem 0.55rem",
      borderRadius: 6,
      fontWeight: 700,
      fontSize: "0.82rem",
      letterSpacing: "0.02em",
    }}>
      {conf}%
    </span>
  );
}

function RRPill({ rr }: { rr: number }) {
  const color = rr >= 2 ? "#2ea043" : rr >= 1.5 ? "#f0883e" : "#8b949e";
  return (
    <span style={{ color, fontWeight: 700, fontSize: "0.95rem" }}>
      1 : {rr.toFixed(2)}
    </span>
  );
}

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [filterGrade, setFilterGrade] = useState<string>("ALL");
  const [filterSignal, setFilterSignal] = useState<string>("ALL");

  const runScan = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const isLocal =
        typeof window !== "undefined" &&
        window.location.hostname === "localhost";
      const url = isLocal ? "http://localhost:5000" : "/api/scan";
      const res = await fetch(url);
      const json = await res.json();
      if (json.status === "success") {
        setResult(json);
      } else {
        setError(json.error || "Scan failed. Check backend.");
      }
    } catch {
      setError(
        "Could not connect to scanner. Ensure run_local_api.py is running locally."
      );
    }
    setLoading(false);
  };

  const allSignals = Object.keys(SIGNAL_META);

  const filtered = result?.data.filter((s) => {
    const gMatch = filterGrade === "ALL" || s.grade === filterGrade;
    const sMatch = filterSignal === "ALL" || s.signal === filterSignal;
    return gMatch && sMatch;
  }) ?? [];

  // Group by signal
  const grouped = allSignals.reduce<Record<string, Setup[]>>((acc, sig) => {
    const group = filtered.filter((s) => s.signal === sig);
    if (group.length > 0) acc[sig] = group;
    return acc;
  }, {});

  const gradeA = result?.data.filter((s) => s.grade === "A").length ?? 0;
  const gradeB = result?.data.filter((s) => s.grade === "B").length ?? 0;

  return (
    <main className="container">
      {/* Header */}
      <div className="header">
        <h1>Vibe Trading AI</h1>
        <p>Nifty 500 Multi-Strategy Scanner &mdash; 5% Target &bull; ATR Stop Loss &bull; Entry Price</p>
      </div>

      <div className="dashboard">
        {/* Scan Controls */}
        <div className="card">
          <div className="card-title">
            <span>⚙️ Scanner Controls</span>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem", alignItems: "center", marginBottom: "1rem" }}>
            <div style={{ flex: 1, minWidth: 220 }}>
              <div style={{ color: "#8b949e", fontSize: "0.85rem", marginBottom: "0.4rem" }}>Target</div>
              <div style={{
                fontSize: "2rem", fontWeight: 800,
                background: "linear-gradient(90deg, #2ea043, #58a6ff)",
                WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent"
              }}>5% Fixed</div>
            </div>
            <div style={{ flex: 1, minWidth: 220 }}>
              <div style={{ color: "#8b949e", fontSize: "0.85rem", marginBottom: "0.4rem" }}>Universe</div>
              <div style={{ fontSize: "1.2rem", fontWeight: 700, color: "#fff" }}>Nifty 500 Stocks</div>
            </div>
            <div style={{ flex: 1, minWidth: 220 }}>
              <div style={{ color: "#8b949e", fontSize: "0.85rem", marginBottom: "0.4rem" }}>Stop Loss</div>
              <div style={{ fontSize: "1.2rem", fontWeight: 700, color: "#f85149" }}>1.5× ATR (Dynamic)</div>
            </div>
            <div style={{ flex: 1, minWidth: 220 }}>
              <div style={{ color: "#8b949e", fontSize: "0.85rem", marginBottom: "0.4rem" }}>Strategies</div>
              <div style={{ fontSize: "1.2rem", fontWeight: 700, color: "#a371f7" }}>7 Signals</div>
            </div>
          </div>

          <button className="btn" onClick={runScan} disabled={loading} id="scan-btn">
            {loading ? (
              <>
                <svg className="spinner" viewBox="0 0 50 50">
                  <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" strokeWidth="5"
                    strokeDasharray="31.4 31.4" strokeLinecap="round" />
                </svg>
                Scanning Nifty 500...
              </>
            ) : (
              "🚀 Run Scanner"
            )}
          </button>
          {error && (
            <div style={{
              marginTop: "1rem", padding: "0.75rem 1rem",
              background: "rgba(248,81,73,0.1)", borderRadius: 8,
              color: "#f85149", border: "1px solid rgba(248,81,73,0.3)"
            }}>
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* Summary Stats */}
        {result && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "1rem" }}>
            {[
              { label: "Total Setups", value: result.total, color: "#58a6ff" },
              { label: "Grade A Signals", value: gradeA, color: "#2ea043" },
              { label: "Grade B Signals", value: gradeB, color: "#f0883e" },
              { label: "Fixed Target", value: result.target, color: "#a371f7" },
              { label: "Min R:R Shown", value: "1.2+", color: "#d2a679" },
            ].map((s) => (
              <div key={s.label} className="card" style={{ padding: "1rem", textAlign: "center" }}>
                <div style={{ color: "#8b949e", fontSize: "0.78rem", marginBottom: "0.25rem", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                  {s.label}
                </div>
                <div style={{ fontSize: "2rem", fontWeight: 800, color: s.color }}>{s.value}</div>
              </div>
            ))}
          </div>
        )}

        {/* Filters */}
        {result && result.total > 0 && (
          <div className="card" style={{ padding: "1rem" }}>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", alignItems: "center" }}>
              <span style={{ color: "#8b949e", fontSize: "0.85rem", fontWeight: 600 }}>Filter:</span>
              {["ALL", "A", "B", "C"].map((g) => (
                <button key={g} onClick={() => setFilterGrade(g)} id={`grade-${g}`}
                  style={{
                    padding: "0.3rem 0.8rem", borderRadius: 6, border: "none", cursor: "pointer",
                    fontWeight: 600, fontSize: "0.85rem",
                    background: filterGrade === g ? "#58a6ff" : "#21262d",
                    color: filterGrade === g ? "#fff" : "#8b949e",
                    transition: "all 0.2s"
                  }}>
                  {g === "ALL" ? "All Grades" : `Grade ${g}`}
                </button>
              ))}
              <div style={{ height: 20, width: 1, background: "#30363d" }} />
              <select
                id="signal-filter"
                value={filterSignal}
                onChange={(e) => setFilterSignal(e.target.value)}
                style={{
                  background: "#21262d", color: "#c9d1d9", border: "1px solid #30363d",
                  borderRadius: 6, padding: "0.3rem 0.6rem", fontSize: "0.85rem", cursor: "pointer"
                }}
              >
                <option value="ALL">All Signals</option>
                {allSignals.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* No results */}
        {result && result.total === 0 && (
          <div className="card" style={{ textAlign: "center", padding: "3rem" }}>
            <div style={{ fontSize: "3rem", marginBottom: "0.5rem" }}>📊</div>
            <strong style={{ color: "#fff", fontSize: "1.2rem" }}>No Trade Day</strong>
            <p style={{ color: "#8b949e", marginTop: "0.5rem" }}>
              No stocks met the criteria today. Market may be choppy — sit in cash.
            </p>
          </div>
        )}

        {/* Results — grouped by signal */}
        {result && filtered.length > 0 && (
          <div className="card">
            <div className="card-title">
              <span>📊 Scanner Results — {filtered.length} Setup{filtered.length !== 1 ? "s" : ""} Found</span>
            </div>

            {Object.entries(grouped).map(([sig, setups]) => {
              const meta = SIGNAL_META[sig] ?? { icon: "•", color: "#8b949e", desc: "" };
              return (
                <div key={sig} style={{ marginBottom: "2.5rem" }}>
                  {/* Signal header */}
                  <div style={{
                    display: "flex", alignItems: "center", gap: "0.75rem",
                    borderLeft: `4px solid ${meta.color}`,
                    paddingLeft: "0.9rem", marginBottom: "0.75rem",
                  }}>
                    <span style={{ fontSize: "1.4rem" }}>{meta.icon}</span>
                    <div>
                      <h3 style={{ color: "#fff", margin: 0, fontSize: "1.05rem" }}>{sig}</h3>
                      <p style={{ color: "#8b949e", fontSize: "0.82rem", margin: 0 }}>{meta.desc}</p>
                    </div>
                    <span style={{
                      marginLeft: "auto",
                      background: `${meta.color}22`, color: meta.color,
                      padding: "0.2rem 0.6rem", borderRadius: 6,
                      fontSize: "0.8rem", fontWeight: 700
                    }}>
                      {setups.length} stock{setups.length !== 1 ? "s" : ""}
                    </span>
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
                          <th>Target ₹ (5%)</th>
                          <th>Risk %</th>
                          <th>R : R</th>
                          <th>Reason</th>
                        </tr>
                      </thead>
                      <tbody>
                        {setups.map((s) => {
                          const gs = GRADE_STYLE[s.grade] ?? GRADE_STYLE["C"];
                          const isA = s.grade === "A";
                          return (
                            <tr key={`${sig}-${s.stock}`} style={isA ? { background: "rgba(46,160,67,0.04)" } : {}}>
                              <td>
                                <strong style={{ color: isA ? "#2ea043" : "#e6edf3", fontSize: "1rem" }}>
                                  {isA ? "★ " : ""}{s.stock}
                                </strong>
                              </td>
                              <td>
                                <span style={{
                                  background: gs.bg, color: gs.text,
                                  padding: "0.2rem 0.55rem", borderRadius: 6,
                                  fontWeight: 700, fontSize: "0.82rem"
                                }}>
                                  {gs.label}
                                </span>
                              </td>
                              <td><ConfidencePill conf={s.confidence} /></td>
                              <td style={{ fontWeight: 600, color: "#e6edf3" }}>₹{s.entry.toFixed(2)}</td>
                              <td>
                                <span className="badge-danger">₹{s.sl.toFixed(2)}</span>
                              </td>
                              <td>
                                <span className="badge-success">₹{s.target.toFixed(2)}</span>
                              </td>
                              <td style={{ color: "#f85149", fontWeight: 600 }}>{s.risk_pct.toFixed(2)}%</td>
                              <td><RRPill rr={s.rr} /></td>
                              <td style={{ color: "#8b949e", fontSize: "0.82rem", maxWidth: 260 }}>{s.reason}</td>
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

        {/* How to Trade */}
        <div className="card">
          <div className="card-title"><span>📖 How to Use This Scanner</span></div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(220px,1fr))", gap: "1.25rem" }}>
            {[
              { icon: "✅", title: "Buy at Entry ₹", body: "Place a market or limit buy at the Entry price shown." },
              { icon: "🛑", title: "Stop Loss ₹", body: "Exit immediately if price falls to Stop Loss (1.5× ATR below entry)." },
              { icon: "🎯", title: "Target ₹ (5%)", body: "Book profits when price hits Target — always 5% above Entry." },
              { icon: "⭐", title: "Grade A = Best", body: "Grade A signals have the strongest confluence of indicators. Prioritise these." },
              { icon: "📊", title: "R:R Ratio", body: "Prefer trades with R:R ≥ 1.5. Higher = better reward for risk taken." },
              { icon: "⏰", title: "Trade Timing", body: "Enter during market hours. Verify price at time of entry before trading." },
            ].map((item) => (
              <div key={item.title} style={{
                background: "#0d1117", borderRadius: 8, padding: "1rem",
                border: "1px solid #21262d"
              }}>
                <div style={{ fontSize: "1.4rem", marginBottom: "0.4rem" }}>{item.icon}</div>
                <div style={{ color: "#fff", fontWeight: 700, marginBottom: "0.3rem" }}>{item.title}</div>
                <div style={{ color: "#8b949e", fontSize: "0.85rem" }}>{item.body}</div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </main>
  );
}
