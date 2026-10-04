import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Sparkles, Compass, User, Palette, Flame, ArrowRight, Loader2, AlertCircle } from "lucide-react";

import { createComic } from "@/api/client";
import { ArtStyleCard } from "@/components/comic/ArtStyleCard";
import { ToneCard } from "@/components/comic/ToneCard";

const createComicSchema = z.object({
  prompt: z
    .string()
    .min(10, "Story prompt must be at least 10 characters long")
    .max(1000, "Story prompt cannot exceed 1000 characters"),
  character_name: z
    .string()
    .min(1, "Please provide the main character's name")
    .max(100, "Character name is too long"),
  setting: z.string().min(1, "Please choose a setting"),
  custom_setting: z.string().optional(),
  tone: z.string().min(1, "Please select a narrative tone"),
  art_style: z.string().min(1, "Please choose an art style"),
}).refine(
  (data) => {
    if (data.setting === "Custom setting" && (!data.custom_setting || data.custom_setting.trim().length === 0)) {
      return false;
    }
    return true;
  },
  {
    message: "Please enter your custom setting description",
    path: ["custom_setting"],
  }
);

type CreateComicFormData = z.infer<typeof createComicSchema>;

const SETTINGS = ["School", "Forest", "Space", "City", "Custom setting"];
const TONES = ["Light-hearted", "Dramatic", "Poetic", "Funny"];
const ART_STYLES = ["Anime", "Pixel Art", "Comic Book", "Realistic"];

