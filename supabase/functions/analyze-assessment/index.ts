import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Client-Info, Apikey",
};

interface CategoryResult {
  category: string;
  score: number;
  critique: string;
  question: string;
  quote: string;
}

interface AuditResponse {
  doc_context: string;
  top_improvements: string[];
  audit_results: CategoryResult[];
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {
      status: 200,
      headers: corsHeaders,
    });
  }

  try {
    const { assessmentText } = await req.json();

    if (!assessmentText) {
      return new Response(
        JSON.stringify({ error: "No assessment text provided" }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    const apiKey = Deno.env.get("GEMINI_API_KEY");
    if (!apiKey) {
      return new Response(
        JSON.stringify({ error: "API key not configured" }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    const categories = [
      "Final product weighting",
      "Iterative documentation",
      "Contextual specificity",
      "Reflective criticality",
      "Temporal friction",
      "Multimodal evidence",
      "Explicit AI interrogation",
      "Real-time defence",
      "Social and collaborative labour",
      "Data recency",
    ];

    const descriptions: Record<string, string> = {
      "Final product weighting":
        "Does the assessment reward the learning process over the final product? Score 1 (single end-of-term submission) to 5 (multiple formative stages).",
      "Iterative documentation":
        "Does the assessment require evidence of the messy middle of learning? Score 1 (polished PDF only) to 5 (mandatory brain-dumps, mind maps, rejected ideas).",
      "Contextual specificity":
        "Is the assessment tied to specific local/classroom contexts that AI cannot access? Score 1 (broad theoretical questions) to 5 (unique in-class discussions).",
      "Reflective criticality":
        "Does the assessment require deep personal synthesis? Score 1 (generic professional reflection) to 5 (narrative on emotional reactions).",
      "Temporal friction":
        "Is it physically impossible to complete quickly? Score 1 (can be done in one night) to 5 (longitudinal study over weeks).",
      "Multimodal evidence":
        "Does the assessment require non-text outputs? Score 1 (standard Word document) to 5 (audio, physical models, hand-drawn).",
      "Explicit AI interrogation":
        "Does the assessment require students to critique AI outputs? Score 1 (AI ignored or banned) to 5 (generate and critique AI drafts).",
      "Real-time defence":
        "Does the assessment include live interaction? Score 1 (entirely asynchronous) to 5 (mandatory viva with Q&A).",
      "Social and collaborative labour":
        "Does the assessment require verified group work? Score 1 (entirely solitary work) to 5 (observed collaboration with peer review).",
      "Data recency":
        "Does the assessment engage with very recent events/data? Score 1 (static concepts from decades ago) to 5 (last fortnight).",
    };

    const categoryInfo = categories
      .map((cat) => `- ${cat}: ${descriptions[cat]}`)
      .join("\n");

    const prompt = `You are Professor Sam Illingworth conducting an Integrity Debt Audit for a Higher Education assessment.

CRITICAL INSTRUCTIONS:
1. Analyse the assessment brief against EXACTLY these 10 categories in this exact order:
${categoryInfo}

2. For each category, provide:
   - A score from 1-5 (where 1 = easily automated/vulnerable, 5 = resilient/Slow AI)
   - A critique explaining why you gave this score (keep under 150 words)
   - A dialogue question to help the educator reflect (one sentence)
   - A direct quote from the assessment that supports your score (under 50 words)

3. Your response MUST be valid JSON with this exact structure:
{
    "doc_context": "Brief title/description of the assessment",
    "top_improvements": ["Improvement 1", "Improvement 2", "Improvement 3"],
    "audit_results": [
        {
            "category": "Final product weighting",
            "score": 3,
            "critique": "Your analysis here",
            "question": "Reflective question here",
            "quote": "Direct quote from assessment"
        },
        ... (repeat for all 10 categories in order)
    ]
}

4. JSON FORMATTING RULES:
   - NO trailing commas before closing braces or brackets
   - Escape ALL quotes within strings using backslash: \\"
   - Keep critique and quote fields SHORT to avoid JSON issues
   - Do NOT include line breaks within string values
   - Use only standard ASCII quotes, not smart quotes

5. IMPORTANT:
   - Use ONLY the category names listed above
   - Provide exactly 10 results, one for each category
   - Scores must be integers from 1-5
   - Use British English spellings (organise not organize, emphasise not emphasize, etc.)
   - If information is missing for a category, estimate based on typical practices and note this in the critique

Assessment text to analyse (truncated to first 8000 characters):
${assessmentText.substring(0, 8000)}

Return ONLY valid JSON with no additional text, markdown formatting, or preamble.`;

    const response = await fetch(
      "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-goog-api-key": apiKey,
        },
        body: JSON.stringify({
          contents: [
            {
              parts: [
                {
                  text: prompt,
                },
              ],
            },
          ],
          generationConfig: {
            temperature: 0.1,
            topP: 0.2,
            topK: 2,
          },
        }),
      }
    );

    if (!response.ok) {
      throw new Error(`Gemini API error: ${response.statusText}`);
    }

    const data = await response.json();
    const aiResponse = data.candidates?.[0]?.content?.parts?.[0]?.text;

    if (!aiResponse) {
      throw new Error("No content in AI response");
    }

    // Clean JSON response
    let cleanedResponse = aiResponse
      .replace(/```json\s*|\s*```/g, "")
      .trim();
    const match = cleanedResponse.match(/\{[\s\S]*\}/);
    if (match) {
      cleanedResponse = match[0];
    }

    // Try to parse JSON
    let parsedResponse: AuditResponse;
    try {
      parsedResponse = JSON.parse(cleanedResponse);
    } catch {
      // Try basic fixes
      cleanedResponse = cleanedResponse
        .replace(/,\s*}/g, "}")
        .replace(/,\s*]/g, "]");
      parsedResponse = JSON.parse(cleanedResponse);
    }

    return new Response(JSON.stringify(parsedResponse), {
      status: 200,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to analyze assessment" }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});
