import React from "react";
import type { PanelResponse } from "@/api/types";
import { MessageSquare, Sparkles } from "lucide-react";

interface ComicPanelCardProps {
  panel: PanelResponse;
  totalPanels?: number;
}

export function ComicPanelCard({
  panel,
  totalPanels = 5,
}: ComicPanelCardProps): React.JSX.Element {
  return (
    <article className="rounded-3xl border border-slate-800 bg-slate-900/80 overflow-hidden shadow-xl shadow-black/40 flex flex-col transition hover:border-slate-700">
      {/* Panel Header */}
      <div className="px-5 py-3.5 border-b border-slate-800 flex items-center justify-between bg-slate-950/40">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            Panel {panel.panel} of {totalPanels}
          </span>
          <h3 className="font-bold text-slate-100 text-base">{panel.title}</h3>
        </div>
      </div>

      {/* Artwork Illustration */}
      <div className="relative aspect-[4/3] w-full bg-slate-950 flex items-center justify-center overflow-hidden group">
        {panel.image_url ? (
          <img
            src={panel.image_url}
            alt={panel.title}
            className="w-full h-full object-cover object-center group-hover:scale-[1.02] transition-transform duration-300"
            loading="lazy"
          />
        ) : (
          <div className="flex flex-col items-center justify-center text-slate-500 p-6 text-center">
            <Sparkles className="w-8 h-8 text-slate-600 mb-2 animate-pulse" />
            <span className="text-sm font-medium">Artwork in generation...</span>
          </div>
        )}
      </div>

      {/* Narrative & Dialogue Content */}
      <div className="p-5 flex-1 flex flex-col gap-3.5">
        {/* Scene Description */}
        {panel.scene_description && (
          <p className="text-xs italic text-slate-400 border-l-2 border-slate-700 pl-3">
            {panel.scene_description}
          </p>
        )}

        {/* Caption */}
        {panel.caption && (
          <div className="px-3.5 py-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs font-semibold">
            <span className="uppercase tracking-wider text-[10px] text-amber-400 block mb-0.5">
              Caption
            </span>
            {panel.caption}
          </div>
        )}

        {/* Narration */}
        {panel.narration && (
          <div className="px-3.5 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-200 text-xs leading-relaxed">
            <span className="uppercase tracking-wider text-[10px] text-slate-400 font-bold block mb-0.5">
              Narrator
            </span>
            {panel.narration}
          </div>
        )}

        {/* Dialogue Bubbles */}
        {panel.dialogue && panel.dialogue.length > 0 && (
          <div className="mt-1 flex flex-col gap-2.5">
            {panel.dialogue.map((d, dIdx) => (
              <div key={dIdx} className="speech-bubble bg-indigo-950/60 border border-indigo-500/30 p-3 rounded-2xl">
                <div className="flex items-center gap-1.5 text-[11px] font-bold text-indigo-400 mb-1">
                  <MessageSquare className="w-3 h-3" />
                  <span>{d.speaker}</span>
                </div>
                <p className="text-xs text-slate-100 font-medium leading-relaxed">
                  &ldquo;{d.text}&rdquo;
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </article>
  );
}
