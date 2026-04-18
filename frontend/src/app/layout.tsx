import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MyMoney – Personal Finance Tracker",
  description: "Upload your bank statements and get AI-powered spending insights.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-900 text-slate-100">
        <nav className="border-b border-slate-700 bg-slate-800/80 backdrop-blur">
          <div className="mx-auto max-w-6xl px-4 py-3 flex items-center gap-6">
            <span className="text-xl font-bold text-emerald-400">💰 MyMoney</span>
            <a href="/" className="text-slate-300 hover:text-white text-sm transition-colors">
              Home
            </a>
            <a href="/upload" className="text-slate-300 hover:text-white text-sm transition-colors">
              Upload
            </a>
          </div>
        </nav>
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
