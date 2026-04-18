import { Suspense } from "react";
import DashboardClient from "./DashboardClient";

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-3xl font-bold text-emerald-400 mb-1">Dashboard</h1>
        <p className="text-slate-400 text-sm">
          Your personalised spending breakdown and financial advice.
        </p>
      </div>
      <Suspense
        fallback={
          <div className="flex items-center justify-center h-64 text-emerald-400 animate-pulse">
            Loading dashboard…
          </div>
        }
      >
        <DashboardClient />
      </Suspense>
    </div>
  );
}
