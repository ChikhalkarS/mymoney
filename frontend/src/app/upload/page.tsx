import FileUpload from "@/components/FileUpload";

export default function UploadPage() {
  return (
    <div className="flex flex-col items-center gap-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-emerald-400 mb-2">Upload Bank Statement</h1>
        <p className="text-slate-400">
          Upload a CSV or Excel file exported from your bank to get started.
        </p>
      </div>
      <FileUpload />
    </div>
  );
}
