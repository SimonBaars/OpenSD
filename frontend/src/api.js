const API_BASE = "/api";

class StreamDroppedError extends Error {
  constructor() {
    super("Connection lost — the server is still processing. Please try again.");
    this.name = "StreamDroppedError";
    this.retryable = true;
  }
}

export async function* streamChat(message, history) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let receivedDone = false;

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const event = JSON.parse(line.slice(6));
            if (event.type === "done") receivedDone = true;
            yield event;
          } catch {
            // skip malformed events
          }
        }
      }
    }
  } catch (err) {
    if (!receivedDone) throw new StreamDroppedError();
    throw err;
  }

  if (!receivedDone) {
    throw new StreamDroppedError();
  }
}

export async function fetchBoundaries(name) {
  const res = await fetch(`${API_BASE}/boundaries/${name}`);
  if (!res.ok) return null;
  return res.json();
}

export async function fetchDatasets() {
  const res = await fetch(`${API_BASE}/datasets`);
  if (!res.ok) return [];
  return res.json();
}
