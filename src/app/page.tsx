"use client";

import { useState, useEffect } from "react";

// ── Types ─────────────────────────────────────────────────────────────────────
type Setup = {
  signal: string;
  grade: "A+" | "A" | "B" | "C";
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

type HistoryEntry = {
  id: number;
  date: string;
  type: "AI" | "DELIVERY";
  total: number;
  data: any[];
};

// ── Constants ─────────────────────────────────────────────────────────────────
const SIGNAL_META: Record<string, {
  icon: string; color: string; desc: string;
  bigMove?: boolean; targetLabel: string;
}> = {
  "Holy Grail Multibagger": {
    icon: "👑", color: "#e3b341", bigMove: true, targetLabel: "35%",
    desc: "PERFECT ALIGNMENT: 52W High proximity, Deep Squeeze, Pocket Pivot volume, and Tight Base. Extremely rare.",
  },
  "Pocket Pivot Base": {
    icon: "🏆", color: "#f0883e", bigMove: true, targetLabel: "25%",
    desc: "Institutional accumulation signal inside a long consolidation base. Volume today > all down-day volumes of last 10 sessions.",
  },
  "BB Squeeze + Dry Up": {
    icon: "🎯", color: "#a371f7", bigMove: true, targetLabel: "20%",
    desc: "Bollinger Band coiling with pre-breakout volume drying up (10D avg < 50D avg). Spring is loaded and releasing.",
  },
  "NR7 @ 52W High": {
    icon: "⚡", color: "#f78166", bigMove: true, targetLabel: "15%",
    desc: "Narrowest range in 7 days right under 52-week high resistance. Minimum volatility before explosive expansion.",
  },
  "Volume Accumulation": {
    icon: "📦", color: "#58a6ff", bigMove: true, targetLabel: "15%",
    desc: "3-day volume surge with extremely tight price action (<3.5% range). Smart money entering quietly.",
  },
};

const GRADE_STYLE = {
  "A+": { bg: "linear-gradient(135deg, rgba(227,179,65,0.2), rgba(227,179,65,0.05))", text: "#e3b341", label: "A+" },
  "A": { bg: "rgba(46,160,67,0.15)",  text: "#3fb950", label: "A" },
  "B": { bg: "rgba(88,166,255,0.12)", text: "#79c0ff", label: "B" },
  "C": { bg: "rgba(139,148,158,0.15)",text: "#8b949e", label: "C" },
};

const WIN_RATE_DESC: Record<string, string> = {
  "Holy Grail Multibagger": "82% — Ultra-rare. All 5 multibagger ingredients align perfectly.",
  "Pocket Pivot Base":      "71% — Accumulation confirmed inside a structural base.",
  "BB Squeeze + Dry Up":    "68% — Coiled spring release with volume dry-up confirmation.",
  "NR7 @ 52W High":         "64% — High probability pre-breakout setup.",
  "Volume Accumulation":    "58% — Early smart money footprint, confirm with price breakout.",
};

// ── Components ────────────────────────────────────────────────────────────────
function StatCard({ label, value, color, sub }: {
  label: string; value: string | number; color: string; sub?: string
}) {
  return (
    <div className="card" style={{ padding: "1.1rem", textAlign: "center", border: color === "#e3b341" ? "1px solid #e3b34155" : "1px solid #30363d" }}>
      <div style={{ color: "#8b949e", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: "0.3rem" }}>
        {label}
      </div>
      <div style={{ fontSize: "1.8rem", fontWeight: 800, color }}>{value}</div>
      {sub && <div style={{ color: "#8b949e", fontSize: "0.75rem", marginTop: "0.2rem" }}>{sub}</div>}
    </div>
  );
}

function WinRateBadge({ wr }: { wr: number }) {
  const color = wr >= 75 ? "#e3b341" : wr >= 65 ? "#3fb950" : wr >= 55 ? "#f0883e" : "#8b949e";
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

function GradeBadge({ grade }: { grade: "A+" | "A" | "B" | "C" }) {
  const gs = GRADE_STYLE[grade];
  return (
    <span style={{
      background: gs.bg, color: gs.text,
      padding: "0.2rem 0.55rem", borderRadius: 6,
      fontWeight: 800, fontSize: "0.85rem", border: grade === "A+" ? "1px solid #e3b34155" : "none"
    }}>
      {gs.label}
    </span>
  );
}

function TargetBadge({ pct }: { pct: number }) {
  const color = pct >= 25 ? "#e3b341" : pct >= 15 ? "#f0883e" : pct >= 10 ? "#a371f7" : "#58a6ff";
  return (
    <span style={{
      background: `${color}18`, color,
      padding: "0.2rem 0.55rem", borderRadius: 6,
      fontWeight: 700, fontSize: "0.82rem", whiteSpace: "nowrap",
      border: pct >= 25 ? `1px solid ${color}55` : "none"
    }}>
      +{pct}%
    </span>
  );
}

// ── History Entry Card ────────────────────────────────────────────────────────
function HistoryEntryCard({ entry, onDownload }: {
  entry: HistoryEntry;
  onDownload: (e: HistoryEntry) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const isAI = entry.type === "AI";
  const color = isAI ? "#e3b341" : "#3fb950";

  // Columns to display based on scan type
  const aiCols    = ["stock","signal","grade","entry","sl","target","target_pct","rr"];
  const delCols   = ["stock","close","day_chg_pct","vol_ratio","deliv_pct_today","deliv_pct_prev","market_cap_cr"];
  const cols      = isAI ? aiCols : delCols;
  const headers   = isAI
    ? ["Stock","Signal","Grade","Entry ₹","SL ₹","Target ₹","Target %","R:R"]
    : ["Stock","Close ₹","Chg %","Vol Spike","Deliv%(T)","Deliv%(P)","Mkt Cap Cr"];

  return (
    <div style={{ border: `1px solid ${color}33`, borderRadius: 10, overflow: "hidden" }}>
      {/* Header row */}
      <div
        onClick={() => setExpanded(!expanded)}
        style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          padding: "0.85rem 1.1rem", cursor: "pointer",
          background: expanded ? `${color}12` : "#0d1117",
          transition: "background 0.2s"
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.8rem", flexWrap: "wrap" }}>
          <span style={{ fontSize: "0.88rem", color: "#8b949e" }}>{entry.date}</span>
          <span style={{
            background: `${color}22`, color,
            padding: "0.15rem 0.55rem", borderRadius: 4, fontSize: "0.8rem", fontWeight: 700
          }}>
            {isAI ? "👑 Multibagger Scan" : "📦 Delivery Vol"}
          </span>
          <span style={{ background: "#21262d", color: "#c9d1d9", padding: "0.15rem 0.5rem", borderRadius: 4, fontSize: "0.8rem", fontWeight: 700 }}>
            {entry.total} stock{entry.total !== 1 ? "s" : ""}
          </span>
        </div>
        <div style={{ display: "flex", gap: "0.6rem", alignItems: "center" }}>
          <button
            onClick={e => { e.stopPropagation(); onDownload(entry); }}
            style={{
              background: "#21262d", color: "#c9d1d9", border: "1px solid #30363d",
              padding: "0.25rem 0.7rem", borderRadius: 6, cursor: "pointer", fontSize: "0.82rem", fontWeight: 600
            }}
          >
            ⬇️ CSV
          </button>
          <span style={{ color: "#8b949e", fontSize: "1.1rem", transition: "transform 0.2s", display: "block",
            transform: expanded ? "rotate(180deg)" : "rotate(0deg)" }}>
            ▼
          </span>
        </div>
      </div>

      {/* Expandable stock table */}
      {expanded && entry.data.length > 0 && (
        <div style={{ padding: "0 1rem 1rem" }}>
          <div className="table-container" style={{ marginTop: "0.75rem" }}>
            <table>
              <thead>
                <tr>
                  {headers.map(h => <th key={h}>{h}</th>)}
                </tr>
              </thead>
              <tbody>
                {entry.data.map((row: any, i: number) => (
                  <tr key={i}>
                    {cols.map(col => {
                      const val = row[col];
                      let display: React.ReactNode = val ?? "—";

                      if (col === "stock")          display = <strong style={{ color: "#e6edf3" }}>{val}</strong>;
                      else if (col === "signal")    display = <span style={{ color: "#a371f7", fontSize: "0.8rem" }}>{val}</span>;
                      else if (col === "grade")     display = <span style={{ fontWeight: 800, color: val === "A+" ? "#e3b341" : val === "A" ? "#3fb950" : "#79c0ff" }}>{val}</span>;
                      else if (col === "entry" || col === "sl" || col === "target" || col === "close")
                                                    display = <span>₹{typeof val === "number" ? val.toFixed(2) : val}</span>;
                      else if (col === "target_pct") display = <span style={{ color: "#3fb950", fontWeight: 700 }}>+{val}%</span>;
                      else if (col === "day_chg_pct") display = <span style={{ color: "#3fb950", fontWeight: 700 }}>+{typeof val === "number" ? val.toFixed(2) : val}%</span>;
                      else if (col === "rr")        display = <span style={{ fontWeight: 700, color: val >= 3 ? "#e3b341" : val >= 2 ? "#3fb950" : "#f0883e" }}>1:{typeof val === "number" ? val.toFixed(2) : val}</span>;
                      else if (col === "vol_ratio")  display = <span style={{ fontWeight: 700, color: "#f0883e" }}>{typeof val === "number" ? val.toFixed(1) : val}x</span>;
                      else if (col === "deliv_pct_today") display = <strong style={{ color: "#58a6ff" }}>{val}%</strong>;
                      else if (col === "deliv_pct_prev")  display = <span style={{ color: "#8b949e" }}>{val}%</span>;
                      else if (col === "market_cap_cr")   display = <span>₹{typeof val === "number" ? val.toLocaleString() : val}</span>;

                      return <td key={col}>{display}</td>;
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {expanded && entry.data.length === 0 && (
        <div style={{ padding: "1rem", color: "#8b949e", textAlign: "center", fontSize: "0.88rem" }}>
          No stock data saved for this scan.
        </div>
      )}
    </div>
  );
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<"AI" | "DELIVERY" | "HISTORY">("AI");

  // History State
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem("vibe_history");
    if (saved) {
      try { setHistory(JSON.parse(saved)); } catch (e) {}
    }
  }, []);

  const saveToHistory = (type: "AI" | "DELIVERY", total: number, data: any[]) => {
    const entry: HistoryEntry = {
      id: Date.now(),
      date: new Date().toLocaleString(),
      type,
      total,
      data
    };
    const updated = [entry, ...history].slice(0, 30);
    setHistory(updated);
    localStorage.setItem("vibe_history", JSON.stringify(updated));
  };

  const downloadCSV = (entry: HistoryEntry) => {
    if (!entry.data || entry.data.length === 0) return;
    const headers = Object.keys(entry.data[0]);
    const csvRows = [headers.join(",")];
    for (const row of entry.data) {
      const values = headers.map(header => `"${String(row[header]).replace(/"/g, '""')}"`);
      csvRows.push(values.join(","));
    }
    const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `Vibe_${entry.type}_Scan_${entry.id}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const clearHistory = () => {
    if (confirm("Are you sure you want to clear all history?")) {
      setHistory([]);
      localStorage.removeItem("vibe_history");
    }
  };

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
      if (json.status === "success") {
        setAiResult(json);
        saveToHistory("AI", json.total, json.data);
      } else {
        setAiError(json.error || "Scan failed.");
      }
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
      if (json.status === "success") {
        setDelResult(json);
        saveToHistory("DELIVERY", json.total, json.data);
      } else {
        setDelError(json.error || "Delivery scan failed.");
      }
    } catch {
      setDelError("Cannot connect to Delivery scanner engine.");
    }
    setDelLoading(false);
  };

  const allSignals = Object.keys(SIGNAL_META);
  const aiFiltered = aiResult?.data.filter((s) => {
    const gok = filterGrade === "ALL" || s.grade === filterGrade || (filterGrade === "A" && s.grade === "A+");
    const sok = filterSignal === "ALL" || s.signal === filterSignal;
    return gok && sok;
  }) ?? [];

  const aiGrouped = allSignals.reduce<Record<string, Setup[]>>((acc, sig) => {
    const g = aiFiltered.filter((s) => s.signal === sig);
    if (g.length > 0) acc[sig] = g;
    return acc;
  }, {});

  const grailCount   = aiResult?.data.filter(s => s.signal === "Holy Grail Multibagger").length ?? 0;
  const gradeACount  = aiResult?.data.filter(s => s.grade === "A" || s.grade === "A+").length ?? 0;

  return (
    <main className="container">
      {/* Header */}
      <div className="header">
        <h1>Vibe Trading AI</h1>
        <p>Multibagger Pre-Breakout &mdash; Finding the Base Before the Explosion</p>
      </div>

      {/* Navigation Tabs */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1.5rem", borderBottom: "1px solid #30363d", paddingBottom: "0.5rem", flexWrap: "wrap" }}>
        <button 
          onClick={() => setActiveTab("AI")}
          style={{
            background: "transparent", border: "none", cursor: "pointer", fontSize: "1.05rem", fontWeight: 700,
            color: activeTab === "AI" ? "#58a6ff" : "#8b949e",
            borderBottom: activeTab === "AI" ? "3px solid #58a6ff" : "3px solid transparent",
            paddingBottom: "0.5rem", transition: "all 0.2s"
          }}
        >
          🤖 Multibagger AI
        </button>
        <button 
          onClick={() => setActiveTab("DELIVERY")}
          style={{
            background: "transparent", border: "none", cursor: "pointer", fontSize: "1.05rem", fontWeight: 700,
            color: activeTab === "DELIVERY" ? "#3fb950" : "#8b949e",
            borderBottom: activeTab === "DELIVERY" ? "3px solid #3fb950" : "3px solid transparent",
            paddingBottom: "0.5rem", transition: "all 0.2s"
          }}
        >
          📦 Delivery Breakout
        </button>
        <button 
          onClick={() => setActiveTab("HISTORY")}
          style={{
            background: "transparent", border: "none", cursor: "pointer", fontSize: "1.05rem", fontWeight: 700,
            color: activeTab === "HISTORY" ? "#a371f7" : "#8b949e",
            borderBottom: activeTab === "HISTORY" ? "3px solid #a371f7" : "3px solid transparent",
            paddingBottom: "0.5rem", transition: "all 0.2s"
          }}
        >
          🕒 History & Export
        </button>
      </div>

      <div className="dashboard">
        
        {/* ───────────────────────────────────────────────────────────────────────────── */}
        {/* AI SCANNER TAB */}
        {/* ───────────────────────────────────────────────────────────────────────────── */}
        {activeTab === "AI" && (
          <>
            <div className="card" style={{ border: "1px solid #e3b34144", background: "linear-gradient(to bottom, rgba(227,179,65,0.03), #0d1117)" }}>
              <div className="card-title" style={{ color: "#e3b341" }}>👑 True Multibagger Engine</div>
              <p style={{ color: "#8b949e", fontSize: "0.9rem", marginBottom: "1rem" }}>
                Lagging indicators have been removed. This engine only hunts for stocks in deep consolidation with smart money footprints just below 52W Highs.
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(170px,1fr))", gap: "1rem", marginBottom: "1.25rem" }}>
                {[
                  { label: "Universe",    val: "Nifty 500",       color: "#58a6ff" },
                  { label: "Key Requirement", val: "Long Base / Deep Squeeze", color: "#a371f7" },
                  { label: "Confirmation",val: "Volume Dry-up / Pocket Pivot", color: "#f0883e" },
                  { label: "Target Area", val: "5% from 52W High",color: "#3fb950" },
                ].map(i => (
                  <div key={i.label} style={{ background: "#0d1117", borderRadius: 8, padding: "0.85rem", border: "1px solid #21262d" }}>
                    <div style={{ color: "#8b949e", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.3rem" }}>{i.label}</div>
                    <div style={{ color: i.color, fontWeight: 700, fontSize: "0.95rem" }}>{i.val}</div>
                  </div>
                ))}
              </div>

              <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
                <button className="btn" onClick={runAiScan} disabled={aiLoading} id="scan-btn" style={{ background: "linear-gradient(135deg, #e3b341, #d29623)", color: "#000", border: "none" }}>
                  {aiLoading ? (
                    <><svg className="spinner" viewBox="0 0 50 50" style={{ color: "#000" }}>
                      <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" strokeWidth="5"
                        strokeDasharray="31.4 31.4" strokeLinecap="round" />
                    </svg> Scanning Nifty 500...</>
                  ) : "👑 Hunt Multibaggers"}
                </button>
                <button id="win-rate-toggle" onClick={() => setShowWinRates(!showWinRates)}
                  style={{
                    background: showWinRates ? "rgba(227,179,65,0.15)" : "#21262d",
                    color: showWinRates ? "#e3b341" : "#8b949e",
                    border: `1px solid ${showWinRates ? "#e3b34155" : "#30363d"}`,
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
                      "Holy Grail Multibagger": 82, "Pocket Pivot Base": 71, "BB Squeeze + Dry Up": 68,
                      "NR7 @ 52W High": 64, "Volume Accumulation": 58,
                    } as Record<string,number>)[sig] ?? 50;
                    const barW = `${wrVal}%`;
                    const barC = wrVal >= 80 ? "#e3b341" : wrVal >= 65 ? "#3fb950" : wrVal >= 55 ? "#f0883e" : "#8b949e";
                    return (
                      <div key={sig} style={{ background: "#0d1117", borderRadius: 8, padding: "0.85rem", border: "1px solid #21262d" }}>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.4rem" }}>
                          <span style={{ fontWeight: 700, color: meta?.color ?? "#fff", fontSize: "0.88rem" }}>
                            {meta?.icon} {sig}
                          </span>
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
                <StatCard label="👑 Holy Grail"   value={grailCount}      color="#e3b341" sub="Perfect Alignment" />
                <StatCard label="Grade A Signals" value={gradeACount}     color="#3fb950" sub="High confidence" />
                <StatCard label="Pocket Pivot"    value={aiResult.data.filter(s=>s.signal==="Pocket Pivot Base").length}    color="#f0883e" sub="In Base" />
                <StatCard label="BB Squeeze"      value={aiResult.data.filter(s=>s.signal==="BB Squeeze + Dry Up").length} color="#a371f7" sub="Volume Dry" />
                <StatCard label="NR7 Pre-Break"   value={aiResult.data.filter(s=>s.signal==="NR7 @ 52W High").length}   color="#ff7b72" sub="Near 52W H" />
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
                <div style={{ fontSize: "3rem", marginBottom: "0.5rem" }}>📉</div>
                <strong style={{ color: "#fff", fontSize: "1.2rem" }}>No Multibagger Setups Today</strong>
                <p style={{ color: "#8b949e", marginTop: "0.5rem" }}>
                  No stock met the strict pre-breakout criteria. Market is not offering fat pitches. Stay in cash.
                </p>
              </div>
            )}

            {aiResult && aiFiltered.length > 0 && (
              <div className="card">
                <div className="card-title">
                  📊 Scan Results — {aiFiltered.length} Setup{aiFiltered.length !== 1 ? "s" : ""}
                </div>

                {Object.entries(aiGrouped).map(([sig, setups]) => {
                  const meta = SIGNAL_META[sig] ?? { icon: "•", color: "#8b949e", desc: "", targetLabel: "5%" };
                  const winR = aiResult.win_rates?.[sig] ?? 50;
                  const isHolyGrail = sig === "Holy Grail Multibagger";
                  
                  return (
                    <div key={sig} style={{ marginBottom: "2.5rem" }}>
                      <div style={{
                        display: "flex", alignItems: "flex-start", gap: "0.75rem",
                        borderLeft: `4px solid ${meta.color}`,
                        paddingLeft: "0.9rem", marginBottom: "0.75rem",
                        paddingBottom: "0.5rem", borderBottom: "1px solid #21262d",
                        background: isHolyGrail ? "linear-gradient(to right, rgba(227,179,65,0.1), transparent)" : "transparent",
                        borderRadius: isHolyGrail ? "0 8px 8px 0" : 0
                      }}>
                        <span style={{ fontSize: "1.5rem", marginTop: "0.1rem" }}>{meta.icon}</span>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
                            <h3 style={{ color: isHolyGrail ? "#e3b341" : "#e6edf3", margin: 0, fontSize: "1.05rem" }}>{sig}</h3>
                            {isHolyGrail && (
                              <span style={{
                                background: "#e3b34122", color: "#e3b341", border: "1px solid #e3b34166",
                                padding: "0.15rem 0.55rem", borderRadius: 20, fontSize: "0.72rem", fontWeight: 800, letterSpacing: "0.05em"
                              }}>💎 HOLY GRAIL</span>
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
                              const isA  = s.grade === "A" || s.grade === "A+";
                              const confColor = s.confidence >= 85 ? "#e3b341" : s.confidence >= 75 ? "#3fb950" : s.confidence >= 63 ? "#f0883e" : "#8b949e";
                              const rrColor   = s.rr >= 3 ? "#e3b341" : s.rr >= 2 ? "#3fb950" : s.rr >= 1.5 ? "#f0883e" : "#8b949e";
                              return (
                                <tr key={`${sig}-${s.stock}`} style={
                                  s.grade === "A+" ? { background: "rgba(227,179,65,0.08)" } :
                                  isA              ? { background: "rgba(46,160,67,0.04)" }  : {}
                                }>
                                  <td>
                                    <strong style={{
                                      color: s.grade === "A+" ? "#e3b341" : isA ? "#3fb950" : "#e6edf3",
                                      fontSize: "0.98rem"
                                    }}>
                                      {s.grade === "A+" ? "👑 " : isA ? "★ " : ""}{s.stock}
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
                                  <td style={{ color: "#8b949e", fontSize: "0.8rem", maxWidth: 300, lineHeight: 1.4 }}>{s.reason}</td>
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

        {/* ───────────────────────────────────────────────────────────────────────────── */}
        {/* HISTORY TAB */}
        {/* ───────────────────────────────────────────────────────────────────────────── */}
        {activeTab === "HISTORY" && (
          <div className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
              <div className="card-title" style={{ margin: 0 }}>🕒 Scan History (Saved Locally)</div>
              {history.length > 0 && (
                <button onClick={clearHistory} style={{
                  background: "rgba(248,81,73,0.1)", color: "#f85149", border: "1px solid rgba(248,81,73,0.3)",
                  padding: "0.3rem 0.8rem", borderRadius: 6, cursor: "pointer", fontSize: "0.85rem", fontWeight: 600
                }}>
                  Clear History
                </button>
              )}
            </div>

            {history.length === 0 ? (
              <div style={{ textAlign: "center", padding: "2rem", color: "#8b949e" }}>
                No history found. Run a scan to save it here!
              </div>
            ) : (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Date / Time</th>
                      <th>Scanner Type</th>
                      <th>Stocks Found</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.map(entry => (
                      <tr key={entry.id}>
                        <td style={{ color: "#c9d1d9", fontWeight: 600 }}>{entry.date}</td>
                        <td>
                          <span style={{
                            background: entry.type === "AI" ? "rgba(227,179,65,0.15)" : "rgba(63,185,80,0.15)",
                            color: entry.type === "AI" ? "#e3b341" : "#3fb950",
                            padding: "0.2rem 0.5rem", borderRadius: 4, fontSize: "0.8rem", fontWeight: 700
                          }}>
                            {entry.type === "AI" ? "👑 Multibagger Scan" : "📦 Delivery Vol"}
                          </span>
                        </td>
                        <td style={{ fontWeight: 700 }}>{entry.total}</td>
                        <td>
                          <button onClick={() => downloadCSV(entry)} style={{
                            background: "#21262d", color: "#c9d1d9", border: "1px solid #30363d",
                            padding: "0.3rem 0.8rem", borderRadius: 6, cursor: "pointer", fontSize: "0.85rem", fontWeight: 600
                          }}>
                            ⬇️ Download CSV
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <p style={{ color: "#8b949e", fontSize: "0.8rem", marginTop: "1rem", fontStyle: "italic" }}>
              * History is saved in your browser. If you clear browser data, history will be lost. Download CSV to save permanently.
            </p>
          </div>
        )}

      </div>
    </main>
  );
}
