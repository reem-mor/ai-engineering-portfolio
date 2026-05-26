/** Returns uppercase file-type label for display (e.g. MD, PDF). */

export function fileTypeLabel(filename: string): string {
  const dot = filename.lastIndexOf(".");
  if (dot < 0) return "FILE";
  const ext = filename.slice(dot + 1).toLowerCase();
  const map: Record<string, string> = {
    md: "MD",
    txt: "TXT",
    csv: "CSV",
    pdf: "PDF",
    docx: "DOCX",
  };
  return map[ext] ?? ext.toUpperCase().slice(0, 6);
}
