//api/client.js
const API_BASE = "http://localhost:8000";

export async function apiFetch(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    let message = "API error";
    try {
      const err = await res.json();
      message = err.detail || err.message || message;
    } catch (_) {}
    throw new Error(message);
  }

  // Handle empty responses (logout / 204)
  if (res.status === 204) return null;

  return res.json();
}
