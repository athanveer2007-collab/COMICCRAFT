import React from "react";
import { Smile, Flame, Feather, Laugh } from "lucide-react";
import { cn } from "@/lib/utils";

interface ToneCardProps {
  name: string;
  isSelected: boolean;
  onSelect: (name: string) => void;
}

const TONE_INFO: Record<
  string,
  { icon: React.ComponentType<{ className?: string }>; description: string }
> = {
  "Light-hearted": {
    icon: Smile,
    description: "Cheerful, warm discoveries, optimistic resolution",
  },
  Dramatic: {
    icon: Flame,
    description: "High tension, intense emotional beats, bold climax",
  },
  Poetic: {
    icon: Feather,
    description: "Lyrical, introspective, contemplative atmosphere",
  },
  Funny: {
    icon: Laugh,
    description: "Witty banter, comedic timing, punchy twist",
  },
};

export function ToneCard({ name, isSelected, onSelect }: ToneCardProps): React.JSX.Element {
  const info = TONE_INFO[name] || TONE_INFO["Dramatic"];
  const IconComponent = info.icon;

  return (
    <button
      type="button"
      onClick={() => onSelect(name)}
      className={cn(
        "flex items-center gap-3 p-3.5 rounded-xl border text-left transition-all duration-150 cursor-pointer focus:outline-none focus:ring-2 focus:ring-indigo-500",
        isSelected
          ? "border-indigo-500 bg-indigo-500/10 text-indigo-300 ring-1 ring-indigo-500/30"
          : "border-slate-800 bg-slate-900/60 text-slate-300 hover:border-slate-700 hover:bg-slate-900"
      )}
    >
      <div
        className={cn(
          "w-8 h-8 rounded-lg flex items-center justify-center shrink-0",
          isSelected ? "bg-indigo-600 text-white" : "bg-slate-800 text-slate-400"
        )}
      >
        <IconComponent className="w-4 h-4" />
      </div>
      <div>
        <div className="font-semibold text-sm">{name}</div>
        <div className="text-xs text-slate-400 line-clamp-1">{info.description}</div>
      </div>
    </button>
  );
}
