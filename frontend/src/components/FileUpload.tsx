"use client";

import { useState, useRef, DragEvent, ChangeEvent } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function FileUpload() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const acceptedTypes = [
    "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/pdf",
  ];

  const handleFile = (f: File) => {
    setError(null);
    if (!acceptedTypes.includes(f.type) && !f.name.match(/\.(csv|xls|xlsx|pdf)$/i)) {
      setError("Only CSV (.csv), Excel (.xls / .xlsx), and PDF (.pdf) files are supported.");
      return;
    }
    setFile(f);
  };

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) handleFile(dropped);
  };

  const onInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) handleFile(selected);
  };

  const onUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const { data } = await axios.post(`${API_BASE}/api/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      router.push(`/dashboard?file_id=${data.file_id}`);
    } catch (err: unknown) {
      const message =
        axios.isAxiosError(err) && err.response?.data?.detail
          ? err.response.data.detail
          : "Upload failed. Make sure the backend is running on port 8000.";
      setError(message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-6 w-full max-w-xl mx-auto">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
        className={`w-full border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-colors ${
          isDragging
            ? "border-emerald-400 bg-emerald-400/10"
            : "border-slate-600 bg-slate-800 hover:border-emerald-500"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xls,.xlsx,.pdf"
          className="hidden"
          onChange={onInputChange}
        />
        <div className="text-5xl mb-4">📁</div>
        {file ? (
          <p className="text-emerald-400 font-medium">{file.name}</p>
        ) : (
          <>
            <p className="text-slate-300 font-medium">
              Drag &amp; drop your bank statement here
            </p>
            <p className="text-slate-500 text-sm mt-1">
              or click to browse &mdash; CSV, XLS, XLSX, PDF
            </p>
          </>
        )}
      </div>

      {error && (
        <div className="w-full bg-red-900/40 border border-red-500 text-red-300 rounded-xl px-4 py-3 text-sm">
          ⚠️ {error}
        </div>
      )}

      <button
        onClick={onUpload}
        disabled={!file || uploading}
        className="w-full bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors"
      >
        {uploading ? "Uploading…" : "Analyse My Spending"}
      </button>

      <div className="text-slate-500 text-xs text-center">
        <p className="font-medium text-slate-400 mb-1">Expected CSV / Excel columns:</p>
        <code className="bg-slate-800 px-2 py-1 rounded">date, description, amount</code>
        <p className="mt-1">PDF bank statements are also supported. All data is processed locally.</p>
      </div>
    </div>
  );
}
