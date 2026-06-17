import type {
  ChatMessage,
  ChatSession,
  GenerationMode,
  HealthResponse,
  PetProfile,
  QueryResponse,
  SourceCatalogResponse,
} from "./types";

const API_BASE_URL = (import.meta.env.VITE_DOCQA_API_BASE_URL ?? "http://127.0.0.1:8000").replace(
  /\/+$/,
  "",
);

async function requestJson<T>(path: string, init?: RequestInit, accessToken?: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
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

export async function getMyPets(accessToken: string): Promise<PetProfile[]> {
  const response = await requestJson<{ pets: PetProfile[] }>("/api/v1/me/pets", undefined, accessToken);
  return response.pets;
}

export async function saveMyPet(accessToken: string, pet: PetProfile): Promise<PetProfile> {
  const response = await requestJson<{ pet: PetProfile }>(
    "/api/v1/me/pets",
    {
      method: "POST",
      body: JSON.stringify(pet),
    },
    accessToken,
  );
  return response.pet;
}

export async function getMyMessages(accessToken: string): Promise<ChatMessage[]> {
  const response = await requestJson<{ messages: ChatMessage[] }>(
    "/api/v1/me/messages",
    undefined,
    accessToken,
  );
  return response.messages;
}

export async function saveMyMessages(
  accessToken: string,
  petId: string | null,
  messages: ChatMessage[],
  sessionId = "default",
): Promise<void> {
  await requestJson<{ ok: boolean }>(
    "/api/v1/me/messages",
    {
      method: "PUT",
      body: JSON.stringify({ pet_id: petId, session_id: sessionId, messages }),
    },
    accessToken,
  );
}

export async function getMyChatSessions(accessToken: string): Promise<ChatSession[]> {
  const response = await requestJson<{ sessions: ChatSession[] }>(
    "/api/v1/me/chat-sessions",
    undefined,
    accessToken,
  );
  return response.sessions;
}

export async function saveMyChatSession(
  accessToken: string,
  session: Pick<ChatSession, "id" | "title" | "pet_id">,
): Promise<ChatSession> {
  const response = await requestJson<{ session: ChatSession }>(
    "/api/v1/me/chat-sessions",
    {
      method: "POST",
      body: JSON.stringify({ id: session.id, title: session.title, pet_id: session.pet_id }),
    },
    accessToken,
  );
  return response.session;
}

export async function getMySessionMessages(accessToken: string, sessionId: string): Promise<ChatMessage[]> {
  const response = await requestJson<{ messages: ChatMessage[] }>(
    `/api/v1/me/chat-sessions/${encodeURIComponent(sessionId)}/messages`,
    undefined,
    accessToken,
  );
  return response.messages;
}

export async function saveMySessionMessages(
  accessToken: string,
  sessionId: string,
  petId: string | null,
  messages: ChatMessage[],
): Promise<void> {
  await requestJson<{ ok: boolean }>(
    `/api/v1/me/chat-sessions/${encodeURIComponent(sessionId)}/messages`,
    {
      method: "PUT",
      body: JSON.stringify({ pet_id: petId, session_id: sessionId, messages }),
    },
    accessToken,
  );
}
