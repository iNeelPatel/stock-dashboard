"use client";

import React, { useState, useEffect } from "react";
import { X, AlertCircle, CheckCircle2, ShieldCheck } from "lucide-react";
import { api } from "@/lib/api";

interface OrderModalProps {
  symbol: string;
  currentPrice: number;
  mode: "INVESTMENT" | "TRADING";
  isOpen: boolean;
  onClose: () => void;
  onOrderSuccess: () => void;
}

export const OrderModal: React.FC<OrderModalProps> = ({
  symbol,
  currentPrice,
  mode,
  isOpen,
  onClose,
  onOrderSuccess
}) => {
  const [direction, setDirection] = useState<"BUY" | "SELL">("BUY");
  const [orderType, setOrderType] = useState<string>("MARKET");
  const [quantity, setQuantity] = useState<number>(10);
  const [limitPrice, setLimitPrice] = useState<number>(currentPrice);
  const [charges, setCharges] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    setLimitPrice(currentPrice);
  }, [currentPrice]);

  useEffect(() => {
    if (quantity > 0 && currentPrice > 0) {
      const priceToUse = orderType === "MARKET" ? currentPrice : limitPrice;
      api.previewCharges(direction, mode, quantity, priceToUse)
        .then(setCharges)
        .catch(() => setCharges(null));
    }
  }, [direction, mode, quantity, limitPrice, orderType, currentPrice]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const res = await api.placeOrder({
        symbol,
        direction,
        quantity,
        order_type: orderType,
        mode,
        limit_price: orderType === "LIMIT" ? limitPrice : undefined
      });
      setSuccess(`Order executed successfully! ${direction} ${quantity} ${symbol} @ ₹${res.execution_price}`);
      setTimeout(() => {
        onOrderSuccess();
        onClose();
      }, 1500);
    } catch (err: any) {
      setError(err.message || "Failed to execute order.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 dark:border-slate-800 space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <div>
            <h3 className="font-semibold text-lg text-slate-900 dark:text-white flex items-center gap-2">
              <span>Simulated Order Ticket</span>
              <span className="text-xs px-2 py-0.5 rounded-full font-mono bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300">
                {mode}
              </span>
            </h3>
            <div className="text-xs text-slate-500 font-mono">
              {symbol} • CMP: ₹{currentPrice.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 dark:hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Direction Tabs */}
        <div className="grid grid-cols-2 gap-2 p-1 bg-slate-100 dark:bg-slate-800 rounded-xl">
          <button
            type="button"
            onClick={() => setDirection("BUY")}
            className={`py-2 rounded-lg text-xs font-bold transition ${
              direction === "BUY"
                ? "bg-emerald-600 text-white shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            BUY (Long)
          </button>
          <button
            type="button"
            onClick={() => setDirection("SELL")}
            className={`py-2 rounded-lg text-xs font-bold transition ${
              direction === "SELL"
                ? "bg-rose-600 text-white shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            }`}
          >
            SELL (Exit / Short)
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Order Type
              </label>
              <select
                value={orderType}
                onChange={(e) => setOrderType(e.target.value)}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs focus:ring-1 focus:ring-black dark:focus:ring-white"
              >
                <option value="MARKET">Market Order</option>
                <option value="LIMIT">Limit Order</option>
                <option value="STOP_LOSS">Stop Loss Order</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Quantity (Shares)
              </label>
              <input
                type="number"
                min="1"
                value={quantity}
                onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-mono"
              />
            </div>
          </div>

          {orderType === "LIMIT" && (
            <div>
              <label className="block text-xs font-medium text-slate-700 dark:text-slate-300 mb-1">
                Limit Price (₹)
              </label>
              <input
                type="number"
                step="0.05"
                value={limitPrice}
                onChange={(e) => setLimitPrice(parseFloat(e.target.value) || currentPrice)}
                className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-mono"
              />
            </div>
          )}

          {/* Real-time Indian Statutory Charges Breakdown */}
          {charges && (
            <div className="p-3 bg-slate-50 dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700 space-y-1.5 text-xs font-mono">
              <div className="font-sans font-semibold text-slate-800 dark:text-slate-200 flex items-center justify-between pb-1 border-b border-slate-200 dark:border-slate-700">
                <span>Estimated Statutory Levies:</span>
                <span className="text-[11px] font-normal text-slate-500">SEBI / NSE Mandated</span>
              </div>
              <div className="flex justify-between text-slate-600 dark:text-slate-400">
                <span>Gross Turnover:</span>
                <span>₹{Number(charges.turnover).toLocaleString("en-IN", { minimumFractionDigits: 2 })}</span>
              </div>
              <div className="flex justify-between text-slate-600 dark:text-slate-400">
                <span>Securities Transaction Tax (STT):</span>
                <span>₹{Number(charges.stt).toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-slate-600 dark:text-slate-400">
                <span>Exchange Turnover Charges:</span>
                <span>₹{Number(charges.exchange_charges).toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-slate-600 dark:text-slate-400">
                <span>GST (18%) & SEBI Fees:</span>
                <span>₹{(Number(charges.gst) + Number(charges.sebi_charges)).toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-slate-600 dark:text-slate-400">
                <span>Stamp Duty:</span>
                <span>₹{Number(charges.stamp_duty).toFixed(2)}</span>
              </div>
              <div className="flex justify-between font-bold pt-1.5 border-t border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white">
                <span>Total Net {direction === "BUY" ? "Payable" : "Receivable"}:</span>
                <span className={direction === "BUY" ? "text-emerald-600" : "text-blue-600"}>
                  ₹{Number(charges.net_amount).toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          )}

          {error && (
            <div className="p-3 rounded-lg bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="p-3 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
              <span>{success}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 rounded-xl font-bold text-xs tracking-wide uppercase transition shadow-sm ${
              direction === "BUY"
                ? "bg-emerald-600 hover:bg-emerald-700 text-white"
                : "bg-rose-600 hover:bg-rose-700 text-white"
            } ${loading ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            {loading ? "Executing simulated order..." : `Place Simulated ${direction} Order`}
          </button>
        </form>
      </div>
    </div>
  );
};
