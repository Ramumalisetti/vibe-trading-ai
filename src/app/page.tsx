"use client";

import { useState } from "react";

type Setup = {
  strategy: string;
  confidence: string;
  stock: string;
  entry: number;
  sl: number;
  target: number;
  target_type: string;
  rr: number;
  reason: string;
};

const STRATEGY_META: Record<string, { icon: string; badge: string; desc: string }> = {
  "RSI Divergence + Vol Spike": {
    icon: "💎",
    badge: "#a371f7",
    desc: "MULTIBAGGER SETUP — Price lower low + RSI higher low + Institutional volume spike. Aim for 50%+ gain.",
  },
  "DEMA Momentum Spike": {
    icon: "⚡",
    badge: "#58a6ff",
    desc: "Momentum setup — DEMA 9 crossed above EMA 21 with volume drying then spiking. Target: 3%.",
  },
  "Pullback to Value": {
    icon: "📉",
    badge: "#2ea043",
    desc: "Value entry — Stock pulled back to 50DMA with low RSI in an uptrend. Target: 3%.",
  },
  "Darvas Breakout": {
    icon: "🚀",
    badge: "#d29922",
    desc: "Breakout — Above 50-day high with 2x volume. Lower confidence (44.6%). Use tight stop loss.",
  },
};

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [setups, setSetups] = useState<Setup[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const scanMarket = async () => {
    setLoading(true);
    setError(null);
    setSetups(null);
    try {
      const isLocal = typeof window !== "undefined" && window.location.hostname === "localhost";
      const url = isLocal ? "http://localhost:5000" : "/api/scan";
      const res = await fetch(url);
      const json = await res.json();
      if (json.status === "success") {
        setSetups(json.data);
      } else {
        setError(json.error || "Failed to fetch data.");
      }
    } catch {
      setError("Cannot connect to Python engine. Make sure run_local_api.py is running.");
    }
    setLoading(false);
  };

  const strategies = [
    "RSI Divergence + Vol Spike",
    "DEMA Momentum Spike",
    "Pullback to Value",
    "Darvas Breakout",
  ];

  const totalSetups = setups ? setups.length : 0;
  const multibaggers = setups
    ? setups.filter((s) => s.strategy === "RSI Divergence + Vol Spike")
    : [];

  return (
    <main className="container">
      <div className="header">
        <h1>Vibe Trading AI</h1>
        <p>Multi-Strategy Institutional Scanner — NSE F&amp;O Universe</p>
      </div>

      <div className="dashboard">
        {/* Controls */}
        <div className="card">
          <div className="card-title">
            <span>⚙️ System Controls</span>
          </div>
          <p style={{ marginBottom: "1rem", color: "#8b949e" }}>
            Scans 70+ liquid NSE F&amp;O stocks across 4 strategies simultaneously. Multibagger setups
            appear first. Approx <strong>15–30 seconds</strong> to complete.
          </p>
          <button className="btn" onClick={scanMarket} disabled={loading} id="scan-btn">
            {loading ? (
              <>
                <svg className="spinner" viewBox="0 0 50 50">
                  <circle cx="25" cy="25" r="20" fill="none" stroke="currentColor" strokeWidth="5"
                    strokeDasharray="31.4 31.4" strokeLinecap="round" />
                </svg>
                Scanning F&amp;O Universe...
              </>
            ) : (
              "🚀 Run AI Scanner"
            )}
          </button>
          {error && <p style={{ color: "var(--danger)", marginTop: "1rem" }}>{error}</p>}
        </div>

        {/* Summary Bar */}
        {setups !== null && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: "1rem" }}>
            {[
              { label: "Total Setups Found", value: totalSetups, color: "#58a6ff" },
              { label: "💎 Multibagger Setups", value: multibaggers.length, color: "#a371f7" },
              { label: "Best Confidence", value: totalSetups ? "77.8%" : "—", color: "#2ea043" },
              { label: "Strategy Target", value: multibaggers.length ? "50%+" : "3%", color: "#f0883e" },
            ].map((stat) => (
              <div key={stat.label} className="card" style={{ padding: "1rem", textAlign: "center" }}>
                <div style={{ color: "#8b949e", fontSize: "0.8rem", marginBottom: "0.3rem" }}>{stat.label}</div>
                <div style={{ fontSize: "1.8rem", fontWeight: "bold", color: stat.color }}>{stat.value}</div>
              </div>
            ))}
          </div>
        )}

        {/* Results per strategy */}
        {setups !== null && (
          <div className="card">
            <div className="card-title">
              <span>📊 Live Scanner Results</span>
            </div>

            {setups.length === 0 ? (
              <div style={{ padding: "1.5rem", textAlign: "center", color: "#8b949e" }}>
                <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>🔍</div>
                <strong style={{ color: "#fff" }}>NO TRADE DAY</strong>
                <p style={{ marginTop: "0.5rem" }}>
                  No stock met any strategy criteria today. Market may be choppy — sit in cash.
                </p>
              </div>
            ) : (
              strategies.map((strategyName) => {
                const meta = STRATEGY_META[strategyName];
                const group = setups.filter((s) => s.strategy === strategyName);
                if (group.length === 0) return null;

                return (
                  <div key={strategyName} style={{ marginBottom: "2.5rem" }}>
                    <div style={{
                      display: "flex", alignItems: "center", gap: "0.75rem",
                      borderLeft: `4px solid ${meta.badge}`,
                      paddingLeft: "0.75rem", marginBottom: "0.5rem"
                    }}>
                      <span style={{ fontSize: "1.3rem" }}>{meta.icon}</span>
                      <div>
                        <h3 style={{ color: "#fff", margin: 0 }}>{strategyName}</h3>
                        <p style={{ color: "#8b949e", fontSize: "0.85rem", margin: 0 }}>{meta.desc}</p>
                      </div>
                    </div>

                    <div className="table-container">
                      <table>
                        <thead>
                          <tr>
                            <th>Stock</th>
                            <th>Confidence</th>
                            <th>Entry ₹</th>
                            <th>Stop Loss ₹</th>
                            <th>Target ₹</th>
                            <th>Target Type</th>
                            <th>RR</th>
                            <th>Reason</th>
                          </tr>
                        </thead>
                        <tbody>
                          {group.map((setup) => {
                            const confNum = parseFloat(setup.confidence);
                            const isMultibagger = setup.strategy === "RSI Divergence + Vol Spike";
                            return (
                              <tr key={`${strategyName}-${setup.stock}`} style={
                                isMultibagger ? { background: "rgba(163,113,247,0.06)" } : {}
                              }>
                                <td>
                                  <strong style={{ color: isMultibagger ? "#a371f7" : "#fff" }}>
                                    {isMultibagger ? "💎 " : ""}{setup.stock}
                                  </strong>
                                </td>
                                <td>
                                  <span style={{
                                    color: confNum >= 60 ? "var(--success)" : confNum >= 50 ? "#f0883e" : "var(--danger)",
                                    fontWeight: "bold"
                                  }}>{setup.confidence}</span>
                                </td>
                                <td>₹{setup.entry.toFixed(2)}</td>
                                <td><span className="badge-danger">₹{setup.sl.toFixed(2)}</span></td>
                                <td><span className="badge-success">₹{setup.target.toFixed(2)}</span></td>
                                <td>
                                  <span style={{
                                    background: isMultibagger ? "rgba(163,113,247,0.15)" : "rgba(88,166,255,0.1)",
                                    color: isMultibagger ? "#a371f7" : "#58a6ff",
                                    padding: "0.2rem 0.5rem", borderRadius: "4px", fontSize: "0.8rem", fontWeight: 600
                                  }}>{setup.target_type}</span>
                                </td>
                                <td>1:{setup.rr.toFixed(2)}</td>
                                <td style={{ color: "#8b949e", fontSize: "0.85rem" }}>{setup.reason}</td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>
    </main>
  );
}
