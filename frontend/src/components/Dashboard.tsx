"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import SpendingPieChart from "./SpendingPieChart";
import MonthlyBarChart from "./MonthlyBarChart";
import DailyLineChart from "./DailyLineChart";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface CategorySummary {
  category: string;
  total: number;
  percentage: number;
}

interface MonthlySummary {
  month: string;
  total: number;
  categories: Record<string, number>;
}

interface DailySummary {
  date: string;
  total: number;
}

interface Transaction {
  date: string;
  description: string;
  amount: number;
  category: string;
}

interface AnalysisData {
  categories: CategorySummary[];
  monthly: MonthlySummary[];
  daily: DailySummary[];
  transactions: Transaction[];
  advice: string;
}

interface Props {
  fileId: string;
}

export default function Dashboard({ fileId }: Props) {
  const [data, setData] = useState<AnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [txPage, setTxPage] = useState(0);
  const PAGE_SIZE = 20;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`${API_BASE}/api/analysis/${fileId}`);
        setData(res.data);
      } catch (err: unknown) {
        const message =
          axios.isAxiosError(err) && err.response?.data?.detail
            ? err.response.data.detail
            : "Failed to load analysis. Make sure the backend is running.";
        setError(message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [fileId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-emerald-400 text-lg animate-pulse">
          Analysing your transactions…
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/40 border border-red-500 text-red-300 rounded-xl px-6 py-4">
        ⚠️ {error}
      </div>
    );
  }

  if (!data) return null;

  const paginatedTx = data.transactions.slice(
    txPage * PAGE_SIZE,
    (txPage + 1) * PAGE_SIZE
  );
  const totalPages = Math.ceil(data.transactions.length / PAGE_SIZE);

  return (
    <div className="flex flex-col gap-8">
      {/* Summary cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard
          label="Total Transactions"
          value={data.transactions.length.toString()}
        />
        <StatCard
          label="Total Spending"
          value={`$${data.categories.reduce((s, c) => s + c.total, 0).toFixed(2)}`}
        />
        <StatCard
          label="Categories"
          value={data.categories.length.toString()}
        />
        <StatCard
          label="Top Category"
          value={data.categories[0]?.category ?? "—"}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SpendingPieChart data={data.categories} />
        <MonthlyBarChart data={data.monthly} />
      </div>
      <DailyLineChart data={data.daily} />

      {/* AI / Rule-Based Advice */}
      <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
        <h2 className="text-lg font-semibold mb-3 text-emerald-400">
          🤖 Financial Advisor
        </h2>
        <div className="text-slate-300 text-sm whitespace-pre-wrap leading-relaxed">
          {data.advice}
        </div>
      </div>

      {/* Transaction Table */}
      <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-slate-200">Transactions</h2>
          <span className="text-slate-500 text-sm">
            {data.transactions.length} total
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-slate-400 border-b border-slate-700">
                <th className="text-left py-2 pr-4">Date</th>
                <th className="text-left py-2 pr-4">Description</th>
                <th className="text-left py-2 pr-4">Category</th>
                <th className="text-right py-2">Amount</th>
              </tr>
            </thead>
            <tbody>
              {paginatedTx.map((tx, i) => (
                <tr
                  key={i}
                  className="border-b border-slate-700/50 hover:bg-slate-700/30 transition-colors"
                >
                  <td className="py-2 pr-4 text-slate-400">{tx.date}</td>
                  <td className="py-2 pr-4 text-slate-300 max-w-xs truncate">
                    {tx.description}
                  </td>
                  <td className="py-2 pr-4">
                    <span className="bg-slate-700 text-emerald-400 text-xs px-2 py-0.5 rounded-full">
                      {tx.category}
                    </span>
                  </td>
                  <td
                    className={`py-2 text-right font-mono ${
                      tx.amount < 0 ? "text-emerald-400" : "text-slate-200"
                    }`}
                  >
                    {tx.amount < 0 ? "+" : ""}${Math.abs(tx.amount).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-4 text-sm text-slate-400">
            <button
              onClick={() => setTxPage((p) => Math.max(0, p - 1))}
              disabled={txPage === 0}
              className="px-3 py-1 bg-slate-700 rounded disabled:opacity-40 hover:bg-slate-600 transition-colors"
            >
              ← Prev
            </button>
            <span>
              Page {txPage + 1} of {totalPages}
            </span>
            <button
              onClick={() => setTxPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={txPage === totalPages - 1}
              className="px-3 py-1 bg-slate-700 rounded disabled:opacity-40 hover:bg-slate-600 transition-colors"
            >
              Next →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-800 rounded-2xl p-4 border border-slate-700">
      <p className="text-slate-500 text-xs mb-1">{label}</p>
      <p className="text-xl font-bold text-slate-100 truncate">{value}</p>
    </div>
  );
}
