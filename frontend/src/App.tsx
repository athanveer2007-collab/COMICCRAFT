import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { Navbar } from "@/components/layout/Navbar";
import { CreatePage } from "@/pages/CreatePage";
import { GeneratingPage } from "@/pages/GeneratingPage";
import { PreviewPage } from "@/pages/PreviewPage";
import { ExportSuccessPage } from "@/pages/ExportSuccessPage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export function App(): React.JSX.Element {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white antialiased transition-colors">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<CreatePage />} />
              <Route path="/comics/:id/generating" element={<GeneratingPage />} />
              <Route path="/comics/:id" element={<PreviewPage />} />
              <Route path="/comics/:id/export-success" element={<ExportSuccessPage />} />
            </Routes>
          </main>
          <footer className="border-t border-slate-800/80 py-8 text-center text-xs text-slate-500 bg-slate-950/60 backdrop-blur-sm">
            <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
              <span className="comic-title text-base text-slate-400">COMICCRAFT</span>
              <p>ComicCraft &copy; 2026. Production-Grade AI Comic Generation Platform.</p>
              <div className="flex items-center gap-4 text-slate-400">
                <span>FastAPI + React 19</span>
                <span>&bull;</span>
                <span>ReportLab PDF</span>
              </div>
            </div>
          </footer>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
