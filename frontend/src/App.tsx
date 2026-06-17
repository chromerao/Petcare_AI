import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import {
  askQuestion,
  getHealth,
  getMyMessages,
  getMyPets,
  getSources,
  saveMyMessages,
  saveMyPet,
} from "./api";
import { supabase, supabaseConfigured } from "./supabase";
import type { ChatMessage, GenerationMode, QueryResponse } from "./types";

type Page = "home" | "dashboard" | "chat" | "profile" | "register";

interface AuthUser {
  id: string;
  email: string;
  name: string;
}

interface PetProfile {
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

const AUTH_STORAGE_KEY = "petcare-ai-current-user";
const PETS_STORAGE_KEY = "petcare-ai-pets";
const MESSAGES_STORAGE_KEY = "petcare-ai-messages";
const GUEST_USER_ID = "guest";

const dogPhoto =
  "https://lh3.googleusercontent.com/aida-public/AB6AXuACyhdaGHCc-TwvQn6RtYbW4zOmGSGKaYqqiJxu7CzYNMOXtV7urU5QkBsPxp6hfGaXCotJiNw8nCnFPdL1M7q9MislFg8awpLnvGwBV2wMiUEfa6IvG-0pjFrrhBUQVMvkP-kQGwSZ7J_rCsdJMmQHRcQPnoaYhmbeLNGiNotv6CRLS_zQUI0FoV9akQKfnN9lt1QG3mQvjOYhfA4h4lXl92VW_-fm3PGVlaGblZlEnm8yf019xCq0-BRV1lx18PPfQU_zuMHP6gE";
const catPhoto =
  "https://lh3.googleusercontent.com/aida-public/AB6AXuCz4lWf4CbWjOXO8s9Er6XDF4Q6TjA-BltGVWqJFQPkPROklLPkb9EucN515YyLoqwi2lgoY4BkqthMccPfv7nZU-9XODa42Dn0VBfLtkcDi63wgkyKz3R44tDt6CYdnCYuEetCji8CUDXg09ED4tzWt25NfePw6jNri4-3MlXsxQQpsJ4DEQuz5b5rNT8qatr2SjX7mXdvqzaWbbWjpy3kgtD6IIuhmiFkHqPHhYDX9oPwJ7YToZ1nBMyQKNPAPxhfLmqW3PlYU48";

const defaultPets: PetProfile[] = [
  {
    id: "bella",
    name: "Bella",
    species: "강아지",
    breed: "골든 리트리버",
    age: "4세",
    weight: "28kg",
    status: "건강함",
    vet: "스크리치 동물병원",
    note: "닭고기 단백질 알레르기가 있고 분리불안 경향이 있습니다.",
    photoUrl: dogPhoto,
  },
  {
    id: "max",
    name: "Max",
    species: "고양이",
    breed: "태비 고양이",
    age: "2세",
    weight: "5.1kg",
    status: "업데이트 필요",
    vet: "동네동물의료센터",
    note: "최근 음수량과 화장실 사용 빈도를 관찰 중입니다.",
    photoUrl: catPhoto,
  },
];

const navItems: { page: Page; label: string }[] = [
  { page: "home", label: "메인" },
  { page: "dashboard", label: "대시보드" },
  { page: "chat", label: "AI 상담" },
  { page: "profile", label: "프로필" },
  { page: "register", label: "반려동물 등록" },
];

const chips = ["구토", "설사", "초콜릿 섭취", "분리불안", "물을 많이 마심", "화장실 문제", "호텔 입실", "시설 사고"];

const chipQuestions: Record<string, string> = {
  구토: "반려동물이 구토를 했을 때 어떤 증상을 기록하고 언제 병원에 가야 하나요?",
  설사: "반려동물이 설사를 할 때 사료, 간식, 응급 신호를 어떤 순서로 확인해야 하나요?",
  "초콜릿 섭취": "강아지가 초콜릿을 조금 먹었는데 어떻게 해야 하나요?",
  분리불안: "혼자 두면 계속 짖고 문을 긁어요. 분리불안일까요?",
  "물을 많이 마심": "반려동물이 물을 많이 마시고 화장실을 자주 가요. 무엇을 확인해야 하나요?",
  "화장실 문제": "고양이가 화장실이 아닌 곳에 소변을 봐요. 원인이 뭘까요?",
  "호텔 입실": "반려동물 호텔 입실 전에 보호자가 준비해야 할 체크리스트는 무엇인가요?",
  "시설 사고": "반려동물 시설에서 사고가 났을 때 먼저 해야 할 조치는 무엇인가요?",
};

const historySeed = [
  { title: "오른쪽 앞발 절뚝거림", meta: "최근 상담 · 관찰 권장" },
  { title: "예방접종 문의", meta: "일반 상담 · 일정 확인" },
];

function createId(prefix: string): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function userStorageKey(baseKey: string, userId: string): string {
  return `${baseKey}:${userId}`;
}

function normalizeUserId(email: string): string {
  return email.trim().toLowerCase().replace(/[^a-z0-9@._-]/g, "");
}

function loadCurrentUser(): AuthUser | null {
  try {
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as AuthUser) : null;
  } catch {
    return null;
  }
}

function saveCurrentUser(user: AuthUser | null) {
  if (user) {
    window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(user));
  } else {
    window.localStorage.removeItem(AUTH_STORAGE_KEY);
  }
}

function loadStoredPets(userId: string): PetProfile[] {
  try {
    const raw = window.localStorage.getItem(userStorageKey(PETS_STORAGE_KEY, userId));
    if (!raw) return defaultPets;
    const parsed = JSON.parse(raw) as PetProfile[];
    return Array.isArray(parsed) && parsed.length > 0 ? parsed : defaultPets;
  } catch {
    return defaultPets;
  }
}

function saveStoredPets(userId: string, pets: PetProfile[]) {
  window.localStorage.setItem(userStorageKey(PETS_STORAGE_KEY, userId), JSON.stringify(pets));
}

