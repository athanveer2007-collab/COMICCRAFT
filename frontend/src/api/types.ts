/**
 * TypeScript API contracts matching backend OpenAPI schema.
 */

export interface DialogueItem {
  speaker: string;
  text: string;
}

export interface CharacterSheet {
  name: string;
  appearance: string;
  age_presentation: string;
  hair: string;
  face: string;
  eyes: string;
  outfit: string;
  primary_colors: string[];
  accessories: string[];
  distinctive_features: string[];
}

export interface PanelResponse {
  panel: number;
  title: string;
  scene_description: string;
  caption: string;
  narration: string;
  dialogue: DialogueItem[];
  image_prompt: string;
  image_url?: string | null;
}

export interface ComicResponse {
  id: string;
  prompt: string;
  character_name: string;
  setting: string;
  custom_setting?: string | null;
  tone: string;
  art_style: string;
  title?: string | null;
  synopsis?: string | null;
  character_sheet?: CharacterSheet | null;
  status: "queued" | "in_progress" | "completed" | "failed";
  panels?: PanelResponse[] | null;
  pdf_path?: string | null;
  pdf_url?: string | null;
  error_code?: string | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ComicCreateRequest {
  prompt: string;
  character_name: string;
  setting: string;
  custom_setting?: string | null;
  tone: string;
  art_style: string;
}

export interface ComicRegenerateRequest {
  tone?: string | null;
  art_style?: string | null;
}

export interface JobCreateResponse {
  job_id: string;
  comic_id: string;
  status: string;
  stage: string;
}

export interface ComicEvent {
  stage: string;
  progress: number;
  message: string;
  comic_id: string;
  job_id: string;
  panel_index?: number | null;
  panel_data?: PanelResponse | null;
  error?: string | null;
}

export interface PDFExportResponse {
  pdf_url: string;
  message: string;
}
