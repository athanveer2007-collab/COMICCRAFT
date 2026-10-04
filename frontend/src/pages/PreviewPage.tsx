import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { Download, RefreshCw, FileText, ArrowLeft, Loader2, Sparkles, User, Palette } from "lucide-react";

import { exportComicPdf, getComic, regenerateComic } from "@/api/client";
import type { ComicResponse } from "@/api/types";
import { ComicPanelCard } from "@/components/comic/ComicPanelCard";
import { RegenerateModal } from "@/components/comic/RegenerateModal";

export function PreviewPage(): React.JSX.Element {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [comic, setComic] = useState<ComicResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [isRegenerateOpen, setIsRegenerateOpen] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [isRegenerating, setIsRegenerating] = useState<boolean>(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getComic(id)
      .then((data) => {
        setComic(data);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  const handleDownloadPdf = async () => {
    if (!id) return;
    setIsExporting(true);
    try {
      const res = await exportComicPdf(id);
      navigate(`/comics/${id}/export-success`, { state: { pdfUrl: res.pdf_url } });
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to compile PDF");
      setIsExporting(false);
    }
  };

  const handleConfirmRegenerate = async (newTone: string, newStyle: string) => {
    if (!id) return;
    setIsRegenerating(true);
    try {
      await regenerateComic(id, { tone: newTone, art_style: newStyle });
      navigate(`/comics/${id}/generating`);
    } catch (err: unknown) {
      alert(err instanceof Error ? err.message : "Failed to trigger regeneration");
      setIsRegenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center gap-4 text-center">
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        <p className="text-sm font-semibold text-slate-400">Loading your comic preview...</p>
      </div>
    );
  }

  if (error || !comic) {
    return (
      <div className="max-w-md mx-auto my-20 p-8 rounded-3xl bg-slate-900 border border-slate-800 text-center flex flex-col items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-rose-500/10 text-rose-400 flex items-center justify-center">
          <FileText className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-slate-100">Comic Not Found</h2>
        <p className="text-xs text-slate-400">{error || "The requested comic could not be found."}</p>
        <Link
          to="/"
          className="mt-2 px-5 py-2.5 rounded-xl bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500 transition"
        >
          Back to Creator
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 pb-28">
      {/* Top Breadcrumb & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <Link
          to="/"
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-400 hover:text-slate-200 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Create Another Comic</span>
        </Link>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setIsRegenerateOpen(true)}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 shadow-sm transition"
          >
            <RefreshCw className="w-4 h-4 text-indigo-400" />
            <span>Regenerate Style/Tone</span>
          </button>

          <button
            type="button"
            onClick={handleDownloadPdf}
            disabled={isExporting}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-600 hover:from-amber-400 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-500/20 transition disabled:opacity-50"
          >
            {isExporting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Preparing PDF...</span>
              </>
            ) : (
              <>
                <Download className="w-4 h-4" />
                <span>Download PDF</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Comic Header Banner */}
      <section className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 sm:p-8 mb-10 shadow-xl">
        <div className="flex flex-wrap items-center gap-2 mb-3">
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            {comic.art_style}
          </span>
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
            {comic.tone}
          </span>
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            {comic.custom_setting || comic.setting}
          </span>
        </div>

        <h1 className="text-3xl sm:text-5xl font-extrabold text-slate-100 tracking-tight">
          {comic.title || "Untitled Comic"}
        </h1>

        {comic.synopsis && (
          <p className="mt-3 text-sm sm:text-base text-slate-300 max-w-4xl italic leading-relaxed">
            &ldquo;{comic.synopsis}&rdquo;
          </p>
        )}

        {/* Character Visual Identity Card */}
        {comic.character_sheet && (
          <div className="mt-6 pt-6 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="flex items-start gap-2.5">
              <User className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-slate-300 block">Protagonist</span>
                <span className="text-slate-400">{comic.character_sheet.name} ({comic.character_sheet.age_presentation})</span>
              </div>
            </div>
            <div className="flex items-start gap-2.5">
              <Palette className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-slate-300 block">Visual Colors</span>
                <span className="text-slate-400">{comic.character_sheet.primary_colors.join(", ")}</span>
              </div>
            </div>
            <div className="flex items-start gap-2.5">
              <Sparkles className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold text-slate-300 block">Signature Outfit</span>
                <span className="text-slate-400 truncate block">{comic.character_sheet.outfit}</span>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* 5-Panel Display */}
      <section className="flex flex-col gap-10">
        {comic.panels && comic.panels.length > 0 ? (
          comic.panels.map((panel) => (
            <ComicPanelCard key={panel.panel} panel={panel} totalPanels={comic.panels?.length || 5} />
          ))
        ) : (
          <div className="text-center py-12 text-slate-500">No panels available for this comic.</div>
        )}
      </section>

      {/* Floating Action Bar on Mobile */}
      <div className="sm:hidden fixed bottom-4 inset-x-4 z-40 bg-slate-900/90 backdrop-blur-md border border-slate-800 p-3 rounded-2xl flex items-center justify-between shadow-2xl">
        <button
          type="button"
          onClick={() => setIsRegenerateOpen(true)}
          className="px-4 py-2.5 rounded-xl bg-slate-800 text-slate-200 text-xs font-bold"
        >
          Regenerate
        </button>
        <button
          type="button"
          onClick={handleDownloadPdf}
          disabled={isExporting}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 text-white text-xs font-bold shadow-md"
        >
          {isExporting ? "Exporting..." : "Download PDF"}
        </button>
      </div>

      {/* Regeneration Modal */}
      <RegenerateModal
        isOpen={isRegenerateOpen}
        onClose={() => setIsRegenerateOpen(false)}
        currentTone={comic.tone}
        currentStyle={comic.art_style}
        onConfirm={handleConfirmRegenerate}
        isSubmitting={isRegenerating}
      />
    </div>
  );
}
