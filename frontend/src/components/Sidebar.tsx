"use client";

import React from "react";
import {
  LayoutDashboard,
  LineChart,
  Radar,
  Bot,
  SearchCode,
  BookmarkCheck,
  TrendingUp,
  Activity,
  Briefcase,
  WalletCards,
  Award,
  GitCompare,
  CalendarDays,
  Bell,
  GraduationCap,
  Settings
} from "lucide-react";

export type NavTab =
  | "overview"
  | "markets"
  | "scanner"
  | "analyst"
  | "research"
  | "watchlist"
  | "investment_mode"
  | "trading_mode"
  | "portfolio"
  | "paper_trading"
  | "ai_performance"
  | "benchmarks"
  | "heatmap"
  | "alerts"
  | "learning"
  | "settings";

interface SidebarProps {
  activeTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  unreadAlertsCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  unreadAlertsCount
}) => {
  const navItems: Array<{ id: NavTab; label: string; icon: React.ElementType; badge?: string | number }> = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    { id: "markets", label: "Markets", icon: LineChart },
    { id: "scanner", label: "AI Scanner", icon: Radar, badge: "Live" },
    { id: "analyst", label: "AI Analyst", icon: Bot },
    { id: "research", label: "Stock Research", icon: SearchCode },
    { id: "watchlist", label: "Watchlist", icon: BookmarkCheck },
    { id: "investment_mode", label: "Investment Mode", icon: TrendingUp },
    { id: "trading_mode", label: "Trading Mode", icon: Activity },
    { id: "portfolio", label: "Portfolio", icon: Briefcase },
    { id: "paper_trading", label: "Paper Trading", icon: WalletCards },
    { id: "ai_performance", label: "AI Performance", icon: Award },
    { id: "benchmarks", label: "Benchmark Analysis", icon: GitCompare },
    { id: "heatmap", label: "P&L Heatmap", icon: CalendarDays },
    { id: "alerts", label: "Alerts Hub", icon: Bell, badge: unreadAlertsCount > 0 ? unreadAlertsCount : undefined },
    { id: "learning", label: "Learning & Journal", icon: GraduationCap },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside className="w-64 flex-shrink-0 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col justify-between p-3 min-h-[calc(100vh-5rem)]">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          Core Navigation
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition ${
                isActive
                  ? "bg-slate-900 text-white dark:bg-white dark:text-slate-900 shadow-sm"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`w-4 h-4 ${isActive ? "" : "text-slate-400 group-hover:text-slate-600"}`} />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span
                  className={`px-1.5 py-0.2 rounded-full text-[10px] font-semibold ${
                    isActive
                      ? "bg-slate-800 text-slate-200 dark:bg-slate-200 dark:text-slate-800"
                      : "bg-blue-100 text-blue-700 dark:bg-blue-900/60 dark:text-blue-300"
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Terminal Sandbox Notice */}
      <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-800 text-[11px] text-slate-500 space-y-1">
        <div className="font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          Upstox Sandbox Engine
        </div>
        <p className="leading-snug">Paper orders are simulated with realistic Indian STT & exchange levies.</p>
      </div>
    </aside>
  );
};
