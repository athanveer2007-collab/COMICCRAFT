import React, { useEffect } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { Sparkles, AlertCircle, ArrowLeft, Image as ImageIcon } from "lucide-react";
import { useComicEvents } from "@/hooks/useComicEvents";
import { GenerationStepper } from "@/components/stepper/GenerationStepper";

export function GeneratingPage(): React.JSX.Element {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { stage, progress, message, panels, isCompleted, isFailed, error } =
    useComicEvents(id);

  // When pipeline reaches 'ready' stage, smoothly transition to Preview Page
  useEffect(() => {
    if (isCompleted && id) {
      const timer = setTimeout(() => {
        navigate(`/comics/${id}`);
      }, 1200);
      return () => clearTimeout(timer);
    }
  }, [isCompleted, id, navigate]);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex flex-col items-center">
      {/* Header */}
      <div className="text-center mb-10 max-w-2xl">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-3">
          <Sparkles className="w-3.5 h-3.5 animate-spin" />
          <span>Real-Time AI Pipeline</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-100 tracking-tight">
          Bringing Your Comic to Life
        </h1>
        <p
          aria-live="polite"
          className="mt-2 text-sm sm:text-base text-slate-300 font-medium"
        >
          {message}
        </p>
      </div>

      {/* Failure State */}
      {isFailed && (
        <div
          role="alert"
          className="w-full max-w-xl mb-8 p-6 rounded-3xl bg-rose-500/10 border border-rose-500/30 text-rose-300 flex flex-col items-center text-center gap-4 shadow-xl"
        >
          <div className="w-12 h-12 rounded-2xl bg-rose-500/20 flex items-center justify-center text-rose-400">
            <AlertCircle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-base text-rose-200">Generation Halted</h3>
            <p className="mt-1 text-xs text-rose-300/90">{error || "An error occurred during generation."}</p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/"
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 transition"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Create</span>
            </Link>
          </div>
        </div>
      )}

      {/* Stepper */}
      <div className="w-full mb-12">
        <GenerationStepper stage={stage} progress={progress} />
      </div>

      {/* 5-Panel Live Preview / Skeleton Grid */}
      <div className="w-full">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400">
            Live Panel Canvas (5 Panels)
          </h3>
          <span className="text-xs text-indigo-400 font-semibold">
            {Object.keys(panels).length} / 5 Ready
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {[1, 2, 3, 4, 5].map((idx) => {
            const pData = panels[idx];
            return (
              <div
                key={idx}
                className="aspect-[4/3] rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden relative shadow-md flex flex-col justify-end p-3 transition-all duration-300"
              >
                {pData?.image_url ? (
                  <>
                    <img
                      src={pData.image_url}
                      alt={pData.title || `Panel ${idx}`}
                      className="absolute inset-0 w-full h-full object-cover animate-in fade-in zoom-in-95 duration-500"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent" />
                    <div className="relative z-10">
                      <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/80 text-white inline-block mb-1">
                        Panel {idx}
                      </span>
                      <p className="text-xs font-bold text-white truncate">{pData.title}</p>
                    </div>
                  </>
                ) : (
                  <div className="h-full w-full flex flex-col items-center justify-center text-slate-500 gap-2">
                    <div className="w-10 h-10 rounded-xl bg-slate-800/80 flex items-center justify-center">
                      <ImageIcon className="w-5 h-5 text-slate-600 animate-pulse" />
                    </div>
                    <span className="text-[11px] font-medium text-slate-500">Panel {idx}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
