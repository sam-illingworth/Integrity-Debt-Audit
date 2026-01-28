export async function extractFromFile(file: File): Promise<string> {
  if (file.type === "application/pdf") {
    return await extractFromPDF(file);
  } else if (
    file.type ===
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ) {
    return await extractFromDocx(file);
  }
  throw new Error("Unsupported file type. Please use PDF or DOCX.");
}

async function extractFromPDF(file: File): Promise<string> {
  // Dynamic import to reduce bundle size
  const { getDocument, GlobalWorkerOptions } = await import("pdfjs-dist");
  GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${await import("pdfjs-dist/package.json").then((m: any) => m.default.version)}/pdf.worker.min.js`;

  const arrayBuffer = await file.arrayBuffer();
  const pdf = await getDocument({ data: arrayBuffer }).promise;
  let text = "";

  for (let i = 0; i < pdf.numPages; i++) {
    const page = await pdf.getPage(i + 1);
    const textContent = await page.getTextContent();
    text += textContent.items.map((item: any) => item.str).join(" ") + "\n";
  }

  return text;
}

async function extractFromDocx(file: File): Promise<string> {
  // Using a simpler approach for DOCX extraction without docx library issues
  const arrayBuffer = await file.arrayBuffer();
  const uint8Array = new Uint8Array(arrayBuffer);

  // Convert to text (basic extraction)
  let text = "";
  for (let i = 0; i < uint8Array.length; i++) {
    const byte = uint8Array[i];
    if (byte >= 32 && byte <= 126) {
      text += String.fromCharCode(byte);
    } else if (byte === 10 || byte === 13) {
      text += "\n";
    }
  }

  return text;
}

export async function fetchFromURL(url: string): Promise<string> {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error("Failed to fetch URL");

    const html = await response.text();
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, "text/html");

    // Extract text from relevant tags
    const tags = doc.querySelectorAll("p, h1, h2, h3, li, td");
    const text = Array.from(tags)
      .map((tag) => tag.textContent?.trim())
      .filter(Boolean)
      .join("\n");

    return text || "Could not extract text from URL";
  } catch (error) {
    throw new Error(`Failed to fetch URL: ${error}`);
  }
}
