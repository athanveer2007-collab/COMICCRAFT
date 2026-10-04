import React from "react";
import { useParams, useLocation, Link } from "react-router-dom";
import { CheckCircle2, Download, Plus, Eye, Sparkles, BookOpen } from "lucide-react";

export function ExportSuccessPage(): React.JSX.Element {
  const { id } = useParams<{ id: string }>();
  const location = useLocation();

  const pdfUrl = (location.state as { pdfUrl?: string })?.pdfUrl || `/api/v1/comics/${id}/pdf`;

  return (
    <div className="max-w-2xl mx-auto px-4 py-16 text-center flex flex-col items-center">
      {/* Celebration Icon */}
      <div className="relative mb-6">
        <div className="w-20 h-20 rounded-3xl bg-gradient-to-tr from-emerald-500 via-teal-500 to-indigo-600 flex items-center justify-center text-white shadow-xl shadow-emerald-500/20">
          <CheckCircle2 className="w-10 h-10" />
        </div>
        <div className="absolute -top-1 -right-1 w-6 h-6 rounded-full bg-amber-400 flex items-center justify-center text-slate-950 shadow-md">
          <Sparkles className="w-3.5 h-3.5 fill-current" />
        </div>
      </div>

      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-3">
        <span>Publication Ready</span>
      </div>

      <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-100 tracking-tight">
        Your Comic PDF is Ready!
      </h1>

      <p className="mt-3 text-slate-400 text-sm sm:text-base max-w-lg">
        The multi-page publication PDF with title cover, character metadata, high-resolution artwork, and dialogue has been generated.
      </p>

      {/* Main Download Card */}
      <div className="w-full mt-8 p-6 rounded-3xl bg-slate-900 border border-slate-800 shadow-xl flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 text-left">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center shrink-0">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <h4 className="font-bold text-slate-100 text-sm">ComicCraft Storybook</h4>
            <span className="text-xs text-slate-400">Standard Letter Format &bull; 6 Pages</span>
          </div>
        </div>

        <a
          href={pdfUrl}
          download
          className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-600 hover:from-amber-400 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-500/20 flex items-center justify-center gap-2 transition"
        >
          <Download className="w-4 h-4" />
          <span>Download PDF</span>
        </a>
      </div>

      {/* Alternative Navigation Actions */}
      <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
        <Link
          to={`/comics/${id}`}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition"
        >
          <Eye className="w-4 h-4" />
          <span>View Comic Strips</span>
        </Link>

        <Link
          to="/"
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition"
        >
          <Plus className="w-4 h-4" />
          <span>Create Another Comic</span>
        </Link>
      </div>
    </div>
  );
}
