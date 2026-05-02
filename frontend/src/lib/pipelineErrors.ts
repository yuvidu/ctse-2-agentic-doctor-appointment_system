/** User-facing message when fetch to `/api/pipeline` fails (offline, wrong port, CORS). */
export function formatPipelineNetworkError(err: unknown): string {
  const raw = err instanceof Error ? err.message : String(err);
  const lower = raw.toLowerCase();
  if (
    lower.includes("failed to fetch") ||
    lower.includes("networkerror") ||
    lower.includes("load failed") ||
    lower.includes("network request failed")
  ) {
    return [
      "Could not reach the API.",
      "Start the backend (e.g. uvicorn on 127.0.0.1:8010).",
      "For `npm run dev`, Vite proxies /api to VITE_DEV_API_PROXY (default 8010); change it if your port differs.",
      "Leave VITE_API_BASE_URL unset in dev unless the UI and API are on different hosts.",
    ].join(" ");
  }
  return raw || "Network error";
}
