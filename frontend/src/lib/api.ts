/** Base URL for API calls (no trailing slash). Empty = same origin. */
export function getApiBase(): string {
  const raw = import.meta.env.VITE_API_BASE_URL as string | undefined;
  if (!raw) return "";
  return raw.replace(/\/$/, "");
}

export async function postPipeline(userInput: string): Promise<Response> {
  const base = getApiBase();
  return fetch(`${base}/api/pipeline`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_input: userInput }),
  });
}
