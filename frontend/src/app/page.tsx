import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] text-center gap-8">
      <div>
        <h1 className="text-5xl font-extrabold text-emerald-400 mb-4">
          MyMoney
        </h1>
        <p className="text-xl text-slate-400 max-w-2xl">
          Your zero-cost personal finance tracker. Upload a bank statement CSV or
          Excel file and instantly visualise where your money goes — powered by
          AI-driven insights.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full max-w-3xl">
        <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
          <div className="text-3xl mb-3">📂</div>
          <h2 className="font-semibold text-lg mb-1">Upload</h2>
          <p className="text-slate-400 text-sm">
            Import CSV or Excel bank statements in seconds.
          </p>
        </div>
        <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
          <div className="text-3xl mb-3">📊</div>
          <h2 className="font-semibold text-lg mb-1">Visualise</h2>
          <p className="text-slate-400 text-sm">
            Interactive charts — pie, bar and time-series graphs.
          </p>
        </div>
        <div className="bg-slate-800 rounded-2xl p-6 border border-slate-700">
          <div className="text-3xl mb-3">🤖</div>
          <h2 className="font-semibold text-lg mb-1">Advise</h2>
          <p className="text-slate-400 text-sm">
            AI advisor (Ollama) or rule-based 50/30/20 fallback tips.
          </p>
        </div>
      </div>

      <Link
        href="/upload"
        className="bg-emerald-500 hover:bg-emerald-400 text-white font-semibold px-8 py-3 rounded-xl transition-colors text-lg"
      >
        Get Started →
      </Link>
    </div>
  );
}
