"use client";

import React, { useState, useEffect } from "react";
import { Search, ShieldAlert, TrendingUp, Sun, Moon, Bell, ArrowUpRight, ArrowDownRight, Layers } from "lucide-react";
import { api, QuoteData, SearchResult } from "@/lib/api";

interface NavbarProps {
  activeMode: "INVESTMENT" | "TRADING";
  onModeToggle: (mode: "INVESTMENT" | "TRADING") => void;
  onSelectStock: (symbol: string) => void;
  isDark: boolean;
  onToggleTheme: () => void;
  unreadAlertsCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeMode,
  onModeToggle,
  onSelectStock,
  isDark,
  onToggleTheme,
  unreadAlertsCount
}) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [indices, setIndices] = useState<QuoteData[]>([]);
  const [providerHealth, setProviderHealth] = useState<{ is_connected: boolean; message: string; latency_ms: number } | null>(null);

  useEffect(() => {
    // Initial fetch of indices and provider status
    api.getIndices().then(setIndices).catch(() => {});
    api.getProviderStatus().then(setProviderHealth).catch(() => {});

    // Polling interval for live ticker
    const interval = setInterval(() => {
      api.getIndices().then(setIndices).catch(() => {});
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSearch = async (val: string) => {
    setQuery(val);
    if (val.trim().length > 0) {
      setIsSearching(true);
      try {
        const res = await api.searchStocks(val);
        setResults(res);
      } catch (e) {
        setResults([]);
      }
    } else {
      setIsSearching(false);
      setResults([]);
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
      {/* Top Bar: Search, Mode Switcher, User & Status */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-black dark:bg-white flex items-center justify-center text-white dark:text-black font-bold tracking-tight text-lg shadow-sm">
            AI
          </div>
          <div>
            <div className="font-semibold text-slate-900 dark:text-white text-base leading-tight tracking-tight">
              AI Investment Terminal
            </div>
            <div className="text-[11px] text-slate-500 font-medium">
              NSE / BSE • Paper Trading
            </div>
          </div>
        </div>

        {/* Global Stock Search Bar */}
        <div className="relative flex-1 max-w-lg">
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search Indian stocks (e.g., RELIANCE, TCS, HDFCBANK)..."
              className="w-full pl-10 pr-4 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-black dark:focus:ring-white transition"
            />
          </div>

          {/* Autocomplete Dropdown */}
          {isSearching && results.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-slate-800 rounded-xl shadow-xl border border-slate-200 dark:border-slate-700 py-1.5 z-50 max-h-72 overflow-y-auto">
              {results.map((item) => (
                <button
                  key={item.symbol}
                  onClick={() => {
                    onSelectStock(item.symbol);
                    setIsSearching(false);
                    setQuery("");
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-slate-50 dark:hover:bg-slate-700/50 flex items-center justify-between group transition"
                >
                  <div>
                    <div className="font-medium text-slate-900 dark:text-white text-sm group-hover:text-blue-600 transition">
                      {item.symbol}
                    </div>
                    <div className="text-xs text-slate-500 truncate max-w-xs">{item.name}</div>
                  </div>
                  <span className="text-[11px] px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-mono">
                    {item.exchange}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Controls: Mode Switcher, Provider Health & Theme */}
        <div className="flex items-center gap-3">
          {/* Strategy Mode Toggle */}
          <div className="flex items-center bg-slate-100 dark:bg-slate-800 p-1 rounded-lg border border-slate-200 dark:border-slate-700">
            <button
              onClick={() => onModeToggle("INVESTMENT")}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition ${
                activeMode === "INVESTMENT"
                  ? "bg-emerald-600 text-white shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              Investment Mode (1–5y)
            </button>
            <button
              onClick={() => onModeToggle("TRADING")}
              className={`px-3 py-1 text-xs font-semibold rounded-md transition ${
                activeMode === "TRADING"
                  ? "bg-blue-600 text-white shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              Trading Mode (1–4w)
            </button>
          </div>

          {/* Provider Status Pill */}
          <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Upstox API</span>
          </div>

          {/* Theme Toggle */}
          <button
            onClick={onToggleTheme}
            className="p-2 rounded-lg text-slate-500 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition"
            title="Toggle Light/Dark Theme"
          >
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Real-Time Market Ticker Ribbon */}
      <div className="bg-slate-50/90 dark:bg-slate-900/90 border-t border-slate-200 dark:border-slate-800 overflow-x-auto whitespace-nowrap scrollbar-none py-1.5 px-4">
        <div className="max-w-7xl mx-auto flex items-center gap-6 text-xs font-mono">
          {indices.map((idx) => {
            const isPos = idx.day_change >= 0;
            return (
              <div key={idx.symbol} className="inline-flex items-center gap-2">
                <span className="font-semibold text-slate-700 dark:text-slate-300">{idx.symbol}:</span>
                <span className="text-slate-900 dark:text-white font-medium">₹{Number(idx.ltp).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
                <span className={`inline-flex items-center text-[11px] font-semibold ${isPos ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}>
                  {isPos ? "+" : ""}{Number(idx.day_change_pct).toFixed(2)}%
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </header>
  );
};
