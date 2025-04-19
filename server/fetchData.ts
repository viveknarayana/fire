"use server";

import { createClient } from "@/utils/supabase/server";

export async function fetchUserData() {
  const supabase = await createClient();

  const { data, error } = await supabase.auth.getUser();

  if (error) {
    console.error("Supabase Auth Error:", error.message);
    return null;
  }

  console.log("Authenticated User:", data);
  return data;
}