function loadStoredMessages(userId: string): ChatMessage[] {
  try {
    const raw = window.localStorage.getItem(userStorageKey(MESSAGES_STORAGE_KEY, userId));
    if (!raw) return [];
    const parsed = JSON.parse(raw) as ChatMessage[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveStoredMessages(userId: string, messages: ChatMessage[]) {
  window.localStorage.setItem(userStorageKey(MESSAGES_STORAGE_KEY, userId), JSON.stringify(messages));
}

function fallbackPhoto(species: string): string {
  return species.includes("고양") ? catPhoto : dogPhoto;
}

function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result));
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

function answerLabel(response: QueryResponse): string {
  switch (response.answer_type) {
    case "document_grounded":
      return "문서 근거 답변";
    case "ai_general":
      return "AI 일반 조언";
    case "safety":
      return "안전 차단";
    case "no_evidence":
      return "근거 부족";
    default:
      return response.answer_type;
  }
}

function userMessage(content: string): ChatMessage {
  return { id: createId("user"), role: "user", content };
}

function assistantMessage(response: QueryResponse): ChatMessage {
  return {
    id: createId("assistant"),
    role: "assistant",
    content: response.answer,
    response,
  };
}

function Icon({ children, className = "" }: { children: string; className?: string }) {
  return <span className={`material-symbols-outlined ${className}`}>{children}</span>;
}

function PetPhoto({ pet, className }: { pet: PetProfile; className: string }) {
  return <img alt={`${pet.name} 사진`} className={`${className} object-cover`} src={pet.photoUrl || fallbackPhoto(pet.species)} />;
}

function TopNav({
  activePage,
  onEmergency,
  onLoginClick,
  onLogout,
  onSignupClick,
  setPage,
  user,
}: {
  activePage: Page;
  onEmergency: () => void;
  onLoginClick: () => void;
  onLogout: () => void;
  onSignupClick: () => void;
  setPage: (page: Page) => void;
  user: AuthUser | null;
}) {
  return (
    <header className="fixed top-0 left-0 w-full z-50 flex justify-between items-center px-margin-mobile md:px-xl py-md bg-surface dark:bg-background shadow-sm h-[72px]">
      <button className="flex items-center gap-sm" onClick={() => setPage("home")} type="button">
        <Icon className="text-primary text-3xl" children="pets" />
        <span className="text-headline-md font-headline-md text-primary dark:text-primary-fixed-dim">PetCare AI</span>
      </button>
      <nav className="flex gap-xs md:gap-lg overflow-x-auto max-w-[54vw] md:max-w-none">
        {navItems.map((item) => (
          <button
            className={
              activePage === item.page
                ? "text-primary font-bold border-b-2 border-primary pb-1 hover:bg-surface-container-low transition-colors px-3 py-2 rounded-DEFAULT"
                : "text-on-surface-variant font-medium hover:text-primary hover:bg-surface-container-low transition-colors px-3 py-2 rounded-DEFAULT"
            }
            key={item.page}
            onClick={() => setPage(item.page)}
            type="button"
          >
            {item.label}
          </button>
        ))}
      </nav>
      <div className="flex items-center gap-xs">
        {user && (
          <div className="hidden lg:flex flex-col items-end leading-tight">
            <span className="text-label-md font-label-md text-primary">{user.name}</span>
            <span className="text-label-sm font-label-sm text-on-surface-variant">{user.email}</span>
          </div>
        )}
        <button
          className="bg-error text-on-error px-3 md:px-4 py-2 rounded-lg font-label-md text-label-md flex items-center gap-xs hover:bg-on-error-container transition-colors shadow-soft"
          onClick={onEmergency}
          type="button"
        >
          <Icon className="text-sm" children="emergency" />
          <span className="hidden md:inline">긴급 호출</span>
        </button>
        {user ? (
          <button
            className="bg-surface-container text-primary px-3 py-2 rounded-lg font-label-md text-label-md hover:bg-surface-container-high transition-colors"
            onClick={onLogout}
            type="button"
          >
            로그아웃
          </button>
        ) : (
          <>
            <button
              className="bg-surface-container text-primary px-3 py-2 rounded-lg font-label-md text-label-md hover:bg-surface-container-high transition-colors"
              onClick={onSignupClick}
              type="button"
            >
              회원가입
            </button>
            <button
              className="bg-primary text-on-primary px-3 py-2 rounded-lg font-label-md text-label-md hover:shadow-soft transition-colors"
              onClick={onLoginClick}
              type="button"
            >
              로그인
            </button>
          </>
        )}
      </div>
    </header>
  );
}

function AuthDialog({
  authError,
  authMode,
  authStatus,
  onClose,
  onAuthSubmit,
}: {
  authError: string | null;
  authMode: "login" | "signup";
  authStatus: string | null;
  onClose: () => void;
  onAuthSubmit: (
    mode: "login" | "signup",
    email: string,
    password: string,
    name: string,
  ) => void;
}) {
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmitForm();
  }

  function onSubmitForm() {
    const trimmedEmail = email.trim().toLowerCase();
    if (!trimmedEmail || password.length < 6) return;
    onAuthSubmit(authMode, trimmedEmail, password, name.trim());
  }

  return (
    <div className="fixed inset-0 z-[80] bg-black/40 backdrop-blur-sm flex items-center justify-center px-margin-mobile">
      <form
        className="w-full max-w-lg bg-surface-container-lowest rounded-[2rem] p-lg md:p-xl shadow-lg border border-outline-variant/30"
        onSubmit={onSubmit}
      >
        <div className="flex items-start justify-between gap-md">
          <div className="w-14 h-14 rounded-2xl bg-primary text-on-primary flex items-center justify-center mb-md">
            <Icon className="text-3xl" children="pets" />
          </div>
          <button className="text-on-surface-variant hover:text-primary" onClick={onClose} type="button">
            <Icon children="close" />
          </button>
        </div>
        <h2 className="text-headline-lg font-headline-lg text-primary mb-xs">
          {authMode === "signup" ? "회원가입" : "로그인"}
        </h2>
        <p className="text-body-md font-body-md text-on-surface-variant mb-lg">
          로그인하면 반려동물 프로필과 상담 내역이 Supabase DB에 사용자별로 저장됩니다. 로그인하지 않아도 게스트 모드로 사용할 수 있습니다.
        </p>
        {!supabaseConfigured && (
          <div className="mb-md bg-error-container text-on-error-container rounded-lg p-sm text-label-md font-label-md">
            Supabase 환경변수가 아직 설정되지 않았습니다. Vercel에 VITE_SUPABASE_URL과 VITE_SUPABASE_PUBLISHABLE_KEY를 추가해 주세요.
          </div>
        )}
          <div className="space-y-md">
            <label className="flex flex-col gap-xs">
              <span className="text-label-md font-label-md text-on-surface-variant">이메일</span>
              <input
                autoComplete="email"
                className="bg-surface-container-low rounded-lg px-md py-sm focus:ring-2 focus:ring-primary outline-none"
                onChange={(event) => setEmail(event.target.value)}
                placeholder="guardian@example.com"
                required
                type="email"
                value={email}
              />
            </label>
            <label className="flex flex-col gap-xs">
              <span className="text-label-md font-label-md text-on-surface-variant">비밀번호</span>
              <input
                autoComplete={authMode === "signup" ? "new-password" : "current-password"}
                className="bg-surface-container-low rounded-lg px-md py-sm focus:ring-2 focus:ring-primary outline-none"
                minLength={6}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="6자 이상"
                required
                type="password"
                value={password}
              />
            </label>
            {authMode === "signup" && (
              <label className="flex flex-col gap-xs">
                <span className="text-label-md font-label-md text-on-surface-variant">이름 또는 닉네임</span>
                <input
                  autoComplete="name"
                  className="bg-surface-container-low rounded-lg px-md py-sm focus:ring-2 focus:ring-primary outline-none"
                  onChange={(event) => setName(event.target.value)}
                  placeholder="보호자"
                  value={name}
                />
              </label>
            )}
          </div>
          {authError && <p className="mt-md text-error text-label-md font-label-md">{authError}</p>}
          {authStatus && <p className="mt-md text-primary text-label-md font-label-md">{authStatus}</p>}
          <button
            className="mt-lg w-full bg-primary text-on-primary px-lg py-md rounded-lg font-label-md shadow-soft hover:shadow-md transition-all disabled:opacity-60"
            disabled={!supabaseConfigured}
            type="submit"
          >
            {authMode === "signup" ? "회원가입" : "로그인"}
          </button>
      </form>
    </div>
  );
}

