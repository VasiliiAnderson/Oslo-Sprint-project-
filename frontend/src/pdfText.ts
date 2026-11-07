import type { TextItem } from "pdfjs-dist/types/src/display/api";

const MAX_PDF_BYTES = 20 * 1024 * 1024;
const NEW_LINE_THRESHOLD = 2;
const WORD_GAP_RATIO = 0.15;

/** A failure with a message that is safe and useful to show to the user. */
export class PdfReadError extends Error {}

export type PdfText = { text: string; pages: number };

// The library is large, so it only loads when someone actually picks a PDF.
async function loadPdfJs() {
  const [pdfjs, worker] = await Promise.all([
    import("pdfjs-dist"),
    import("pdfjs-dist/build/pdf.worker.min.mjs?url"),
  ]);
  pdfjs.GlobalWorkerOptions.workerSrc = worker.default;
  return pdfjs;
}

function isPdf(file: File) {
  return file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf");
}

// PDF text comes as positioned fragments, so line breaks and spaces are rebuilt from where they sit.
function joinFragments(items: TextItem[]) {
  let text = "";
  let previous: TextItem | null = null;

  for (const item of items) {
    if (item.str) {
      if (previous) {
        const isNewLine = Math.abs(item.transform[5] - previous.transform[5]) > NEW_LINE_THRESHOLD;
        const gap = item.transform[4] - (previous.transform[4] + previous.width);
        if (isNewLine) {
          if (!text.endsWith("\n")) text += "\n";
        } else if (gap > item.height * WORD_GAP_RATIO && !text.endsWith(" ") && !item.str.startsWith(" ")) {
          text += " ";
        }
      }
      text += item.str;
      previous = item;
    }
    if (item.hasEOL && !text.endsWith("\n")) text += "\n";
  }
  return text;
}

function tidy(text: string) {
  return text
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

export async function extractPdfText(file: File): Promise<PdfText> {
  if (!isPdf(file)) throw new PdfReadError("Filen må være en PDF.");
  if (file.size > MAX_PDF_BYTES) throw new PdfReadError("PDF-filen er for stor. Den kan være på høyst 20 MB.");

  let cleanup: (() => Promise<void>) | undefined;
  try {
    const pdfjs = await loadPdfJs();
    const task = pdfjs.getDocument({
      data: await file.arrayBuffer(),
      verbosity: pdfjs.VerbosityLevel.ERRORS,
    });
    cleanup = () => task.destroy();
    const document = await task.promise;

    const pages: string[] = [];
    for (let number = 1; number <= document.numPages; number++) {
      const page = await document.getPage(number);
      const content = await page.getTextContent();
      pages.push(joinFragments(content.items.filter((item): item is TextItem => "str" in item)));
      page.cleanup();
    }

    const text = tidy(pages.join("\n\n"));
    if (!text) {
      throw new PdfReadError(
        "Fant ingen tekst i PDF-filen. Skannede dokumenter støttes ikke, så lim inn teksten i stedet.",
      );
    }
    return { text, pages: document.numPages };
  } catch (error) {
    if (error instanceof PdfReadError) throw error;
    if (error instanceof Error && error.name === "PasswordException") {
      throw new PdfReadError("PDF-filen er passordbeskyttet. Fjern passordet og prøv igjen.");
    }
    throw new PdfReadError("Kunne ikke lese PDF-filen. Prøv en annen fil, eller lim inn teksten.");
  } finally {
    await cleanup?.().catch(() => undefined);
  }
}
