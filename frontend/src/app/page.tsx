"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "@/components/Navbar";
import { Sidebar, NavTab } from "@/components/Sidebar";
import { TradingViewChart } from "@/components/TradingViewChart";
import { CalendarHeatmap } from "@/components/CalendarHeatmap";
import { OrderModal } from "@/components/OrderModal";
import {
  api,
  QuoteData,
  CandleData,
  PortfolioSummary,
  ScannerCandidate,
  RecommendationRecord,
  PerformanceSummary,
  HeatmapData,
  BenchmarkComparison,
  AlertItem
} from "@/lib/api";
import {
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  ShieldCheck,
  Bot,
  Radar,
  Award,
  Wallet,
  PieChart,
  Calendar,
  AlertTriangle,
  BookOpen,
  Search,
  CheckCircle,
  ExternalLink,
  ChevronRight,
  Sparkles
} from "lucide-react";

export default function TerminalHome() {
  const [activeTab, setActiveTab] = useState<NavTab>("overview");
  const [activeMode, setActiveMode] = useState<"INVESTMENT" | "TRADING">("INVESTMENT");
  const [isDark, setIsDark] = useState<boolean>(false);
  const [selectedSymbol, setSelectedSymbol] = useState<string>("RELIANCE");

  // Live Data States
  const [indices, setIndices] = useState<QuoteData[]>([]);
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null);
  const [candles, setCandles] = useState<CandleData[]>([]);
  const [technicals, setTechnicals] = useState<any>(null);
  const [financials, setFinancials] = useState<any>(null);
  const [aiAnalysis, setAiAnalysis] = useState<any>(null);
  const [scannerResults, setScannerResults] = useState<ScannerCandidate[]>([]);
  const [activePreset, setActivePreset] = useState<string>("Quality Businesses (Buffett-Style)");
  const [recommendations, setRecommendations] = useState<RecommendationRecord[]>([]);
  const [performance, setPerformance] = useState<PerformanceSummary | null>(null);
  const [heatmapData, setHeatmapData] = useState<HeatmapData | null>(null);
  const [benchmarkData, setBenchmarkData] = useState<BenchmarkComparison | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [lessons, setLessons] = useState<any[]>([]);

  // AI Chat State
  const [chatInput, setChatInput] = useState<string>("");
  const [chatMessages, setChatMessages] = useState<Array<{ sender: "user" | "ai"; text: string }>>([
    {
      sender: "ai",
      text: "Welcome to your Indian Equity AI Research Terminal. Ask me to analyse any NSE/BSE stock, review your portfolio, or find Buffett-style quality businesses."
    }
  ]);

  // Order Ticket Modal
  const [isOrderModalOpen, setIsOrderModalOpen] = useState<boolean>(false);

  // Sync theme
  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [isDark]);

  // Fetch core baseline data
  const refreshPortfolio = () => {
    api.getPortfolioSummary(activeMode).then(setPortfolio).catch(() => {});
    api.getHeatmap(activeMode).then(setHeatmapData).catch(() => {});
    api.getBenchmarks(activeMode).then(setBenchmarkData).catch(() => {});
  };

  useEffect(() => {
    api.getIndices().then(setIndices).catch(() => {});
    refreshPortfolio();
    api.getRecommendations().then(setRecommendations).catch(() => {});
    api.getPerformanceSummary().then(setPerformance).catch(() => {});
    api.getAlerts().then(setAlerts).catch(() => {});
    api.getLearningLessons().then(setLessons).catch(() => {});
  }, [activeMode]);

  // When selected stock changes, fetch stock details & AI analysis
  useEffect(() => {
    api.getCandles(selectedSymbol).then(setCandles).catch(() => {});
    api.getTechnicals(selectedSymbol).then(setTechnicals).catch(() => {});
    api.getFinancials(selectedSymbol).then(setFinancials).catch(() => {});
    api.analyzeStock(selectedSymbol, activeMode).then(setAiAnalysis).catch(() => {});
  }, [selectedSymbol, activeMode]);

  // When scanner preset or mode changes
  useEffect(() => {
    api.runScanner(activeMode, activePreset).then(setScannerResults).catch(() => {});
  }, [activePreset, activeMode]);

  const handleStockClick = (symbol: string) => {
    setSelectedSymbol(symbol);
    setActiveTab("research");
  };

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const userMsg = chatInput;
    setChatMessages((prev) => [...prev, { sender: "user", text: userMsg }]);
    setChatInput("");

    try {
      const res = await api.chatWithAnalyst(userMsg, selectedSymbol, activeMode);
      setChatMessages((prev) => [...prev, { sender: "ai", text: res.reply }]);
    } catch {
      setChatMessages((prev) => [
        ...prev,
        { sender: "ai", text: "Network error connecting to research intelligence service." }
      ]);
    }
  };

  const currentQuote = indices.find((i) => i.symbol === selectedSymbol);
  const currentLtp = currentQuote ? Number(currentQuote.ltp) : (aiAnalysis ? aiAnalysis.cmp : 2485.50);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans">
      <Navbar
        activeMode={activeMode}
        onModeToggle={setActiveMode}
        onSelectStock={handleStockClick}
        isDark={isDark}
        onToggleTheme={() => setIsDark(!isDark)}
        unreadAlertsCount={alerts.filter((a) => !a.is_read).length}
      />

      <div className="max-w-7xl mx-auto flex">
        <Sidebar
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          unreadAlertsCount={alerts.filter((a) => !a.is_read).length}
        />

        <main className="flex-1 p-6 space-y-6 overflow-x-hidden min-w-0">
          {/* ======================================================== */}
          {/* VIEW 1: OVERVIEW DASHBOARD */}
          {/* ======================================================== */}
          {activeTab === "overview" && (
            <div className="space-y-6">
              {/* Portfolio Metrics Google Finance Style */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                  <span className="text-xs text-slate-500 font-medium block">Total Portfolio Value</span>
                  <div className="text-xl font-bold font-mono text-slate-900 dark:text-white mt-1">
                    ₹{portfolio ? portfolio.total_portfolio_value.toLocaleString("en-IN", { minimumFractionDigits: 2 }) : "10,00,000.00"}
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono mt-0.5 block">
                    Cash: ₹{portfolio ? portfolio.cash_balance.toLocaleString("en-IN", { minimumFractionDigits: 2 }) : "10,00,000.00"}
                  </span>
                </div>

                <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                  <span className="text-xs text-slate-500 font-medium block">Total Net Return</span>
                  <div className={`text-xl font-bold font-mono mt-1 ${portfolio && portfolio.total_pnl >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                    {portfolio && portfolio.total_pnl >= 0 ? "+" : ""}₹{portfolio ? portfolio.total_pnl.toLocaleString("en-IN", { minimumFractionDigits: 2 }) : "0.00"}
                  </div>
                  <span className="text-[11px] font-mono text-emerald-600 font-semibold block mt-0.5">
                    {portfolio && portfolio.overall_return_pct >= 0 ? "+" : ""}{portfolio ? portfolio.overall_return_pct.toFixed(2) : "0.00"}% Overall
                  </span>
                </div>

                <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                  <span className="text-xs text-slate-500 font-medium block">Unrealized P&L</span>
                  <div className={`text-xl font-bold font-mono mt-1 ${portfolio && portfolio.unrealized_pnl >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                    {portfolio && portfolio.unrealized_pnl >= 0 ? "+" : ""}₹{portfolio ? portfolio.unrealized_pnl.toLocaleString("en-IN", { minimumFractionDigits: 2 }) : "0.00"}
                  </div>
                  <span className="text-[11px] text-slate-400 font-mono block mt-0.5">
                    Realized: ₹{portfolio ? portfolio.realized_pnl.toLocaleString("en-IN", { minimumFractionDigits: 2 }) : "0.00"}
                  </span>
                </div>

                <div className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
                  <span className="text-xs text-slate-500 font-medium block">Active Mode</span>
                  <div className="text-xl font-bold font-mono text-slate-900 dark:text-white mt-1">
                    {activeMode}
                  </div>
                  <span className="text-[11px] text-slate-400 block mt-0.5">
                    {activeMode === "INVESTMENT" ? "1–5y Buffett Compounding" : "1–4w Tactical Swing"}
                  </span>
                </div>
              </div>

              {/* Major Indices Grid */}
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-sm text-slate-900 dark:text-white">Indian Market Overview</h3>
                  <span className="text-xs text-slate-400 font-mono">Provider: Upstox API Engine</span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
                  {indices.map((idx) => {
                    const isPos = idx.day_change >= 0;
                    return (
                      <div key={idx.symbol} className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-lg border border-slate-100 dark:border-slate-700/60 font-mono">
                        <span className="text-[11px] text-slate-500 block truncate font-sans font-medium">{idx.symbol}</span>
                        <span className="text-sm font-bold text-slate-900 dark:text-white block mt-0.5">
                          ₹{Number(idx.ltp).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                        </span>
                        <span className={`text-[11px] font-semibold flex items-center gap-0.5 mt-0.5 ${isPos ? "text-emerald-600" : "text-rose-600"}`}>
                          {isPos ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                          {isPos ? "+" : ""}{Number(idx.day_change_pct).toFixed(2)}%
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* AI Discovered Opportunities Quick Ribbon */}
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Radar className="w-4 h-4 text-emerald-600" />
                    <h3 className="font-semibold text-sm text-slate-900 dark:text-white">
                      AI Opportunity Scanner — Top Indian Stocks
                    </h3>
                  </div>
                  <button
                    onClick={() => setActiveTab("scanner")}
                    className="text-xs text-blue-600 hover:underline flex items-center gap-1 font-medium"
                  >
                    View All Presets <ChevronRight className="w-3 h-3" />
                  </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {scannerResults.slice(0, 3).map((item) => (
                    <div
                      key={item.symbol}
                      onClick={() => handleStockClick(item.symbol)}
                      className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-slate-400 dark:hover:border-slate-600 cursor-pointer transition bg-slate-50/50 dark:bg-slate-800/40 space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-sm text-slate-900 dark:text-white font-mono">{item.symbol}</span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
                          Score: {item.opportunity_score}/100
                        </span>
                      </div>
                      <div className="text-xs text-slate-500 truncate">{item.name}</div>
                      <div className="text-xs text-slate-700 dark:text-slate-300 line-clamp-2">
                        {item.reason_to_buy}
                      </div>
                      <div className="pt-2 border-t border-slate-200 dark:border-slate-700/60 flex items-center justify-between text-xs font-mono">
                        <span className="text-slate-500">Entry: {item.entry_zone}</span>
                        <span className="text-emerald-600 font-bold">Target: ₹{item.target_price}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* GitHub-style Calendar Heatmap Embed */}
              <CalendarHeatmap data={heatmapData} />
            </div>
          )}

          {/* ======================================================== */}
          {/* VIEW 2: MARKETS */}
          {/* ======================================================== */}
          {activeTab === "markets" && (
            <div className="space-y-6">
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                <div>
                  <h3 className="font-semibold text-lg text-slate-900 dark:text-white">NSE & BSE Market Pulse</h3>
                  <p className="text-xs text-slate-500">Live index valuation, sector rotation, and breadth statistics.</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {indices.map((idx) => (
                    <div key={idx.symbol} className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 space-y-2 font-mono">
                      <div className="flex justify-between items-center">
                        <span className="font-bold text-slate-900 dark:text-white text-base">{idx.symbol}</span>
                        <span className={`text-xs font-bold px-2 py-0.5 rounded ${idx.day_change >= 0 ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300" : "bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300"}`}>
                          {idx.day_change >= 0 ? "+" : ""}{Number(idx.day_change_pct).toFixed(2)}%
                        </span>
                      </div>
                      <div className="text-2xl font-bold text-slate-900 dark:text-white">
                        ₹{Number(idx.ltp).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                      </div>
                      <div className="text-xs text-slate-500 flex justify-between pt-2 border-t border-slate-100 dark:border-slate-800">
                        <span>High: ₹{Number(idx.high).toLocaleString("en-IN")}</span>
                        <span>Low: ₹{Number(idx.low).toLocaleString("en-IN")}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* VIEW 3: AI OPPORTUNITY SCANNER (MODULE 1) */}
          {/* ======================================================== */}
          {activeTab === "scanner" && (
            <div className="space-y-6">
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <h3 className="font-semibold text-lg text-slate-900 dark:text-white flex items-center gap-2">
                      <Radar className="w-5 h-5 text-emerald-600" />
                      <span>Module 1: AI Indian Stock Opportunity Scanner</span>
                    </h3>
                    <p className="text-xs text-slate-500">
                      Automated screening across fundamental moats, technical breakouts, and valuation bands.
                    </p>
                  </div>
                  <div className="text-xs font-mono text-slate-500">
                    Mode: <span className="font-bold text-slate-900 dark:text-white">{activeMode}</span>
                  </div>
                </div>

                {/* Preset Chips */}
                <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-none text-xs">
                  {[
                    "Quality Businesses (Buffett-Style)",
                    "Undervalued Opportunities",
                    "High-ROCE Elite Franchise",
                    "Low-Debt Strong Balance Sheet",
                    "Technical Breakouts",
                    "Momentum Setups"
                  ].map((p) => (
                    <button
                      key={p}
                      onClick={() => setActivePreset(p)}
                      className={`px-3 py-1.5 rounded-full font-medium whitespace-nowrap transition ${
                        activePreset === p
                          ? "bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-sm"
                          : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-slate-200"
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>

                {/* Results Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs font-sans">
                    <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 font-mono uppercase text-[11px] border-y border-slate-200 dark:border-slate-800">
                      <tr>
                        <th className="py-3 px-4">Symbol / Name</th>
                        <th className="py-3 px-3">LTP (₹)</th>
                        <th className="py-3 px-3">Day %</th>
                        <th className="py-3 px-3">Opp. Score</th>
                        <th className="py-3 px-3">Entry Zone</th>
                        <th className="py-3 px-3">Target</th>
                        <th className="py-3 px-3">Stop Loss</th>
                        <th className="py-3 px-4">Investment Thesis</th>
                        <th className="py-3 px-3">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-mono">
                      {scannerResults.map((item) => (
                        <tr key={item.symbol} className="hover:bg-slate-50/60 dark:hover:bg-slate-800/40 transition">
                          <td className="py-3 px-4">
                            <span className="font-bold text-slate-900 dark:text-white block cursor-pointer hover:text-blue-600" onClick={() => handleStockClick(item.symbol)}>
                              {item.symbol}
                            </span>
                            <span className="text-[11px] text-slate-400 font-sans truncate block max-w-xs">{item.name}</span>
                          </td>
                          <td className="py-3 px-3 font-semibold text-slate-900 dark:text-white">
                            ₹{item.ltp.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                          </td>
                          <td className={`py-3 px-3 font-semibold ${item.day_change_pct >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                            {item.day_change_pct >= 0 ? "+" : ""}{item.day_change_pct.toFixed(2)}%
                          </td>
                          <td className="py-3 px-3">
                            <span className="px-2 py-0.5 rounded font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
                              {item.opportunity_score}
                            </span>
                          </td>
                          <td className="py-3 px-3 text-slate-600 dark:text-slate-400">{item.entry_zone}</td>
                          <td className="py-3 px-3 text-emerald-600 font-bold">₹{item.target_price}</td>
                          <td className="py-3 px-3 text-rose-600">₹{item.stop_loss}</td>
                          <td className="py-3 px-4 font-sans text-slate-600 dark:text-slate-400 max-w-xs truncate" title={item.reason_to_buy}>
                            {item.reason_to_buy}
                          </td>
                          <td className="py-3 px-3">
                            <button
                              onClick={() => {
                                setSelectedSymbol(item.symbol);
                                setIsOrderModalOpen(true);
                              }}
                              className="px-2.5 py-1 rounded bg-black dark:bg-white text-white dark:text-black font-semibold text-[11px] hover:opacity-80 transition"
                            >
                              Trade
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* VIEW 4: AI RESEARCH & STOCK DETAIL */}
          {/* ======================================================== */}
          {activeTab === "research" && (
            <div className="space-y-6">
              {/* Header Card */}
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm flex flex-wrap items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h2 className="text-2xl font-bold font-mono text-slate-900 dark:text-white">
                      {selectedSymbol}
                    </h2>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-mono">
                      NSE Equity
                    </span>
                    {aiAnalysis && (
                      <span className="text-xs px-3 py-0.5 rounded-full font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
                        AI Verdict: {aiAnalysis.recommendation_type} ({aiAnalysis.composite_score}/100)
                      </span>
                    )}
                  </div>
                  <div className="text-2xl font-mono font-bold text-slate-900 dark:text-white mt-1">
                    ₹{currentLtp.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    onClick={() => setIsOrderModalOpen(true)}
                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold text-xs shadow-sm transition"
                  >
                    Simulate Buy Order
                  </button>
                  <button
                    onClick={() => setIsOrderModalOpen(true)}
                    className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-xl font-bold text-xs shadow-sm transition"
                  >
                    Simulate Sell Order
                  </button>
                </div>
              </div>

              {/* TradingView Chart */}
              <TradingViewChart candles={candles} symbol={selectedSymbol} isDark={isDark} />

              {/* Multi-Agent Synthesis Breakdown */}
              {aiAnalysis && (
                <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                  <h3 className="font-semibold text-base text-slate-900 dark:text-white flex items-center gap-2">
                    <Bot className="w-5 h-5 text-blue-600" />
                    <span>Multi-Agent Research Intelligence ({activeMode} Mode)</span>
                  </h3>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
                    <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block">Agent 1: Fundamental</span>
                      <span className="text-sm font-bold text-emerald-600">{aiAnalysis.fundamental_score}/100</span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block">Agent 2: Technical</span>
                      <span className="text-sm font-bold text-blue-600">{aiAnalysis.technical_score}/100</span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block">Agent 3: News Catalyst</span>
                      <span className="text-sm font-bold text-amber-600">{aiAnalysis.news_score}/100</span>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block">Agent 6: Risk Gatekeeper</span>
                      <span className="text-sm font-bold text-emerald-600">{aiAnalysis.risk_approved ? "APPROVED" : "BLOCKED"}</span>
                    </div>
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700/60 space-y-2 text-xs">
                    <div className="font-bold text-slate-900 dark:text-white">Core Investment Thesis:</div>
                    <p className="text-slate-700 dark:text-slate-300 leading-relaxed">{aiAnalysis.investment_thesis}</p>
                    <div className="font-bold text-slate-900 dark:text-white pt-2">Key Risk Factors to Monitor:</div>
                    <p className="text-rose-600 dark:text-rose-400 leading-relaxed">{aiAnalysis.key_risks}</p>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ======================================================== */}
          {/* VIEW 5: AI ANALYST CHAT */}
          {/* ======================================================== */}
          {activeTab === "analyst" && (
            <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm flex flex-col h-[650px]">
              <div className="border-b border-slate-100 dark:border-slate-800 pb-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bot className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-base text-slate-900 dark:text-white">
                    Conversational Indian Stock Market Research Assistant
                  </h3>
                </div>
                <span className="text-xs text-slate-400 font-mono">Grounded in Live Terminal DB</span>
              </div>

              {/* Message Feed */}
              <div className="flex-1 overflow-y-auto py-4 space-y-4">
                {chatMessages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-2xl p-4 rounded-2xl text-xs leading-relaxed ${
                        msg.sender === "user"
                          ? "bg-slate-900 text-white dark:bg-white dark:text-slate-900"
                          : "bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 whitespace-pre-line"
                      }`}
                    >
                      {msg.text}
                    </div>
                  </div>
                ))}
              </div>

              {/* Input Form */}
              <form onSubmit={handleChatSubmit} className="pt-3 border-t border-slate-100 dark:border-slate-800 flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask a research question (e.g. 'Analyse RELIANCE in Investment Mode' or 'Find high ROCE stocks')..."
                  className="flex-1 px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs focus:ring-2 focus:ring-black dark:focus:ring-white focus:outline-none"
                />
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-black dark:bg-white text-white dark:text-black rounded-xl font-bold text-xs shadow-sm"
                >
                  Ask AI
                </button>
              </form>
            </div>
          )}

          {/* ======================================================== */}
          {/* VIEW 6: PAPER TRADING WALLET & LEDGER */}
          {/* ======================================================== */}
          {activeTab === "paper_trading" && (
            <div className="space-y-6">
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-lg text-slate-900 dark:text-white">
                      Virtual Capital Wallet & Immutable Transaction Ledger
                    </h3>
                    <p className="text-xs text-slate-500">
                      Double-entry virtual ledger initialized at ₹10,00,000 with mandatory statutory charges.
                    </p>
                  </div>
                  <button
                    onClick={() => setIsOrderModalOpen(true)}
                    className="px-4 py-2 bg-black dark:bg-white text-white dark:text-black rounded-xl font-bold text-xs"
                  >
                    Place Simulated Order
                  </button>
                </div>

                {/* Holdings Table */}
                <div className="pt-2">
                  <h4 className="font-semibold text-xs text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
                    Current Portfolio Positions
                  </h4>
                  {portfolio && portfolio.holdings.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 uppercase text-[11px] border-y border-slate-200 dark:border-slate-800">
                          <tr>
                            <th className="py-2.5 px-3">Symbol</th>
                            <th className="py-2.5 px-3">Qty</th>
                            <th className="py-2.5 px-3">Avg Buy Price</th>
                            <th className="py-2.5 px-3">Current LTP</th>
                            <th className="py-2.5 px-3">Invested Value</th>
                            <th className="py-2.5 px-3">Current Value</th>
                            <th className="py-2.5 px-3">Unrealized P&L</th>
                            <th className="py-2.5 px-3">Action</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                          {portfolio.holdings.map((h) => (
                            <tr key={h.symbol} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                              <td className="py-2.5 px-3 font-bold text-slate-900 dark:text-white">{h.symbol}</td>
                              <td className="py-2.5 px-3">{h.quantity}</td>
                              <td className="py-2.5 px-3">₹{h.average_price.toFixed(2)}</td>
                              <td className="py-2.5 px-3 font-semibold">₹{h.current_price.toFixed(2)}</td>
                              <td className="py-2.5 px-3">₹{h.invested_value.toLocaleString("en-IN")}</td>
                              <td className="py-2.5 px-3">₹{h.current_value.toLocaleString("en-IN")}</td>
                              <td className={`py-2.5 px-3 font-bold ${h.unrealized_pnl >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                                {h.unrealized_pnl >= 0 ? "+" : ""}₹{h.unrealized_pnl.toFixed(2)} ({h.unrealized_pnl_pct.toFixed(2)}%)
                              </td>
                              <td className="py-2.5 px-3">
                                <button
                                  onClick={() => {
                                    setSelectedSymbol(h.symbol);
                                    setIsOrderModalOpen(true);
                                  }}
                                  className="px-2 py-1 rounded bg-rose-600 text-white font-bold text-[10px]"
                                >
                                  Sell / Exit
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="p-8 text-center text-slate-400 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-dashed border-slate-200 dark:border-slate-800 text-xs">
                      No open positions yet. Use the search or AI scanner to execute your first simulated trade!
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* VIEW 7: AI RECOMMENDATION PERFORMANCE TRACKER (MODULE 2) */}
          {/* ======================================================== */}
          {activeTab === "ai_performance" && (
            <div className="space-y-6">
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                <div>
                  <h3 className="font-semibold text-lg text-slate-900 dark:text-white flex items-center gap-2">
                    <Award className="w-5 h-5 text-amber-500" />
                    <span>Module 2: AI Recommendation Performance Tracker & Calibration</span>
                  </h3>
                  <p className="text-xs text-slate-500">
                    Immutable audit trail evaluating out-of-sample prediction accuracy and alpha relative to NIFTY 50.
                  </p>
                </div>

                {performance && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono text-xs">
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block">Total Recommendations</span>
                      <span className="text-xl font-bold text-slate-900 dark:text-white mt-1 block">
                        {performance.total_recommendations}
                      </span>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block">Empirical Win Rate</span>
                      <span className="text-xl font-bold text-emerald-600 mt-1 block">
                        {performance.win_rate_pct}%
                      </span>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block">Profit Factor</span>
                      <span className="text-xl font-bold text-blue-600 mt-1 block">
                        {performance.profit_factor}x
                      </span>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block">Alpha vs NIFTY 50</span>
                      <span className="text-xl font-bold text-emerald-600 mt-1 block">
                        +{performance.alpha_vs_nifty_pct}%
                      </span>
                    </div>
                  </div>
                )}

                {/* Recommendation Timeline Table */}
                <div className="overflow-x-auto pt-2">
                  <table className="w-full text-left text-xs font-mono">
                    <thead className="bg-slate-50 dark:bg-slate-800/60 text-slate-500 uppercase text-[11px] border-y border-slate-200 dark:border-slate-800">
                      <tr>
                        <th className="py-2.5 px-3">Stock</th>
                        <th className="py-2.5 px-3">Mode</th>
                        <th className="py-2.5 px-3">Entry CMP</th>
                        <th className="py-2.5 px-3">Target</th>
                        <th className="py-2.5 px-3">Stop Loss</th>
                        <th className="py-2.5 px-3">Current Return</th>
                        <th className="py-2.5 px-3">Status</th>
                        <th className="py-2.5 px-3">NIFTY Return</th>
                        <th className="py-2.5 px-3">Alpha</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                      {recommendations.map((rec) => (
                        <tr key={rec.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                          <td className="py-2.5 px-3 font-bold text-slate-900 dark:text-white">{rec.symbol}</td>
                          <td className="py-2.5 px-3">{rec.mode}</td>
                          <td className="py-2.5 px-3">₹{rec.cmp_at_rec.toFixed(2)}</td>
                          <td className="py-2.5 px-3 text-emerald-600 font-bold">₹{rec.target_price.toFixed(2)}</td>
                          <td className="py-2.5 px-3 text-rose-600">₹{rec.stop_loss.toFixed(2)}</td>
                          <td className={`py-2.5 px-3 font-bold ${rec.current_pnl_pct >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                            {rec.current_pnl_pct >= 0 ? "+" : ""}{rec.current_pnl_pct.toFixed(2)}%
                          </td>
                          <td className="py-2.5 px-3">
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 dark:bg-slate-800">
                              {rec.status}
                            </span>
                          </td>
                          <td className="py-2.5 px-3">+{rec.benchmark_nifty_return_pct.toFixed(2)}%</td>
                          <td className="py-2.5 px-3 text-emerald-600 font-bold">+{rec.alpha_pct.toFixed(2)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Self-Evaluation AI Retrospectives */}
                {performance && (
                  <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 space-y-2 text-xs">
                    <div className="font-bold text-slate-900 dark:text-white flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-amber-500" />
                      <span>AI Model Self-Evaluation Observations:</span>
                    </div>
                    <ul className="list-disc pl-5 space-y-1 text-slate-600 dark:text-slate-300">
                      {performance.self_evaluation_notes.map((note, idx) => (
                        <li key={idx}>{note}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* VIEW 8: BENCHMARK ANALYSIS (MODULE 5) */}
          {/* ======================================================== */}
          {activeTab === "benchmarks" && (
            <div className="space-y-6">
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                <div>
                  <h3 className="font-semibold text-lg text-slate-900 dark:text-white">
                    Module 5: Benchmark Everything — NIFTY 50 TRI Relative Performance
                  </h3>
                  <p className="text-xs text-slate-500">
                    Evaluating personal simulated equity curves and Sharpe ratios against the benchmark.
                  </p>
                </div>

                {benchmarkData && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono text-xs">
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block">Portfolio Cumulative Return</span>
                      <span className="text-xl font-bold text-emerald-600 mt-1 block">
                        +{benchmarkData.portfolio_return_pct}%
                      </span>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block">NIFTY 50 Benchmark Return</span>
                      <span className="text-xl font-bold text-slate-700 dark:text-slate-300 mt-1 block">
                        +{benchmarkData.benchmark_return_pct}%
                      </span>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block">Alpha Outperformance</span>
                      <span className="text-xl font-bold text-emerald-600 mt-1 block">
                        +{benchmarkData.alpha}%
                      </span>
                    </div>
                    <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
                      <span className="text-slate-500 block">Annualized Sharpe Ratio</span>
                      <span className="text-xl font-bold text-blue-600 mt-1 block">
                        {benchmarkData.sharpe_ratio}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* VIEW 9: PERSONAL P&L HEATMAP (MANDATORY FEATURE) */}
          {/* ======================================================== */}
          {activeTab === "heatmap" && (
            <div className="space-y-6">
              <CalendarHeatmap data={heatmapData} />
            </div>
          )}

          {/* ======================================================== */}
          {/* VIEW 10: ALERTS HUB (MODULE 4) */}
          {/* ======================================================== */}
          {activeTab === "alerts" && (
            <div className="space-y-6">
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                <div>
                  <h3 className="font-semibold text-lg text-slate-900 dark:text-white">
                    Module 4: AI Investment Opportunity Alerts & Threshold Monitor
                  </h3>
                  <p className="text-xs text-slate-500">
                    Real-time monitoring across price entries, earnings inflections, and portfolio drawdown caps.
                  </p>
                </div>

                <div className="space-y-3">
                  {alerts.map((a) => (
                    <div
                      key={a.id}
                      className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 flex items-start justify-between gap-4"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-sm text-slate-900 dark:text-white font-mono">{a.symbol}</span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300">
                            {a.category}
                          </span>
                          <span className="text-xs font-semibold text-slate-800 dark:text-slate-200">{a.title}</span>
                        </div>
                        <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">{a.ai_explanation}</p>
                        <div className="text-[11px] text-slate-400 font-mono">
                          Trigger Condition: {a.trigger_condition} • {a.event_timestamp}
                        </div>
                      </div>
                      <button
                        onClick={() => handleStockClick(a.symbol)}
                        className="px-3 py-1.5 rounded-lg bg-black dark:bg-white text-white dark:text-black font-semibold text-xs whitespace-nowrap"
                      >
                        Research
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* VIEW 11: LEARNING CENTRE & JOURNAL */}
          {/* ======================================================== */}
          {activeTab === "learning" && (
            <div className="space-y-6">
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
                <div>
                  <h3 className="font-semibold text-lg text-slate-900 dark:text-white flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-emerald-600" />
                    <span>Investment Learning Centre & Buffett Compounding Principles</span>
                  </h3>
                  <p className="text-xs text-slate-500">
                    Educational modules anchored in real portfolio performance, ROCE compounding, and cognitive bias control.
                  </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {lessons.map((lesson) => (
                    <div
                      key={lesson.id}
                      className="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 space-y-3 flex flex-col justify-between"
                    >
                      <div className="space-y-2">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-600 block">
                          {lesson.category}
                        </span>
                        <h4 className="font-semibold text-sm text-slate-900 dark:text-white">
                          {lesson.title}
                        </h4>
                        <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                          {lesson.description}
                        </p>
                        <ul className="list-disc pl-4 space-y-1 text-xs text-slate-500">
                          {lesson.key_takeaways.map((point: string, idx: number) => (
                            <li key={idx}>{point}</li>
                          ))}
                        </ul>
                      </div>

                      {lesson.buffett_quote && (
                        <blockquote className="p-3 rounded-lg bg-amber-50 dark:bg-amber-950/30 border-l-2 border-amber-500 text-[11px] italic text-amber-900 dark:text-amber-200">
                          &ldquo;{lesson.buffett_quote}&rdquo;
                        </blockquote>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* VIEW 12: SETTINGS & BROKER CREDENTIALS */}
          {/* ======================================================== */}
          {activeTab === "settings" && (
            <div className="space-y-6">
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-4 max-w-2xl">
                <div>
                  <h3 className="font-semibold text-lg text-slate-900 dark:text-white">
                    API Connections & Terminal Settings
                  </h3>
                  <p className="text-xs text-slate-500">
                    Configure your Indian broker API credentials and statutory tax rates.
                  </p>
                </div>

                <div className="space-y-4 text-xs font-mono">
                  <div>
                    <label className="block font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Primary Market Data Adapter
                    </label>
                    <select
                      value="UPSTOX"
                      disabled
                      className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs"
                    >
                      <option value="UPSTOX">Upstox Developer API v2 (Configured Default)</option>
                      <option value="DHAN">DhanHQ API</option>
                      <option value="KITE">Zerodha Kite Connect</option>
                    </select>
                  </div>

                  <div>
                    <label className="block font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Upstox API Key / Access Token
                    </label>
                    <input
                      type="password"
                      placeholder="Enter your Upstox v2 Access Token..."
                      className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs"
                    />
                    <span className="text-[11px] text-slate-400 mt-1 block">
                      Stored securely server-side. Never exposed to browser bundle.
                    </span>
                  </div>

                  <div className="pt-2 border-t border-slate-100 dark:border-slate-800">
                    <span className="font-bold text-slate-800 dark:text-slate-200 block mb-2 font-sans">
                      Configured Statutory Rates (SEBI & Indian Exchange)
                    </span>
                    <div className="grid grid-cols-2 gap-2 text-slate-600 dark:text-slate-400 text-[11px]">
                      <div>Delivery Brokerage: ₹0.00</div>
                      <div>Delivery STT: 0.10%</div>
                      <div>NSE Exchange Charge: 0.00345%</div>
                      <div>GST: 18.00%</div>
                      <div>SEBI Turnover Fee: 0.0001%</div>
                      <div>Stamp Duty: 0.015%</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* Order Execution Ticket Modal */}
      <OrderModal
        symbol={selectedSymbol}
        currentPrice={currentLtp}
        mode={activeMode}
        isOpen={isOrderModalOpen}
        onClose={() => setIsOrderModalOpen(false)}
        onOrderSuccess={refreshPortfolio}
      />
    </div>
  );
}