function LandingPage({ selectedPet, setPage }: { selectedPet: PetProfile; setPage: (page: Page, question?: string) => void }) {
  return (
    <main className="flex-grow pt-[88px] pb-xxl bg-surface text-on-surface font-body-md">
      <section className="relative w-full max-w-container-max mx-auto px-margin-mobile md:px-xl py-lg md:py-xl flex flex-col md:flex-row items-center gap-xl md:min-h-[620px]">
        <div className="flex-1 flex flex-col items-start gap-md z-10">
          <div className="inline-flex items-center gap-2 bg-secondary-container text-on-secondary-container px-3 py-1 rounded-full text-label-sm font-label-sm mb-2">
            <Icon className="text-sm" children="health_and_safety" />
            <span>나만의 반려동물 의사 / 전문가</span>
          </div>
          <h1 className="text-display-lg font-display-lg text-primary max-w-2xl leading-tight">
            우리 아이의 건강과 생활,
            <br />
            <span className="text-surface-tint">AI가 근거와 함께 안내합니다.</span>
          </h1>
          <p className="text-body-lg font-body-lg text-on-surface-variant max-w-xl mt-sm mb-lg">
            내부 운영 문서, 공신력 있는 외부 자료, 그리고 LLM 조언을 함께 활용해 증상 상담부터 시설 이용, 생활 습관까지 도와주는 반려동물 케어 시스템입니다.
          </p>
          <div className="flex flex-col sm:flex-row gap-sm w-full sm:w-auto">
            <button
              className="bg-primary text-on-primary px-lg py-md rounded-lg text-label-md font-label-md flex items-center justify-center gap-sm hover:shadow-md transition-all active:scale-95"
              onClick={() => setPage("chat")}
              type="button"
            >
              <Icon children="medical_services" />
              AI 상담 시작
            </button>
            <button
              className="bg-secondary-container text-primary px-lg py-md rounded-lg text-label-md font-label-md flex items-center justify-center gap-sm hover:bg-secondary-fixed transition-all active:scale-95 border border-transparent hover:border-primary/20"
              onClick={() => setPage("register")}
              type="button"
            >
              <Icon children="add_circle" />
              반려동물 등록
            </button>
            <button
              className="bg-surface-container-low text-primary px-lg py-md rounded-lg text-label-md font-label-md flex items-center justify-center gap-sm hover:bg-surface-container transition-all"
              onClick={() => setPage("dashboard")}
              type="button"
            >
              <Icon children="dashboard" />
              대시보드 보기
            </button>
          </div>
          <div className="mt-xl flex items-center gap-md text-label-sm font-label-sm text-on-surface-variant">
            <PetPhoto className="w-10 h-10 rounded-full border-2 border-surface" pet={selectedPet} />
            <span>현재 상담 대상: {selectedPet.name} · {selectedPet.breed || selectedPet.species}</span>
          </div>
        </div>
        <div className="flex-1 w-full relative">
          <div className="absolute inset-0 bg-primary-fixed rounded-[2rem] transform rotate-3 scale-105 opacity-50 z-0" />
          <div className="relative z-10 w-full min-h-[480px] rounded-[2rem] shadow-lg border-4 border-surface bg-gradient-to-br from-primary-fixed via-surface-container-lowest to-secondary-fixed flex items-center justify-center p-xl">
            <div className="bg-surface-container-lowest/90 rounded-[2rem] p-xl shadow-soft max-w-md">
              <PetPhoto className="w-36 h-36 rounded-[2rem] shadow-soft mb-md" pet={selectedPet} />
              <h2 className="text-headline-lg font-headline-lg text-primary mb-sm">{selectedPet.name} 케어 룸</h2>
              <p className="text-body-md font-body-md text-on-surface-variant">
                증상, 식이, 행동, 시설 이용 이슈를 하나의 맥락으로 묶어 상담합니다. 사진을 등록하면 프로필과 상담 화면에 함께 반영됩니다.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="max-w-container-max mx-auto px-margin-mobile md:px-xl py-xxl">
        <div className="text-center mb-xl">
          <h2 className="text-headline-lg font-headline-lg text-primary mb-sm">주요 기능</h2>
          <p className="text-body-lg font-body-lg text-on-surface-variant max-w-2xl mx-auto">
            보기만 좋은 버튼이 아니라 실제로 상담, 등록, 프로필, 대시보드 흐름으로 연결됩니다.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
          {[
            ["smart_toy", "AI 상담", "문서 근거와 AI 일반 조언을 함께 확인합니다.", "chat"],
            ["pets", "프로필 기반 상담", "종, 품종, 나이, 체중, 특이사항을 질문에 자동 반영합니다.", "profile"],
            ["add_photo_alternate", "사진 등록", "기본 귀여운 사진 또는 직접 업로드한 사진을 사용할 수 있습니다.", "register"],
          ].map(([icon, title, desc, page]) => (
            <button
              className="text-left bg-surface-container-low rounded-[1.5rem] p-lg border border-surface-variant hover:shadow-sm transition-shadow"
              key={title}
              onClick={() => setPage(page as Page)}
              type="button"
            >
              <div className="w-12 h-12 bg-primary text-on-primary rounded-xl flex items-center justify-center mb-md shadow-sm">
                <Icon className="text-2xl" children={icon} />
              </div>
              <h3 className="text-headline-md font-headline-md text-primary mb-sm">{title}</h3>
              <p className="text-body-md font-body-md text-on-surface-variant">{desc}</p>
            </button>
          ))}
        </div>
      </section>
    </main>
  );
}

