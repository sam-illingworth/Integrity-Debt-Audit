import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseKey);

export async function saveAuditResult(
  email: string,
  score: number,
  susceptibility: string,
  categories: any,
  context: string,
  pdfBlob?: Blob
) {
  try {
    const { data, error } = await supabase.from("audit_submissions").insert([
      {
        email,
        audit_score: score,
        susceptibility: susceptibility.split("(")[0].trim(),
        categories,
        assessment_context: context,
        pdf_data: pdfBlob ? new Uint8Array(await pdfBlob.arrayBuffer()) : null,
      },
    ]);

    if (error) throw error;
    return data;
  } catch (error) {
    console.error("Error saving audit result:", error);
    throw error;
  }
}

export async function saveLead(
  email: string,
  auditId: string,
  wantsStrategyCall: boolean
) {
  try {
    const { data, error } = await supabase.from("lead_emails").insert([
      {
        email,
        audit_id: auditId,
        wants_strategy_call: wantsStrategyCall,
      },
    ]);

    if (error) throw error;
    return data;
  } catch (error) {
    console.error("Error saving lead:", error);
    throw error;
  }
}

export async function getAuditResult(email: string) {
  try {
    const { data, error } = await supabase
      .from("audit_submissions")
      .select("*")
      .eq("email", email)
      .maybeSingle();

    if (error) throw error;
    return data;
  } catch (error) {
    console.error("Error fetching audit result:", error);
    return null;
  }
}
