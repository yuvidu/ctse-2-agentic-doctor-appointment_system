import type { PipelineResponse } from "@/types/pipeline";

/** Prefer API `available_slots` strings; else format structured slot rows. */
export function extractSlotLines(data: PipelineResponse): string[] {
  const direct = data.available_slots;
  if (Array.isArray(direct) && direct.length > 0) {
    return direct.map(String);
  }
  const raw = data.availability?.available_slots;
  if (!Array.isArray(raw) || raw.length === 0) {
    return [];
  }
  return raw.map((s) => {
    if (s && typeof s === "object") {
      const id = s.doctor_id ?? "";
      const start = s.start ?? "";
      const end = s.end ?? "";
      const loc = s.location ?? "";
      return `${id} | ${start} – ${end} | ${loc}`.trim();
    }
    return String(s);
  });
}
