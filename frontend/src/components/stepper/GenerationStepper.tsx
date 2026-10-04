import React from "react";
import { Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface GenerationStepperProps {
  stage: string;
  progress: number;
}

interface StepItem {
  id: string;
  title: string;
  subtitle: string;
  stageTrigger: string[];
}

const STEPS: StepItem[] = [
  {
    id: "outline",
    title: "Character Identity & Outline",
    subtitle: "Designing canonical character visual traits",
    stageTrigger: ["outline", "story", "images", "image_panel_1", "image_panel_2", "image_panel_3", "image_panel_4", "image_panel_5", "layout", "ready"],
  },
  {
    id: "story",
    title: "Narration & Dialogue",
    subtitle: "Drafting 5-panel story arc and speech bubbles",
    stageTrigger: ["story", "images", "image_panel_1", "image_panel_2", "image_panel_3", "image_panel_4", "image_panel_5", "layout", "ready"],
  },
  {
    id: "images",
    title: "Panel Artwork Illustrations",
    subtitle: "Bounded concurrent generation across 5 panels",
    stageTrigger: ["images", "image_panel_1", "image_panel_2", "image_panel_3", "image_panel_4", "image_panel_5", "layout", "ready"],
  },
  {
    id: "layout",
    title: "Comic Layout & PDF Compilation",
    subtitle: "ReportLab multi-page document synthesis",
    stageTrigger: ["layout", "ready"],
  },
  {
    id: "ready",
    title: "Comic Ready",
    subtitle: "5 illustrated panels and PDF download ready",
    stageTrigger: ["ready"],
  },
];

export function GenerationStepper({
  stage,
  progress,
}: GenerationStepperProps): React.JSX.Element {
  return (
    <div className="w-full max-w-xl mx-auto flex flex-col gap-6">
      {/* Real-time Progress Bar */}
      <div className="flex flex-col gap-2">
        <div className="flex justify-between items-center text-xs font-semibold text-slate-400">
          <span className="uppercase tracking-wider">Progress</span>
          <span className="text-indigo-400 font-bold">{progress}%</span>
        </div>
        <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden p-0.5 border border-slate-700/50">
          <div
            className="h-full bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-500 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${Math.max(5, Math.min(100, progress))}%` }}
          />
        </div>
      </div>

      {/* Step items */}
      <div className="flex flex-col gap-3">
        {STEPS.map((step, idx) => {
          const isDone = step.stageTrigger.slice(1).includes(stage) || stage === "ready";
          const isCurrent = step.stageTrigger.includes(stage) && !isDone;

          return (
            <div
              key={step.id}
              className={cn(
                "flex items-center gap-4 p-3.5 rounded-2xl border transition-all duration-300",
                isCurrent
                  ? "border-indigo-500 bg-indigo-500/10 shadow-md shadow-indigo-500/10 ring-1 ring-indigo-500/30"
                  : isDone
                  ? "border-slate-800 bg-slate-900/40 text-slate-300"
                  : "border-slate-800/40 bg-slate-950/20 text-slate-500 opacity-60"
              )}
            >
              <div
                className={cn(
                  "w-8 h-8 rounded-full flex items-center justify-center shrink-0 font-bold text-xs transition-colors",
                  isDone
                    ? "bg-emerald-500 text-white shadow-sm"
                    : isCurrent
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-800 text-slate-500"
                )}
              >
                {isDone ? (
                  <Check className="w-4 h-4 stroke-[3]" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <span>{idx + 1}</span>
                )}
              </div>

              <div className="flex-1 min-w-0">
                <div
                  className={cn(
                    "text-sm font-semibold truncate",
                    isCurrent ? "text-indigo-300" : isDone ? "text-slate-200" : "text-slate-400"
                  )}
                >
                  {step.title}
                </div>
                <div className="text-xs text-slate-400 truncate">{step.subtitle}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