function DashboardPage({
  pets,
  selectedPet,
  setPage,
  setSelectedPetId,
}: {
  pets: PetProfile[];
  selectedPet: PetProfile;
  setPage: (page: Page) => void;
  setSelectedPetId: (id: string) => void;
}) {
  return (
    <main className="flex-grow pt-[88px] px-margin-mobile md:px-xl max-w-container-max mx-auto w-full pb-xxl bg-background text-on-surface font-body-md text-body-md antialiased min-h-screen">
      <header className="mb-xl mt-lg">
        <h1 className="text-headline-lg font-headline-lg text-on-surface mb-xs">반려동물 케어 대시보드</h1>
        <p className="text-body-lg font-body-lg text-on-surface-variant">등록된 아이들의 상태와 상담 흐름을 한눈에 확인하세요.</p>
      </header>
      <div className="grid grid-cols-1 md:grid-cols-12 gap-gutter">
        <div className="md:col-span-4 flex flex-col gap-md">
          {pets.map((pet) => (
            <button
              className={`text-left bg-surface-container-lowest rounded-xl shadow-soft p-md border-t-2 ${pet.id === selectedPet.id ? "border-primary" : "border-outline-variant"} relative overflow-hidden group cursor-pointer hover:-translate-y-1 transition-transform`}
              key={pet.id}
              onClick={() => {
                setSelectedPetId(pet.id);
                setPage("profile");
              }}
              type="button"
            >
              <div className="flex items-center gap-md mb-sm">
                <PetPhoto className="w-16 h-16 rounded-full border-2 border-primary-fixed" pet={pet} />
                <div>
                  <h2 className="text-headline-md font-headline-md text-on-surface text-xl">{pet.name}</h2>
                  <p className="text-label-md font-label-md text-on-surface-variant">
                    {pet.breed || pet.species}, {pet.age || "나이 미입력"}
                  </p>
                </div>
              </div>
              <div className="flex justify-between items-center bg-secondary-fixed/30 p-sm rounded-lg">
                <span className="text-label-sm font-label-sm text-secondary">상태</span>
                <span className="text-label-sm font-label-sm text-primary font-bold bg-primary-fixed px-2 py-1 rounded">{pet.status || "관찰 중"}</span>
              </div>
            </button>
          ))}
          <button
            className="bg-surface-container border border-dashed border-outline-variant rounded-xl p-md flex items-center justify-center gap-sm text-primary hover:bg-surface-container-high transition-colors"
            onClick={() => setPage("register")}
            type="button"
          >
            <Icon children="add_circle" />
            <span className="text-label-md font-label-md font-bold">반려동물 추가</span>
          </button>
        </div>

        <div className="md:col-span-8 flex flex-col gap-md">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-sm">
            {[
              ["monitor_weight", `${selectedPet.name} 체중`, selectedPet.weight || "미입력", "primary"],
              ["vaccines", "다음 예방접종", "확인 필요", "secondary"],
              ["chat", "상담 준비", "완료", "primary"],
              ["calendar_month", "건강검진", "일정 등록", "secondary"],
            ].map(([icon, label, value, tone]) => (
              <div className="bg-surface-container-lowest rounded-xl shadow-soft p-sm flex flex-col items-center justify-center text-center" key={label}>
                <Icon className={`text-${tone} mb-xs`} children={icon} />
                <span className="text-body-md font-body-md text-on-surface-variant">{label}</span>
                <span className="text-headline-md font-headline-md text-primary">{value}</span>
              </div>
            ))}
          </div>
          <div className="bg-surface-container-lowest rounded-xl shadow-soft p-lg border-t-2 border-primary flex-grow">
            <div className="flex justify-between items-center mb-md">
              <h3 className="text-headline-md font-headline-md text-on-surface text-lg">{selectedPet.name} 케어 노트</h3>
              <button className="text-primary text-label-md font-label-md hover:underline" onClick={() => setPage("chat")} type="button">
                상담하기
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
              <div className="bg-surface-container-low p-md rounded-lg">
                <p className="text-label-md font-label-md text-on-surface-variant mb-xs">기본 정보</p>
                <p className="text-body-lg font-body-lg text-on-surface">
                  {selectedPet.species} · {selectedPet.breed || "품종 미입력"} · {selectedPet.age || "나이 미입력"}
                </p>
              </div>
              <div className="bg-surface-container-low p-md rounded-lg">
                <p className="text-label-md font-label-md text-on-surface-variant mb-xs">주의 사항</p>
                <p className="text-body-md font-body-md text-on-surface-variant">{selectedPet.note || "등록된 특이사항이 없습니다."}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="md:col-span-12 grid grid-cols-1 md:grid-cols-2 gap-gutter mt-sm">
          <div className="bg-surface-container-lowest rounded-xl shadow-soft p-md">
            <h3 className="text-headline-md font-headline-md text-on-surface text-lg mb-md flex items-center gap-xs">
              <Icon className="text-secondary" children="notifications" />
              예정된 일정
            </h3>
            <ul className="space-y-sm">
              <li className="flex items-center justify-between p-sm hover:bg-surface-container-low rounded-lg transition-colors">
                <div className="flex items-center gap-sm">
                  <div className="w-2 h-2 rounded-full bg-error" />
                  <span className="text-body-md font-body-md text-on-surface">{selectedPet.name} - 예방접종 일정 확인</span>
                </div>
                <span className="text-label-sm font-label-sm text-on-surface-variant bg-surface-container px-2 py-1 rounded">등록 필요</span>
              </li>
            </ul>
          </div>
          <div className="bg-surface-container-lowest rounded-xl shadow-soft p-md">
            <h3 className="text-headline-md font-headline-md text-on-surface text-lg mb-md flex items-center gap-xs">
              <Icon className="text-primary" children="history" />
              빠른 상담
            </h3>
            <button
              className="block text-left w-full p-sm border border-outline-variant rounded-lg hover:border-primary transition-colors bg-surface-bright"
              onClick={() => setPage("chat")}
              type="button"
            >
              <div className="flex justify-between items-start mb-xs">
                <span className="text-label-md font-label-md font-bold text-primary">{selectedPet.name}: 최근 상태 상담</span>
                <span className="text-label-sm font-label-sm text-outline">지금</span>
              </div>
              <p className="text-body-md font-body-md text-on-surface-variant text-sm truncate">증상, 식이, 행동 변화를 입력하면 AI가 케어 방향을 정리합니다.</p>
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}

function ProfilePage({
  pet,
  onEdit,
  setPage,
}: {
  pet: PetProfile;
  onEdit: () => void;
  setPage: (page: Page, question?: string) => void;
}) {
  return (
    <main className="flex-grow pt-xxl mt-xl max-w-container-max mx-auto w-full px-margin-mobile md:px-xl pb-xxl bg-surface text-on-surface font-body-md min-h-screen">
      <section className="flex flex-col md:flex-row items-center md:items-start gap-xl mb-xl bg-surface-container-low p-lg md:p-xl rounded-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary-fixed opacity-30 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4 pointer-events-none" />
        <div className="relative shrink-0">
          <PetPhoto className="w-40 h-40 md:w-56 md:h-56 rounded-full shadow-sm border-4 border-surface-container-lowest" pet={pet} />
        </div>
        <div className="flex-grow flex flex-col items-center md:items-start text-center md:text-left z-10 w-full">
          <div className="flex flex-col md:flex-row md:items-center justify-between w-full mb-sm">
            <h1 className="text-headline-lg-mobile md:text-headline-lg font-headline-lg-mobile md:font-headline-lg text-primary mb-xs md:mb-0">{pet.name}</h1>
            <button
              className="hidden md:flex items-center gap-xs bg-secondary-container text-primary font-label-md px-md py-sm rounded-full hover:bg-secondary-fixed-dim transition-colors"
              onClick={onEdit}
              type="button"
            >
              <Icon className="text-[18px]" children="edit" />
              프로필 수정
            </button>
          </div>
          <p className="text-body-lg font-body-lg text-on-surface-variant mb-md">
            {pet.breed || pet.species} · {pet.age || "나이 미입력"} · {pet.status || "상태 미입력"}
          </p>
          <div className="flex flex-wrap justify-center md:justify-start gap-sm mb-lg">
            {[
              ["scale", pet.weight || "체중 미입력"],
              ["pets", pet.species || "종 미입력"],
              ["local_hospital", pet.vet || "병원 미입력"],
            ].map(([icon, text]) => (
              <span className="inline-flex items-center gap-xs bg-surface-container-lowest border border-outline-variant rounded-full px-md py-xs text-label-sm font-label-sm text-on-surface-variant shadow-sm" key={text}>
                <Icon className="text-[16px]" children={icon} /> {text}
              </span>
            ))}
          </div>
          <button className="md:hidden bg-secondary-container text-primary font-label-md px-md py-sm rounded-full" onClick={onEdit} type="button">
            프로필 수정
          </button>
        </div>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-lg">
        <div className="md:col-span-8 bg-surface-container-lowest rounded-xl p-lg shadow-sm border-t-2 border-primary flex flex-col">
          <h2 className="text-headline-md font-headline-md text-primary flex items-center gap-sm mb-lg border-b border-surface-variant pb-sm">
            <Icon className="text-primary" children="medical_information" />
            종합 케어 정보
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-lg flex-grow">
            <div>
              <h3 className="text-label-md font-label-md text-on-surface-variant mb-md uppercase tracking-wider">특이사항</h3>
              <p className="bg-surface-container p-md rounded-lg text-body-md font-body-md text-on-surface-variant min-h-28">{pet.note || "등록된 특이사항이 없습니다."}</p>
            </div>
            <div>
              <h3 className="text-label-md font-label-md text-on-surface-variant mb-md uppercase tracking-wider">빠른 액션</h3>
              <div className="space-y-sm">
                <button className="w-full bg-primary text-on-primary p-sm rounded-lg flex items-center justify-center gap-sm" onClick={() => setPage("chat")} type="button">
                  <Icon children="smart_toy" />
                  이 아이 정보로 AI 상담
                </button>
                <button
                  className="w-full bg-secondary-container text-primary p-sm rounded-lg flex items-center justify-center gap-sm"
                  onClick={() => setPage("chat", `${pet.name}를 동물병원에 데려가기 전 보호자가 기록하고 준비해야 할 정보는 무엇인가요?`)}
                  type="button"
                >
                  <Icon children="call" />
                  병원 방문 준비
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="md:col-span-4 flex flex-col gap-lg">
          <div className="bg-surface-container-lowest rounded-xl p-lg shadow-sm border-t-2 border-secondary h-full">
            <h2 className="text-headline-md font-headline-md text-primary mb-md flex items-center gap-sm">
              <Icon className="text-secondary" children="restaurant" />
              생활 관리
            </h2>
            <p className="text-body-md font-body-md text-on-surface-variant">식이, 산책, 배변, 행동 문제를 상담 시 함께 반영합니다.</p>
          </div>
          <div className="bg-surface-container-lowest rounded-xl p-lg shadow-sm border-t-2 border-secondary h-full">
            <h2 className="text-headline-md font-headline-md text-primary mb-md flex items-center gap-sm">
              <Icon className="text-secondary" children="local_hospital" />
              담당 동물병원
            </h2>
            <p className="text-label-md font-label-md text-on-surface">{pet.vet || "미입력"}</p>
            <button
              className="mt-md w-full bg-secondary-container text-primary font-label-md py-sm rounded-full hover:bg-secondary-fixed-dim transition-colors flex justify-center items-center gap-xs"
              onClick={() => setPage("chat", `${pet.name}의 병원 진료 전 준비할 기록과 질문 목록을 정리해줘.`)}
              type="button"
            >
              <Icon className="text-[18px]" children="call" />
              진료 준비 상담
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}

function RegisterPetPage({
  initialPet,
  onCancel,
  onSave,
}: {
  initialPet: PetProfile | null;
  onCancel: () => void;
  onSave: (pet: PetProfile) => void;
}) {
  const [form, setForm] = useState<PetProfile>(
    initialPet ?? {
      id: "",
      name: "",
      species: "강아지",
      breed: "",
      age: "",
      weight: "",
      status: "관찰 중",
      vet: "",
      note: "",
      photoUrl: dogPhoto,
    },
  );
  const [uploadError, setUploadError] = useState<string | null>(null);

  async function onPhotoChange(file: File | undefined) {
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      setUploadError("이미지 파일만 업로드할 수 있습니다.");
      return;
    }
    if (file.size > 2 * 1024 * 1024) {
      setUploadError("브라우저 저장을 위해 2MB 이하 이미지를 권장합니다.");
      return;
    }
    setUploadError(null);
    const photoUrl = await fileToDataUrl(file);
    setForm((previous) => ({ ...previous, photoUrl }));
  }

  function update<K extends keyof PetProfile>(key: K, value: PetProfile[K]) {
    setForm((previous) => ({ ...previous, [key]: value }));
  }

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const savedPet: PetProfile = {
      ...form,
      id: form.id || createId("pet"),
      name: form.name.trim() || "이름 없는 친구",
      photoUrl: form.photoUrl || fallbackPhoto(form.species),
    };
    onSave(savedPet);
  }

  return (
    <main className="flex-grow pt-[88px] px-margin-mobile md:px-xl max-w-container-max mx-auto w-full pb-xxl bg-background text-on-surface font-body-md min-h-screen">
      <header className="my-lg">
        <h1 className="text-headline-lg font-headline-lg text-primary">{initialPet ? "반려동물 프로필 수정" : "반려동물 등록"}</h1>
        <p className="text-body-lg font-body-lg text-on-surface-variant">사진과 기본 정보를 등록하면 상담 질문에 자동으로 맥락이 붙습니다.</p>
      </header>
      <form className="grid grid-cols-1 lg:grid-cols-12 gap-lg" onSubmit={onSubmit}>
        <section className="lg:col-span-4 bg-surface-container-lowest rounded-[1.5rem] p-lg shadow-soft border border-outline-variant/30">
          <PetPhoto className="w-full aspect-square rounded-[1.5rem] shadow-soft mb-md" pet={form} />
          <label className="block">
            <span className="text-label-md font-label-md text-on-surface-variant">내 반려동물 사진 업로드</span>
            <input className="mt-sm block w-full text-label-md" onChange={(event) => void onPhotoChange(event.target.files?.[0])} type="file" accept="image/*" />
          </label>
          {uploadError && <p className="mt-sm text-label-md font-label-md text-error">{uploadError}</p>}
          <div className="grid grid-cols-2 gap-sm mt-md">
            <button className="bg-secondary-container text-primary rounded-lg py-sm font-label-md" onClick={() => update("photoUrl", dogPhoto)} type="button">
              강아지 기본 사진
            </button>
            <button className="bg-secondary-container text-primary rounded-lg py-sm font-label-md" onClick={() => update("photoUrl", catPhoto)} type="button">
              고양이 기본 사진
            </button>
          </div>
        </section>

        <section className="lg:col-span-8 bg-surface-container-lowest rounded-[1.5rem] p-lg shadow-soft border border-outline-variant/30">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-md">
            <label className="flex flex-col gap-xs">
              <span className="text-label-md font-label-md text-on-surface-variant">이름</span>
              <input className="bg-surface-container-low rounded-lg px-md py-sm focus:ring-2 focus:ring-primary outline-none" onChange={(event) => update("name", event.target.value)} required value={form.name} />
            </label>
            <label className="flex flex-col gap-xs">
              <span className="text-label-md font-label-md text-on-surface-variant">종</span>
              <select className="bg-surface-container-low rounded-lg px-md py-sm focus:ring-2 focus:ring-primary outline-none" onChange={(event) => update("species", event.target.value)} value={form.species}>
                <option>강아지</option>
                <option>고양이</option>
                <option>토끼</option>
                <option>햄스터</option>
                <option>기타</option>
              </select>
            </label>
            <label className="flex flex-col gap-xs">
              <span className="text-label-md font-label-md text-on-surface-variant">품종</span>
              <input className="bg-surface-container-low rounded-lg px-md py-sm focus:ring-2 focus:ring-primary outline-none" onChange={(event) => update("breed", event.target.value)} placeholder="예: 골든 리트리버" value={form.breed} />
            </label>
            <label className="flex flex-col gap-xs">
              <span className="text-label-md font-label-md text-on-surface-variant">나이</span>
              <input className="bg-surface-container-low rounded-lg px-md py-sm focus:ring-2 focus:ring-primary outline-none" onChange={(event) => update("age", event.target.value)} placeholder="예: 4세" value={form.age} />
            </label>
            <label className="flex flex-col gap-xs">
              <span className="text-label-md font-label-md text-on-surface-variant">체중</span>
              <input className="bg-surface-container-low rounded-lg px-md py-sm focus:ring-2 focus:ring-primary outline-none" onChange={(event) => update("weight", event.target.value)} placeholder="예: 5.1kg" value={form.weight} />
            </label>
            <label className="flex flex-col gap-xs">
              <span className="text-label-md font-label-md text-on-surface-variant">상태</span>
              <input className="bg-surface-container-low rounded-lg px-md py-sm focus:ring-2 focus:ring-primary outline-none" onChange={(event) => update("status", event.target.value)} placeholder="예: 건강함, 관찰 중" value={form.status} />
            </label>
            <label className="flex flex-col gap-xs md:col-span-2">
              <span className="text-label-md font-label-md text-on-surface-variant">담당 병원</span>
              <input className="bg-surface-container-low rounded-lg px-md py-sm focus:ring-2 focus:ring-primary outline-none" onChange={(event) => update("vet", event.target.value)} placeholder="예: 우리동네 동물병원" value={form.vet} />
            </label>
            <label className="flex flex-col gap-xs md:col-span-2">
              <span className="text-label-md font-label-md text-on-surface-variant">특이사항</span>
              <textarea className="bg-surface-container-low rounded-lg px-md py-sm min-h-32 focus:ring-2 focus:ring-primary outline-none" onChange={(event) => update("note", event.target.value)} placeholder="알레르기, 약 복용, 성격, 시설 이용 시 주의사항 등을 적어주세요." value={form.note} />
            </label>
          </div>
          <div className="flex flex-col sm:flex-row justify-end gap-sm mt-lg">
            <button className="bg-surface-container text-primary px-lg py-md rounded-lg font-label-md" onClick={onCancel} type="button">
              취소
            </button>
            <button className="bg-primary text-on-primary px-lg py-md rounded-lg font-label-md shadow-soft" type="submit">
              {initialPet ? "수정 완료" : "등록 완료"}
            </button>
          </div>
        </section>
      </form>
    </main>
  );
}

