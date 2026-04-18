"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

interface Props {
  data: { date: string; total: number }[];
}

export default function DailyLineChart({ data }: Props) {
  if (!data.length) return null;

  const avg = data.reduce((s, d) => s + d.total, 0) / data.length;

  return (
    <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
      <h2 className="text-lg font-semibold mb-1 text-slate-200">
        Daily Cash Flow
      </h2>
      <p className="text-slate-500 text-xs mb-4">
        Outgoing spend per day — spikes highlight unusual activity.
      </p>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey="date"
            tick={{ fill: "#94a3b8", fontSize: 11 }}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: "#94a3b8", fontSize: 12 }}
            tickFormatter={(v) => `$${v}`}
          />
          <Tooltip
            contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }}
            formatter={(value: number) => [`$${value.toFixed(2)}`, "Spent"]}
          />
          <ReferenceLine
            y={avg}
            stroke="#f59e0b"
            strokeDasharray="4 4"
            label={{ value: "Avg", fill: "#f59e0b", fontSize: 11 }}
          />
          <Line
            type="monotone"
            dataKey="total"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
