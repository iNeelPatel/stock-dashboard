"use client";

import React, { useState } from "react";
import { HeatmapData, CalendarDay } from "@/lib/api";
import { Calendar, TrendingUp, TrendingDown, ArrowUpRight, ArrowDownRight, X } from "lucide-react";

interface CalendarHeatmapProps {
  data: HeatmapData | null;
}

export const CalendarHeatmap: React.FC<CalendarHeatmapProps> = ({ data }) => {
  const [selectedDay, setSelectedDay] = useState<CalendarDay | null>(null);

  if (!data || !data.calendar_days) {
    return (
      <div className="p-8 text-center text-slate-400 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl">
        Loading personal P&L calendar heatmap...
      </div>
    );
  }

  const { calendar_days, metrics } = data;

  // Group into weeks (7 days per column)
  const weeks: CalendarDay[][] = [];
  let currentWeek: CalendarDay[] = [];
  calendar_days.forEach((day, index) => {
    currentWeek.push(day);
    if (currentWeek.length === 7 || index === calendar_days.length - 1) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
  });

  const getCellColor = (intensity: number, isWeekend: boolean) => {
    if (isWeekend) return "bg-slate-100/40 dark:bg-slate-800/20 border-transparent opacity-40";
    switch (intensity) {
      case 4:
        return "bg-emerald-600 hover:ring-2 hover:ring-emerald-400";
      case 3:
        return "bg-emerald-500 hover:ring-2 hover:ring-emerald-300";
      case 2:
        return "bg-emerald-400 hover:ring-2 hover:ring-emerald-200";
      case -1:
        return "bg-rose-400 hover:ring-2 hover:ring-rose-200";
      case -2:
        return "bg-rose-600 hover:ring-2 hover:ring-rose-400";
      default:
        return "bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700";
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm space-y-5">
      {/* Header and Aggregate Metrics */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-slate-700 dark:text-slate-300" />
            <h3 className="font-semibold text-base text-slate-900 dark:text-white">
              Personal Profit & Loss Calendar Heatmap
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Daily simulated performance across 52 trading weeks. Click any cell to inspect trade logs.
          </p>
        </div>

        {/* Quick Stats Pills */}
        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="px-3 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300">
            Profitable Days: <span className="font-bold">{metrics.profitable_days}</span> ({metrics.win_rate_pct}%)
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300">
            Losing Days: <span className="font-bold">{metrics.losing_days}</span>
          </div>
          {metrics.best_day.date && (
            <div className="hidden sm:block px-3 py-1.5 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300">
              Best Day: <span className="text-emerald-600 font-bold">+₹{metrics.best_day.pnl.toLocaleString("en-IN")}</span> ({metrics.best_day.date})
            </div>
          )}
        </div>
      </div>

      {/* GitHub-style Heatmap Grid */}
      <div className="overflow-x-auto pb-2">
        <div className="min-w-[760px] flex gap-1.5">
          {weeks.map((week, wIdx) => (
            <div key={wIdx} className="flex flex-col gap-1.5">
              {week.map((day) => {
                const colorClass = getCellColor(day.intensity, day.is_weekend);
                return (
                  <button
                    key={day.date}
                    onClick={() => !day.is_weekend && setSelectedDay(day)}
                    disabled={day.is_weekend}
                    title={`${day.date}: Net P&L ₹${day.net_pnl.toLocaleString("en-IN")} (${day.trades_count} trades)`}
                    className={`w-3.5 h-3.5 rounded-[3px] transition cursor-pointer ${colorClass}`}
                  />
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100 dark:border-slate-800">
        <span>52 Weeks Historical Record</span>
        <div className="flex items-center gap-2">
          <span>High Loss</span>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 rounded-[2px] bg-rose-600" />
            <span className="w-3 h-3 rounded-[2px] bg-rose-400" />
            <span className="w-3 h-3 rounded-[2px] bg-slate-200 dark:bg-slate-800" />
            <span className="w-3 h-3 rounded-[2px] bg-emerald-400" />
            <span className="w-3 h-3 rounded-[2px] bg-emerald-600" />
          </div>
          <span>High Profit</span>
        </div>
      </div>

      {/* Selected Day Trade Modal */}
      {selectedDay && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold text-lg text-slate-900 dark:text-white">
                  Trading Session Summary
                </h4>
                <div className="text-xs text-slate-500 font-mono">{selectedDay.date}</div>
              </div>
              <button
                onClick={() => setSelectedDay(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 py-2 font-mono text-xs">
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                <span className="text-slate-500 block text-[11px]">Net Daily P&L</span>
                <span className={`text-base font-bold ${selectedDay.net_pnl >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                  {selectedDay.net_pnl >= 0 ? "+" : ""}₹{selectedDay.net_pnl.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                <span className="text-slate-500 block text-[11px]">Daily Return</span>
                <span className={`text-base font-bold ${selectedDay.return_pct >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
                  {selectedDay.return_pct >= 0 ? "+" : ""}{selectedDay.return_pct.toFixed(2)}%
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                <span className="text-slate-500 block text-[11px]">Realized P&L</span>
                <span className="text-sm font-semibold text-slate-900 dark:text-white">
                  ₹{selectedDay.realized_pnl.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                </span>
              </div>
              <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700">
                <span className="text-slate-500 block text-[11px]">Trades Executed</span>
                <span className="text-sm font-semibold text-slate-900 dark:text-white">
                  {selectedDay.trades_count} Orders
                </span>
              </div>
            </div>

            <div className="text-xs text-slate-500 bg-slate-50 dark:bg-slate-800/60 p-3 rounded-lg border border-slate-200 dark:border-slate-800">
              P&L calculated using double-entry ledger transactions and daily settlement closing mark-to-market.
            </div>

            <button
              onClick={() => setSelectedDay(null)}
              className="w-full py-2.5 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl font-medium text-xs shadow-sm hover:opacity-90 transition"
            >
              Close Summary
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
