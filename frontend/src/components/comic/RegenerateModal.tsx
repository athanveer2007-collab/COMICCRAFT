import React, { useState } from "react";
import { RefreshCw, X, Palette, Flame } from "lucide-react";
import { ArtStyleCard } from "./ArtStyleCard";
import { ToneCard } from "./ToneCard";

interface RegenerateModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentTone: string;
  currentStyle: string;
  onConfirm: (newTone: string, newStyle: string) => void;
  isSubmitting: boolean;
}

const TONES = ["Light-hearted", "Dramatic", "Poetic", "Funny"];
const STYLES = ["Anime", "Pixel Art", "Comic Book", "Realistic"];

export function RegenerateModal({
  isOpen,
  onClose,
  currentTone,
  currentStyle,
  onConfirm,
  isSubmitting,
}: RegenerateModalProps): React.JSX.Element | null {
  const [selectedTone, setSelectedTone] = useState<string>(currentTone);
  const [selectedStyle, setSelectedStyle] = useState<string>(currentStyle);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onConfirm(selectedTone, selectedStyle);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="regenerate-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200"
    >
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl overflow-y-auto max-h-[90vh]">
        <button
          type="button"
          onClick={onClose}
          aria-label="Close modal"
          className="absolute top-5 right-5 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center">
            <RefreshCw className="w-5 h-5" />
          </div>
          <div>
            <h3 id="regenerate-modal-title" className="text-xl font-bold text-slate-100">
              Regenerate Comic
            </h3>
            <p className="text-xs text-slate-400">
              Choose a different tone and art style to re-craft the story and illustrations.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          {/* Tone selection */}
          <div>
            <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
              <Flame className="w-4 h-4 text-amber-400" />
              <span>Select New Tone</span>
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
              {TONES.map((t) => (
                <ToneCard
                  key={t}
                  name={t}
                  isSelected={selectedTone === t}
                  onSelect={setSelectedTone}
                />
              ))}
            </div>
          </div>

          {/* Art Style selection */}
          <div>
            <label className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
              <Palette className="w-4 h-4 text-indigo-400" />
              <span>Select New Visual Art Style</span>
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {STYLES.map((st) => (
                <ArtStyleCard
                  key={st}
                  id={st}
                  name={st}
                  description=""
                  isSelected={selectedStyle === st}
                  onSelect={setSelectedStyle}
                />
              ))}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800 text-xs font-semibold transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-600 hover:from-amber-400 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-500/20 transition flex items-center gap-2 disabled:opacity-50"
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Submitting...</span>
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4" />
                  <span>Start Regeneration</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
