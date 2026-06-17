import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const supabaseKey = (import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY ??
  import.meta.env.VITE_SUPABASE_ANON_KEY) as string | undefined;

export const supabaseConfigured = Boolean(supabaseUrl && supabaseKey);

export const supabase = supabaseConfigured ? createClient(supabaseUrl!, supabaseKey!) : null;

export const petPhotoBucket = (import.meta.env.VITE_SUPABASE_STORAGE_BUCKET as string | undefined) ?? "pet-photos";
