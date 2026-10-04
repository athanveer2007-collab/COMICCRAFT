import React from "react";
import { Sparkles, Gamepad2, BookOpen, Camera, Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface ArtStyleCardProps {
  id: string;
  name: string;
  description: string;
  isSelected: boolean;
  onSelect: (name: string) => void;
}

const STYLE_METADATA: Record<
  string,
  { icon: React.ComponentType<{ className?: string }>; gradient: string; preview: string }
> = {
  Anime: {
    icon: Sparkles,
    gradient: "from-pink-500 via-rose-500 to-amber-500",
    preview: "Vibrant cel shading, dramatic lighting, Makoto Shinkai aesthetic",
  },
  "Pixel Art": {
    icon: Gamepad2,
    gradient: "from-emerald-500 via-teal-500 to-cyan-500",
    preview: "16-bit nostalgic retro sprite palette with crisp pixel clusters",
  },
  "Comic Book": {
    icon: BookOpen,
    gradient: "from-amber-500 via-orange-500 to-red-500",
    preview: "Bold black ink outlines, Ben-Day dot halftone, dynamic shadows",
  },
  Realistic: {
    icon: Camera,
    gradient: "from-indigo-500 via-purple-500 to-blue-500",
    preview: "Cinematic depth of field, photorealistic skin textures and lighting",
  },
};

export function ArtStyleCard({
  name,
  description,
  isSelected,
  onSelect,
}: ArtStyleCardProps): React.JSX.Element {
  const meta = STYLE_METADATA[name] || STYLE_METADATA.Anime;
  const IconComponent = meta.icon;

  return (
    <button
      type="button"
      onClick={() => onSelect(name)}
      className={cn(
        "relative text-left p-4 rounded-2xl border transition-all duration-200 cursor-pointer overflow-hidden group focus:outline-none focus:ring-2 focus:ring-indigo-500",
        isSelected
          ? "border-indigo-500 bg-slate-900 shadow-lg shadow-indigo-500/10 ring-1 ring-indigo-500/50"
          : "border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900/90"
      )}
    >
      <div className={cn("h-1.5 w-full absolute top-0 left-0 bg-gradient-to-r", meta.gradient)} />

      <div className="flex items-start justify-between">
        <div
          className={cn(
            "w-9 h-9 rounded-xl flex items-center justify-center bg-gradient-to-tr text-white shadow-md",
            meta.gradient
          )}
        >
          <IconComponent className="w-4 h-4" />
        </div>

        {isSelected && (
          <span className="w-5 h-5 rounded-full bg-indigo-500 text-white flex items-center justify-center">
            <Check className="w-3 h-3 stroke-[3]" />
          </span>
        )}
      </div>

      <div className="mt-3">
        <h4 className="font-bold text-slate-100 text-sm group-hover:text-indigo-400 transition-colors">
          {name}
        </h4>
        <p className="mt-1 text-xs text-slate-400 line-clamp-2 leading-relaxed">
          {description || meta.preview}
        </p>
      </div>
    </button>
  );
}
