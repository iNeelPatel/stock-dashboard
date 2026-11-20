"use client";

import React, { useEffect, useRef } from "react";
import { createChart, IChartApi, ISeriesApi, ColorType } from "lightweight-charts";
import { CandleData } from "@/lib/api";

interface TradingViewChartProps {
  candles: CandleData[];
  symbol: string;
  isDark?: boolean;
}

export const TradingViewChart: React.FC<TradingViewChartProps> = ({
  candles,
  symbol,
  isDark = false
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 420,
      layout: {
        background: { type: ColorType.Solid, color: isDark ? "#0f172a" : "#ffffff" },
        textColor: isDark ? "#94a3b8" : "#475569",
        fontSize: 11,
        fontFamily: "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif"
      },
      grid: {
        vertLines: { color: isDark ? "#1e293b" : "#f1f5f9" },
        horzLines: { color: isDark ? "#1e293b" : "#f1f5f9" }
      },
      rightPriceScale: {
        borderColor: isDark ? "#334155" : "#e2e8f0",
      },
      timeScale: {
        borderColor: isDark ? "#334155" : "#e2e8f0",
        timeVisible: true,
      },
      crosshair: {
        vertLine: { color: isDark ? "#64748b" : "#94a3b8", width: 1, style: 3 },
        horzLine: { color: isDark ? "#64748b" : "#94a3b8", width: 1, style: 3 },
      }
    });

    const candleSeries = chart.addCandlestickSeries({
      upColor: "#16a34a",
      downColor: "#dc2626",
      borderVisible: false,
      wickUpColor: "#16a34a",
      wickDownColor: "#dc2626",
    });

    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: "volume" },
      priceScaleId: "",
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    // Format candle data for lightweight charts
    const chartData = candles.map((c) => {
      // Lightweight charts requires YYYY-MM-DD or unix timestamp
      const dateStr = c.timestamp.split("T")[0];
      return {
        time: dateStr,
        open: Number(c.open),
        high: Number(c.high),
        low: Number(c.low),
        close: Number(c.close),
      };
    });

    const volData = candles.map((c) => {
      const isUp = Number(c.close) >= Number(c.open);
      return {
        time: c.timestamp.split("T")[0],
        value: Number(c.volume),
        color: isUp ? "rgba(22, 163, 74, 0.25)" : "rgba(220, 38, 38, 0.25)",
      };
    });

    candleSeries.setData(chartData);
    volumeSeries.setData(volData);
    chart.timeScale().fitContent();

    chartRef.current = chart;

    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [candles, isDark]);

  return (
    <div className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="font-semibold text-sm text-slate-900 dark:text-white font-mono">{symbol}</span>
          <span className="text-xs text-slate-400">TradingView Lightweight Chart (Daily Candles & Volume)</span>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="inline-flex items-center gap-1 text-emerald-600 font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span> Bullish
          </span>
          <span className="inline-flex items-center gap-1 text-rose-600 font-medium ml-2">
            <span className="w-2 h-2 rounded-full bg-rose-500"></span> Bearish
          </span>
        </div>
      </div>
      <div ref={chartContainerRef} className="w-full" />
    </div>
  );
};
