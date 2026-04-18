"use client";

import { useSearchParams } from "next/navigation";
import Dashboard from "@/components/Dashboard";
import Link from "next/link";

export default function DashboardClient() {
  const params = useSearchParams();
  const fileId = params.get("file_id");

  if (!fileId) {
    return (
      <div className="flex flex-col items-center gap-4 py-16 text-center">
        <p className="text-slate-400">No data uploaded yet.</p>
        <Link
          href="/upload"
          className="bg-emerald-500 hover:bg-emerald-400 text-white font-semibold px-6 py-2 rounded-xl transition-colors"
        >
          Upload a statement
        </Link>
      </div>
    );
  }

  return <Dashboard fileId={fileId} />;
}