function AssistantAvatar() {
  return (
    <div className="w-8 h-8 rounded-full bg-secondary-container flex items-center justify-center shrink-0 mt-1 shadow-soft">
      <Icon className="text-secondary text-sm" children="smart_toy" />
    </div>
  );
}

function ResponseMeta({ response }: { response: QueryResponse }) {
  const tone =
    response.answer_type === "document_grounded"
      ? "bg-secondary-fixed text-primary"
      : response.answer_type === "ai_general"
        ? "bg-primary-fixed text-primary"
        : "bg-error-container text-on-error-container";

  return (
    <div className="mt-sm flex flex-wrap gap-xs">
      <span className={`px-3 py-1 rounded-full text-label-sm font-label-sm ${tone}`}>{answerLabel(response)}</span>
      <span className="px-3 py-1 rounded-full text-label-sm font-label-sm bg-surface-container text-on-surface-variant">{response.generation_mode}</span>
      <span className="px-3 py-1 rounded-full text-label-sm font-label-sm bg-surface-container text-on-surface-variant">
        신뢰도 {Math.round(response.retrieval_confidence * 100)}%
      </span>
    </div>
  );
}

function Citations({ response }: { response: QueryResponse }) {
  if (!response.citations.length) {
    return response.answer_type === "no_evidence" ? (
      <div className="mt-sm bg-error-container/50 text-on-error-container p-sm rounded-lg text-label-md font-label-md">
        문서 근거가 부족합니다. AI 일반 조언을 켜면 제한된 범위에서 보조 답변을 받을 수 있습니다.
      </div>
    ) : null;
  }

  return (
    <details className="mt-sm bg-surface-container-low rounded-lg p-sm border border-outline-variant/30" open>
      <summary className="cursor-pointer text-label-md font-label-md text-primary">근거 문서 {response.citations.length}개</summary>
      <div className="mt-sm space-y-sm">
        {response.citations.map((citation, index) => (
          <article className="bg-surface-container-lowest border-l-4 border-primary rounded-lg p-sm shadow-soft" key={`${citation.document_id}-${citation.locator}-${index}`}>
            <div className="text-label-md font-label-md text-primary">
              {index + 1}.{" "}
              {citation.source_url ? (
                <a href={citation.source_url} rel="noreferrer" target="_blank">
                  {citation.title}
                </a>
              ) : (
                citation.title
              )}
            </div>
            <p className="text-label-sm font-label-sm text-on-surface-variant mt-xs">
              {citation.locator} · 검색 점수 {(citation.score ?? 0).toFixed(2)}
            </p>
            {citation.snippet && <p className="text-label-md font-label-md text-on-surface-variant mt-xs">{citation.snippet}</p>}
          </article>
        ))}
      </div>
    </details>
  );
}