export function CreatePage(): React.JSX.Element {
  const navigate = useNavigate();
  const [submitError, setSubmitError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    watch,
    control,
    formState: { errors, isSubmitting },
  } = useForm<CreateComicFormData>({
    resolver: zodResolver(createComicSchema),
    defaultValues: {
      prompt: "A brave fox named Free exploring an enchanted forest in search of celestial star magic.",
      character_name: "Free",
      setting: "Forest",
      custom_setting: "",
      tone: "Dramatic",
      art_style: "Anime",
    },
  });

  const promptValue = watch("prompt") || "";
  const currentSetting = watch("setting");

  const onSubmit = async (data: CreateComicFormData) => {
    setSubmitError(null);
    try {
      const response = await createComic({
        prompt: data.prompt,
        character_name: data.character_name,
        setting: data.setting,
        custom_setting: data.setting === "Custom setting" ? data.custom_setting : undefined,
        tone: data.tone,
        art_style: data.art_style,
      });

      navigate(`/comics/${response.comic_id}/generating`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to create comic";
      setSubmitError(msg);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* Scenic Hero */}
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-4">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Production-Grade AI Comic Generator</span>
        </div>
        <h1 className="text-4xl sm:text-5xl font-black text-slate-100 tracking-tight">
          Create Your 5-Panel{" "}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-amber-400 via-rose-400 to-indigo-400">
            Comic Saga
          </span>
        </h1>
        <p className="mt-3 text-slate-400 text-sm sm:text-base max-w-2xl mx-auto">
          Provide your story premise, protagonist, and visual direction. ComicCraft orchestrates structured Gemini narrative scripts, character consistency, and publication-ready illustrations.
        </p>
      </div>

      {submitError && (
        <div
          role="alert"
          className="mb-8 p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3"
        >
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
          <span>{submitError}</span>
        </div>
      )}

      {/* Main Creation Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-10">
        {/* Step 1: Story Premise */}
        <section className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8 flex flex-col gap-4 shadow-xl shadow-black/20">
          <div className="flex items-center justify-between">
            <label htmlFor="story-prompt" className="flex items-center gap-2 font-bold text-slate-200 text-sm sm:text-base">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>1. Story Concept or Plot Idea</span>
            </label>
            <span
              className={`text-xs font-semibold ${
                promptValue.length > 900 ? "text-rose-400" : "text-slate-400"
              }`}
            >
              {promptValue.length} / 1000 characters
            </span>
          </div>

          <textarea
            id="story-prompt"
            rows={4}
            {...register("prompt")}
            placeholder="Describe your story idea, mission, encounter, or world..."
            className="w-full rounded-2xl bg-slate-950 border border-slate-800 p-4 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition resize-none"
          />
          {errors.prompt && (
            <p className="text-xs text-rose-400 font-medium">{errors.prompt.message}</p>
          )}
        </section>

        {/* Step 2: Protagonist and Setting */}
        <section className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8 flex flex-col gap-6 shadow-xl shadow-black/20">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {/* Character Name */}
            <div>
              <label htmlFor="character-name" className="flex items-center gap-2 font-bold text-slate-200 text-sm mb-2">
                <User className="w-4 h-4 text-indigo-400" />
                <span>2. Main Character Name</span>
              </label>
              <input
                id="character-name"
                type="text"
                {...register("character_name")}
                placeholder="e.g. Free, Lucas, Nova, Maya"
                className="w-full rounded-xl bg-slate-950 border border-slate-800 px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              />
              {errors.character_name && (
                <p className="mt-1 text-xs text-rose-400 font-medium">{errors.character_name.message}</p>
              )}
            </div>

            {/* Setting Selector */}
            <div>
              <label htmlFor="setting-select" className="flex items-center gap-2 font-bold text-slate-200 text-sm mb-2">
                <Compass className="w-4 h-4 text-emerald-400" />
                <span>3. Setting</span>
              </label>
              <select
                id="setting-select"
                {...register("setting")}
                className="w-full rounded-xl bg-slate-950 border border-slate-800 px-4 py-3 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              >
                {SETTINGS.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Conditional Custom Setting Field */}
          {currentSetting === "Custom setting" && (
            <div className="animate-in fade-in duration-200">
              <label htmlFor="custom-setting-input" className="block text-xs font-semibold text-slate-300 mb-2">
                Describe Your Custom Setting
              </label>
              <input
                id="custom-setting-input"
                type="text"
                {...register("custom_setting")}
                placeholder="e.g. A cyberpunk sunken ocean research outpost"
                className="w-full rounded-xl bg-slate-950 border border-slate-800 px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
              />
              {errors.custom_setting && (
                <p className="mt-1 text-xs text-rose-400 font-medium">{errors.custom_setting.message}</p>
              )}
            </div>
          )}
        </section>

        {/* Step 3: Narrative Tone */}
        <section className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8 flex flex-col gap-4 shadow-xl shadow-black/20">
          <label className="flex items-center gap-2 font-bold text-slate-200 text-sm sm:text-base">
            <Flame className="w-4 h-4 text-rose-400" />
            <span>4. Narrative Tone</span>
          </label>
          <Controller
            control={control}
            name="tone"
            render={({ field }) => (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {TONES.map((t) => (
                  <ToneCard
                    key={t}
                    name={t}
                    isSelected={field.value === t}
                    onSelect={(val) => field.onChange(val)}
                  />
                ))}
              </div>
            )}
          />
        </section>

        {/* Step 4: Art Style */}
        <section className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 sm:p-8 flex flex-col gap-4 shadow-xl shadow-black/20">
          <label className="flex items-center gap-2 font-bold text-slate-200 text-sm sm:text-base">
            <Palette className="w-4 h-4 text-indigo-400" />
            <span>5. Visual Art Style</span>
          </label>
          <Controller
            control={control}
            name="art_style"
            render={({ field }) => (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {ART_STYLES.map((st) => (
                  <ArtStyleCard
                    key={st}
                    id={st}
                    name={st}
                    description=""
                    isSelected={field.value === st}
                    onSelect={(val) => field.onChange(val)}
                  />
                ))}
              </div>
            )}
          />
        </section>

        {/* Submit Action */}
        <div className="flex flex-col items-center gap-4 py-4">
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full sm:w-auto px-10 py-4 rounded-2xl bg-gradient-to-r from-amber-500 via-rose-500 to-indigo-600 hover:from-amber-400 hover:to-indigo-500 text-white font-extrabold text-base shadow-xl shadow-indigo-500/25 transition-all duration-200 flex items-center justify-center gap-3 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed group focus:outline-none focus:ring-4 focus:ring-indigo-500/50"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Initializing Pipeline...</span>
              </>
            ) : (
              <>
                <span>Generate 5-Panel Comic</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
          <p className="text-xs text-slate-500 text-center">
            Generates 5 coherent story panels, character consistency attributes, illustrations, and publication PDF.
          </p>
        </div>
      </form>
    </div>
  );
}
