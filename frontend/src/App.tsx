import React, { useEffect, useState } from "react";
import { Sparkles, Palette, CheckCircle2, AlertCircle } from "lucide-react";
import { fetchHealth, type HealthData } from "@/api/client";

export function App(): React.JSX.Element {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setHealth(data);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Navigation Bar */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-rose-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Palette className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="comic-title text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-amber-400 via-rose-400 to-indigo-400">
                COMICCRAFT
              </span>
              <span className="hidden sm:inline-block ml-2 text-xs font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                Production AI
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {loading ? (
              <span className="text-xs text-slate-400 flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
                Connecting API...
              </span>
            ) : error ? (
              <span className="text-xs text-rose-400 flex items-center gap-1.5 bg-rose-500/10 px-2.5 py-1 rounded-md border border-rose-500/20">
                <AlertCircle className="w-3.5 h-3.5" />
                API Offline ({error})
              </span>
            ) : (
              <span className="text-xs text-emerald-400 flex items-center gap-1.5 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/20">
                <CheckCircle2 className="w-3.5 h-3.5" />
                API v{health?.version} Connected
              </span>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex flex-col items-center justify-center text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 mb-6 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>Transform any idea into a professional 5-panel comic</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight max-w-3xl leading-tight sm:leading-tight">
          AI Comic Generator with{" "}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-400 via-rose-400 to-indigo-400">
            Character Consistency
          </span>
        </h1>

        <p className="mt-4 text-base sm:text-lg text-slate-400 max-w-2xl">
          ComicCraft orchestrates structured Gemini narrative scripts, bounded concurrent image generation, real-time SSE progress, and publication-ready PDF export.
        </p>

        <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-3xl text-left">
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition">
            <h3 className="font-semibold text-slate-200">5-Panel Structured Arc</h3>
            <p className="mt-1 text-xs text-slate-400">
              Coherent story outline, dialogue bubbles, and narration dynamically orchestrated.
            </p>
          </div>
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition">
            <h3 className="font-semibold text-slate-200">Character Sheets</h3>
            <p className="mt-1 text-xs text-slate-400">
              Canonical visual attributes ensure character continuity across every panel.
            </p>
          </div>
          <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition">
            <h3 className="font-semibold text-slate-200">Professional PDF</h3>
            <p className="mt-1 text-xs text-slate-400">
              Multi-page publication layout built with ReportLab ready for print or sharing.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        <p>ComicCraft &copy; 2026. Production-Grade AI Comic Generation Platform.</p>
      </footer>
    </div>
  );
}

export default App;
