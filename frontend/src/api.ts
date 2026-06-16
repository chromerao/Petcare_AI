import type { GenerationMode, HealthResponse, QueryResponse, SourceCatalogResponse } from "./types";

const API_BASE_URL = (import.meta.env.VITE_DOCQA_API_BASE_URL ?? "http://127.0.0.1:8000").replace(
  /\/+$/,
  "",
);

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...init?.headers,
      },
    });
  } catch (error) {
    throw new Error(`백엔드 API에 연결할 수 없습니다. FastAPI 서버가 실행 중인지 확인해 주세요. 현재 API 주소: ${API_BASE_URL}`, {
      cause: error,
    });
  }

  if (!response.ok) {
    let message = `API 요청에 실패했습니다. (${response.status})`;
    try {
      const body = (await response.json()) as { detail?: { message?: string } | string };
      if (typeof body.detail === "string") {
        message = body.detail;
      } else if (body.detail?.message) {
        message = body.detail.message;
      }
    } catch {
      // Keep the status-based message when the server does not return JSON.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function getHealth(): Promise<HealthResponse> {
  return requestJson<HealthResponse>("/api/v1/health");
}

export async function getSources(): Promise<SourceCatalogResponse> {
  return requestJson<SourceCatalogResponse>("/api/v1/sources");
}

export async function askQuestion(question: string, generationMode: GenerationMode): Promise<QueryResponse> {
  return requestJson<QueryResponse>("/api/v1/query", {
    method: "POST",
    body: JSON.stringify({
      question,
      generation_mode: generationMode,
    }),
  });
}