function MessageItem({ message }: { message: ChatMessage }) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end gap-sm">
        <div className="bg-primary text-on-primary p-md rounded-xl rounded-tr-sm shadow-soft max-w-[80%]">
          <p className="text-body-md font-body-md whitespace-pre-wrap">{message.content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start gap-sm">
      <AssistantAvatar />
      <div className="bg-surface-container-lowest text-on-surface p-md rounded-xl rounded-tl-sm shadow-soft max-w-[80%] border border-outline-variant/10">
        <p className="text-body-md font-body-md whitespace-pre-wrap">{message.content}</p>
        {message.response && (
          <>
            <ResponseMeta response={message.response} />
            {message.response.safety_notice && <div className="mt-sm bg-error-container/60 text-on-error-container p-sm rounded-lg text-label-md font-label-md">{message.response.safety_notice}</div>}
            <Citations response={message.response} />
          </>
        )}
      </div>
    </div>
  );
}

function ChatPage({
  apiReady,
  assistantMessages,
  draft,
  error,
  loading,
  messages,
  selectedPet,
  setDraft,
  setMessages,
  sourceCount,
  submit,
  useOpenAI,
  setUseOpenAI,
}: {
  apiReady: boolean;
  assistantMessages: ChatMessage[];
  draft: string;
  error: string | null;
  loading: boolean;
  messages: ChatMessage[];
  selectedPet: PetProfile;
  setDraft: (value: string) => void;
  setMessages: (value: ChatMessage[]) => void;
  sourceCount: number;
  submit: (question: string) => Promise<void>;
  useOpenAI: boolean;
  setUseOpenAI: (value: boolean) => void;
}) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submit(draft);
  }

  return (
    <main className="flex flex-1 pt-[72px] h-screen overflow-hidden">
      <aside className="hidden md:flex flex-col w-80 bg-surface-container-lowest border-r border-outline-variant/30 overflow-y-auto">
        <div className="p-md border-b border-outline-variant/20">
          <h2 className="text-label-md font-label-md text-on-surface-variant mb-xs">진행 중인 상담</h2>
          <div className="bg-surface-container-low p-sm rounded-lg flex items-center gap-sm border border-primary/20">
            <PetPhoto className="w-10 h-10 rounded-full" pet={selectedPet} />
            <div>
              <p className="text-body-md font-body-md font-semibold">
                {selectedPet.name} ({selectedPet.breed || selectedPet.species})
              </p>
              <p className="text-label-sm font-label-sm text-on-surface-variant">
                {messages.length > 0 ? "상담 진행 중" : "대기 중"} · 출처 {sourceCount}개
              </p>
            </div>
          </div>
          <label className="mt-sm flex items-center gap-xs text-label-md font-label-md text-primary">
            <input checked={useOpenAI} className="rounded border-outline-variant text-primary focus:ring-primary" onChange={(event) => setUseOpenAI(event.target.checked)} type="checkbox" />
            AI 일반 조언 허용
          </label>
        </div>

        <div className="p-md flex-1">
          <h2 className="text-label-md font-label-md text-on-surface-variant mb-sm">히스토리</h2>
          <ul className="space-y-sm">
            {assistantMessages.length > 0
              ? assistantMessages
                  .slice(-4)
                  .reverse()
                  .map((message) => (
                    <li key={message.id}>
                      <div className="p-sm rounded-lg flex items-start gap-sm hover:bg-surface-container-low transition-colors">
                        <Icon className="text-secondary mt-1" children="check_circle" />
                        <div>
                          <p className="text-body-md font-body-md text-on-surface">{message.response ? answerLabel(message.response) : "상담 답변"}</p>
                          <p className="text-label-sm font-label-sm text-on-surface-variant">{message.content.slice(0, 44)}</p>
                        </div>
                      </div>
                    </li>
                  ))
              : historySeed.map((item) => (
                  <li key={item.title}>
                    <div className="p-sm rounded-lg flex items-start gap-sm hover:bg-surface-container-low transition-colors">
                      <Icon className="text-secondary mt-1" children="check_circle" />
                      <div>
                        <p className="text-body-md font-body-md text-on-surface">{item.title}</p>
                        <p className="text-label-sm font-label-sm text-on-surface-variant">{item.meta}</p>
                      </div>
                    </div>
                  </li>
                ))}
          </ul>
        </div>

        <div className="p-md border-t border-outline-variant/20 mt-auto">
          <button className="w-full py-2 px-4 rounded-lg bg-surface-container border border-outline-variant text-on-surface font-label-md text-label-md flex items-center justify-center gap-xs hover:bg-surface-container-high transition-colors" onClick={() => setMessages([])} type="button">
            <Icon className="text-sm" children="add" />새 상담 시작
          </button>
        </div>
      </aside>

      <section className="flex-1 flex flex-col bg-background relative max-w-container-max mx-auto w-full">
        <div className="px-margin-mobile md:px-xl py-sm bg-surface-container-lowest border-b border-outline-variant/20 flex items-center gap-2">
          <div className="h-1 flex-1 bg-primary rounded-full" />
          <div className={`h-1 flex-1 rounded-full ${messages.length ? "bg-primary" : "bg-secondary-fixed"}`} />
          <div className={`h-1 flex-1 rounded-full ${assistantMessages.length ? "bg-primary" : "bg-secondary-fixed"}`} />
          <div className="h-1 flex-1 bg-surface-variant rounded-full" />
          <span className="text-label-sm font-label-sm text-primary ml-2">{apiReady ? "상담 가능" : "API 연결 대기"}</span>
        </div>

        <div className="mx-margin-mobile md:mx-xl mt-md bg-error-container text-on-error-container px-md py-sm rounded-lg flex items-center gap-sm shadow-soft">
          <Icon className="text-error" children="info" />
          <p className="text-label-md font-label-md flex-1">{selectedPet.name}가 호흡 곤란, 반복 경련, 의식 저하, 심한 출혈을 보이면 즉시 응급 진료를 받으세요.</p>
          <span className="text-label-sm font-label-sm">{apiReady ? "API 정상" : "API 확인 필요"}</span>
        </div>

        <div className="mx-margin-mobile md:mx-xl mt-sm flex flex-wrap gap-2">
          {chips.map((chip) => (
            <button className="px-4 py-2 bg-surface-container-lowest border-2 border-primary/20 text-primary rounded-full text-label-md font-label-md hover:bg-secondary-fixed hover:border-primary transition-all shadow-sm" key={chip} onClick={() => void submit(chipQuestions[chip])} type="button">
              {chip}
            </button>
          ))}
        </div>

        <div className="flex-1 overflow-y-auto p-margin-mobile md:p-xl space-y-lg scrollbar-hide flex flex-col max-w-[800px] mx-auto w-full pb-40 md:pb-44">
          <div className="text-center">
            <span className="text-label-sm font-label-sm text-outline px-2 py-1 bg-surface-container-low rounded-full">오늘 상담</span>
          </div>

          {messages.length === 0 && (
            <div className="flex justify-start gap-sm">
              <AssistantAvatar />
              <div className="bg-surface-container-lowest text-on-surface p-md rounded-xl rounded-tl-sm shadow-soft max-w-[80%] border border-outline-variant/10">
                <p className="text-body-md font-body-md mb-2">안녕하세요. {selectedPet.name}의 상태를 알려주시면 문서 근거와 공식 출처를 먼저 확인하고, 필요한 경우 AI 일반 조언을 덧붙이겠습니다.</p>
                <p className="text-body-md font-body-md">예: “오늘 아침부터 토하고 밥을 안 먹어요”, “호텔 입실 전 준비물이 궁금해요”</p>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <MessageItem key={message.id} message={message} />
          ))}

          {loading && (
            <div className="flex justify-start gap-sm">
              <AssistantAvatar />
              <div className="bg-surface-container-lowest text-on-surface p-md rounded-xl rounded-tl-sm shadow-soft max-w-[80%] border border-outline-variant/10">
                <p className="text-body-md font-body-md">케어 문서와 공식 출처를 검색하고 있습니다...</p>
              </div>
            </div>
          )}

          {error && <div className="bg-error-container text-on-error-container p-md rounded-lg shadow-soft text-label-md font-label-md">{error}</div>}
          <div ref={bottomRef} />
        </div>

        <form className="absolute bottom-0 left-0 w-full bg-surface-container-lowest border-t border-outline-variant/20 p-margin-mobile md:p-xl flex gap-sm items-end shadow-[0_-4px_20px_rgba(0,0,0,0.02)]" onSubmit={onSubmit}>
          <button className="p-3 text-secondary hover:bg-surface-container-low rounded-full transition-colors shrink-0 mb-1" onClick={() => void submit(`${selectedPet.name}를 병원에 데려가기 전 보호자가 기록하고 준비해야 할 정보는 무엇인가요?`)} type="button">
            <Icon children="add_circle" />
          </button>
          <div className="flex-1 relative">
            <textarea
              className="w-full bg-surface-container-low border-none rounded-xl py-3 px-4 text-body-md font-body-md text-on-surface focus:ring-2 focus:ring-primary focus:bg-surface-container-lowest resize-none max-h-32 shadow-inner min-h-[56px]"
              disabled={!apiReady || loading}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
                  event.preventDefault();
                  void submit(draft);
                }
              }}
              placeholder={`${selectedPet.name}의 증상이나 궁금한 점을 입력하세요...`}
              rows={1}
              style={{ scrollbarWidth: "none" }}
              value={draft}
            />
          </div>
          <button className="p-3 bg-primary text-on-primary rounded-xl hover:bg-primary-container hover:text-on-primary-container transition-colors shrink-0 shadow-soft mb-1 flex items-center justify-center h-[56px] w-[56px]" disabled={!apiReady || loading || !draft.trim()} type="submit">
            <Icon children="send" />
          </button>
        </form>
      </section>
    </main>
  );
}

