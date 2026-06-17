export type GenerationMode = "local" | "openai";

export type AnswerType = "document_grounded" | "ai_general" | "no_evidence" | "safety";

export interface HealthResponse {
  status: string;
  service: string;
  environment: string;
}

export interface Citation {
  document_id: string;
  title: string;
  locator: string;
  source_url: string | null;
  snippet: string | null;
  score: number | null;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  grounded: boolean;
  request_id: string;
  generation_mode: string;
  retrieval_confidence: number;
  answer_type: AnswerType;
  safety_notice: string | null;
}

export interface SourceRecord {
  source_id: string;
  title: string;
  publisher: string;
  source_kind: string;
  authority_level: string;
  url: string;
  checked_on: string;
  ingestion_status: string;
  notes: string;
}

export interface SourceCatalogResponse {
  topic_id: string;
  scope: string;
  sources: SourceRecord[];
}

export interface PetProfile {
  id: string;
  name: string;
  species: string;
  breed: string;
  age: string;
  weight: string;
  status: string;
  vet: string;
  note: string;
  photoUrl: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: QueryResponse;
}
