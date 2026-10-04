import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Palette, Moon, Sun, Plus, CheckCircle2, AlertCircle } from "lucide-react";
import { fetchHealth, type HealthData } from "@/api/client";

export function Navbar(): React.JSX.Element {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [isDark, setIsDark] = useState<boolean>(() => {
    return localStorage.getItem("comiccraft-theme") !== "light";
  });

  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add("dark");
      localStorage.setItem("comiccraft-theme", "dark");
    } else {
      root.classList.remove("dark");
      localStorage.setItem("comiccraft-theme", "light");
    }
  }, [isDark]);

  return (
    <header className="border-b border-slate-800 bg-slate-900/70 backdrop-blur-md sticky top-0 z-50 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 group focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-lg p-1">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-rose-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <Palette className="w-5 h-5 text-white" />
          </div>
          <div className="flex flex-col">
            <span className="comic-title text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-amber-400 via-rose-400 to-indigo-400 tracking-wider">
              COMICCRAFT
            </span>
          </div>
        </Link>

        <div className="flex items-center gap-3">
          {health ? (
            <span className="hidden sm:inline-flex items-center gap-1.5 text-xs font-medium text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
              <CheckCircle2 className="w-3.5 h-3.5" />
              API v{health.version} Online
            </span>
          ) : (
            <span className="hidden sm:inline-flex items-center gap-1.5 text-xs font-medium text-rose-400 bg-rose-500/10 px-2.5 py-1 rounded-full border border-rose-500/20">
              <AlertCircle className="w-3.5 h-3.5" />
              Connecting...
            </span>
          )}

          <Link
            to="/"
            className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-500/20 transition focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
            <Plus className="w-3.5 h-3.5" />
            <span className="hidden xs:inline">New Comic</span>
          </Link>

          <button
            type="button"
            onClick={() => setIsDark(!isDark)}
            aria-label="Toggle color theme"
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition focus:outline-none focus:ring-2 focus:ring-indigo-400"
          >
            {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-indigo-400" />}
          </button>
        </div>
      </div>
    </header>
  );
}