function App() {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [authMode, setAuthMode] = useState<"login" | "signup" | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);
  const [authStatus, setAuthStatus] = useState<string | null>(null);
  const [page, setPageState] = useState<Page>("home");
  const [apiReady, setApiReady] = useState(false);
  const [sourceCount, setSourceCount] = useState(0);
  const [useOpenAI, setUseOpenAI] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>(() =>
    loadStoredMessages(GUEST_USER_ID),
  );
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pets, setPets] = useState<PetProfile[]>(() => loadStoredPets(GUEST_USER_ID));
  const [selectedPetId, setSelectedPetId] = useState(
    () => loadStoredPets(GUEST_USER_ID)[0]?.id ?? "bella",
  );
  const [editingPetId, setEditingPetId] = useState<string | null>(null);

  const generationMode: GenerationMode = useOpenAI ? "openai" : "local";
  const assistantMessages = messages.filter((message) => message.role === "assistant");
  const selectedPet = useMemo(() => pets.find((pet) => pet.id === selectedPetId) ?? pets[0] ?? defaultPets[0], [pets, selectedPetId]);
  const editingPet = editingPetId ? pets.find((pet) => pet.id === editingPetId) ?? null : null;

  async function handleAuthSubmit(
    mode: "login" | "signup",
    email: string,
    password: string,
    name: string,
  ) {
    if (!supabase) return;
    setAuthError(null);
    setAuthStatus(null);
    if (mode === "signup") {
      const { error: signUpError } = await supabase.auth.signUp({
        email,
        password,
        options: { data: { name: name || email.split("@")[0] } },
      });
      if (signUpError) {
        setAuthError(signUpError.message);
        return;
      }
      setAuthStatus("회원가입이 완료되었습니다. 이메일 확인이 필요한 설정이면 메일을 확인해 주세요.");
    } else {
      const { error: signInError } = await supabase.auth.signInWithPassword({ email, password });
      if (signInError) {
        setAuthError(signInError.message);
        return;
      }
      setAuthMode(null);
    }
  }

  async function handleLogout() {
    if (supabase) {
      await supabase.auth.signOut();
    }
    saveCurrentUser(null);
    setCurrentUser(null);
    setAccessToken(null);
    const guestPets = loadStoredPets(GUEST_USER_ID);
    setPets(guestPets);
    setMessages(loadStoredMessages(GUEST_USER_ID));
    setDraft("");
    setEditingPetId(null);
    setSelectedPetId(guestPets[0]?.id ?? "bella");
    setPageState("home");
  }

  function setPage(nextPage: Page, question?: string) {
    if (nextPage === "register") {
      setEditingPetId(null);
    }
    setPageState(nextPage);
    if (question) {
      window.setTimeout(() => void submit(question), 0);
    }
  }

  function openEditProfile() {
    setEditingPetId(selectedPet.id);
    setPageState("register");
  }

  function savePet(pet: PetProfile) {
    setPets((previous) => {
      const exists = previous.some((item) => item.id === pet.id);
      return exists ? previous.map((item) => (item.id === pet.id ? pet : item)) : [...previous, pet];
    });
    if (accessToken) {
      void saveMyPet(accessToken, pet).catch((caught) => {
        setError(caught instanceof Error ? caught.message : "반려동물 정보를 DB에 저장하지 못했습니다.");
      });
    }
    setSelectedPetId(pet.id);
    setEditingPetId(null);
    setPageState("profile");
  }

  useEffect(() => {
    const storageUserId = currentUser?.id ?? GUEST_USER_ID;
    saveStoredPets(storageUserId, pets);
  }, [currentUser, pets]);

  useEffect(() => {
    const storageUserId = currentUser?.id ?? GUEST_USER_ID;
    saveStoredMessages(storageUserId, messages);
    if (currentUser && accessToken) {
      void saveMyMessages(accessToken, selectedPet.id, messages).catch(() => {
        // Keep local fallback data even if remote sync is temporarily unavailable.
      });
    }
  }, [accessToken, currentUser, messages, selectedPet.id]);

  useEffect(() => {
    if (!supabase) return;

    function applySession(session: { access_token?: string; user?: { id: string; email?: string; user_metadata?: { name?: string } } } | null) {
      if (!session?.user || !session.access_token) {
        return;
      }
      const email = session.user.email ?? "user@supabase.local";
      const user: AuthUser = {
        id: session.user.id,
        email,
        name: session.user.user_metadata?.name || email.split("@")[0] || "보호자",
      };
      saveCurrentUser(user);
      setCurrentUser(user);
      setAccessToken(session.access_token);
      setAuthMode(null);
    }

    void supabase.auth.getSession().then(({ data }) => {
      applySession(data.session);
    });
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      applySession(session);
      if (!session) {
        saveCurrentUser(null);
        setCurrentUser(null);
        setAccessToken(null);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (!currentUser || !accessToken) return;

    const token = accessToken;
    const userId = currentUser.id;
    let cancelled = false;
    async function loadRemoteUserData() {
      try {
        const [remotePets, remoteMessages] = await Promise.all([
          getMyPets(token),
          getMyMessages(token),
        ]);
        if (cancelled) return;
        const nextPets = remotePets.length ? remotePets : loadStoredPets(userId);
        const nextMessages = remoteMessages.length
          ? remoteMessages
          : loadStoredMessages(userId);
        setPets(nextPets);
        setMessages(nextMessages);
        setSelectedPetId(nextPets[0]?.id ?? "bella");
        setError(null);
      } catch (caught) {
        if (!cancelled) {
          const fallbackPets = loadStoredPets(userId);
          setPets(fallbackPets);
          setMessages(loadStoredMessages(userId));
          setSelectedPetId(fallbackPets[0]?.id ?? "bella");
          console.warn("User data sync failed; using local fallback.", caught);
        }
      }
    }

    void loadRemoteUserData();
    return () => {
      cancelled = true;
    };
  }, [accessToken, currentUser]);

  useEffect(() => {
    if (!pets.some((pet) => pet.id === selectedPetId) && pets[0]) {
      setSelectedPetId(pets[0].id);
    }
  }, [pets, selectedPetId]);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        await getHealth();
        const catalog = await getSources();
        if (!cancelled) {
          setApiReady(true);
          setSourceCount(catalog.sources.length);
          setError(null);
        }
      } catch (caught) {
        if (!cancelled) {
          setApiReady(false);
          setError(caught instanceof Error ? caught.message : "API 연결을 확인해 주세요.");
        }
      }
    }

    void bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  async function submit(question: string) {
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    const contextualQuestion = `${trimmed}\n\n[상담 대상]\n이름: ${selectedPet.name}\n종: ${selectedPet.species}\n품종: ${selectedPet.breed || "미입력"}\n나이: ${selectedPet.age || "미입력"}\n체중: ${selectedPet.weight || "미입력"}\n특이사항: ${selectedPet.note || "없음"}`;

    setPageState("chat");
    setMessages((previous) => [...previous, userMessage(trimmed)]);
    setDraft("");
    setLoading(true);
    setError(null);

    try {
      const response = await askQuestion(contextualQuestion, generationMode);
      setMessages((previous) => [...previous, assistantMessage(response)]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "질의 처리 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={page === "chat" ? "flex flex-col h-screen overflow-hidden text-on-surface bg-background" : "min-h-screen bg-surface text-on-surface font-body-md flex flex-col"}>
      <TopNav
        activePage={page}
        onEmergency={() => void submit("응급 신호가 보일 때 보호자가 즉시 확인하고 병원에 전달해야 할 정보는 무엇인가요?")}
        onLoginClick={() => {
          setAuthMode("login");
          setAuthError(null);
          setAuthStatus(null);
        }}
        onLogout={handleLogout}
        onSignupClick={() => {
          setAuthMode("signup");
          setAuthError(null);
          setAuthStatus(null);
        }}
        setPage={setPage}
        user={currentUser}
      />
      {authMode && (
        <AuthDialog
          authError={authError}
          authMode={authMode}
          authStatus={authStatus}
          onAuthSubmit={handleAuthSubmit}
          onClose={() => setAuthMode(null)}
        />
      )}
      {page === "home" && <LandingPage selectedPet={selectedPet} setPage={setPage} />}
      {page === "dashboard" && <DashboardPage pets={pets} selectedPet={selectedPet} setPage={setPage} setSelectedPetId={setSelectedPetId} />}
      {page === "profile" && <ProfilePage onEdit={openEditProfile} pet={selectedPet} setPage={setPage} />}
      {page === "register" && <RegisterPetPage initialPet={editingPet} onCancel={() => setPageState("dashboard")} onSave={savePet} />}
      {page === "chat" && (
        <ChatPage
          apiReady={apiReady}
          assistantMessages={assistantMessages}
          draft={draft}
          error={error}
          loading={loading}
          messages={messages}
          selectedPet={selectedPet}
          setDraft={setDraft}
          setMessages={(nextMessages) => {
            setMessages(nextMessages);
            setError(null);
          }}
          setUseOpenAI={setUseOpenAI}
          sourceCount={sourceCount}
          submit={submit}
          useOpenAI={useOpenAI}
        />
      )}
    </div>
  );
}

export default App;
