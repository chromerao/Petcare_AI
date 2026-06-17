import type { PetProfile } from "./types";

export const petProfiles: PetProfile[] = [
  {
    id: "bella",
    name: "Bella",
    species: "강아지",
    breed: "골든 리트리버",
    age: "5세",
    weight: "27kg",
    status: "관찰 안정",
    vet: "오크리지 동물병원",
    note: "위장이 예민하고 긴 산책 후 다리 피로가 가끔 있습니다.",
    photoUrl:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuACyhdaGHCc-TwvQn6RtYbW4zOmGSGKaYqqiJxu7CzYNMOXtV7urU5QkBsPxp6hfGaXCotJiNw8nCnFPdL1M7q9MislFg8awpLnvGwBV2wMiUEfa6IvG-0pjFrrhBUQVMvkP-kQGwSZ7J_rCsdJMmQHRcQPnoaYhmbeLNGiNotv6CRLS_zQUI0FoV9akQKfnN9lt1QG3mQvjOYhfA4h4lXl92VW_-fm3PGVlaGblZlEnm8yf019xCq0-BRV1lx18PPfQU_zuMHP6gE",
  },
  {
    id: "max",
    name: "Max",
    species: "고양이",
    breed: "코리안 숏헤어",
    age: "12세",
    weight: "5.1kg",
    status: "노령 케어",
    vet: "동네동물의료센터",
    note: "음수량, 배뇨 횟수, 식욕 변화를 주기적으로 관찰합니다.",
    photoUrl:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuCz4lWf4CbWjOXO8s9Er6XDF4Q6TjA-BltGVWqJFQPkPROklLPkb9EucN515YyLoqwi2lgoY4BkqthMccPfv7nZU-9XODa42Dn0VBfLtkcDi63wgkyKz3R44tDt6CYdnCYuEetCji8CUDXg09ED4tzWt25NfePw6jNri4-3MlXsxQQpsJ4DEQuz5b5rNT8qatr2SjX7mXdvqzaWbbWjpy3kgtD6IIuhmiFkHqPHhYDX9oPwJ7YToZ1nBMyQKNPAPxhfLmqW3PlYU48",
  },
];

export const quickQuestions = [
  "강아지가 초콜릿을 조금 먹었는데 어떻게 해야 하나요?",
  "사료를 바꾸고 설사를 하는데 어떤 순서로 확인해야 하나요?",
  "혼자 두면 계속 짖고 문을 긁어요. 분리불안일까요?",
  "노령묘가 물을 많이 마시고 화장실을 자주 가요.",
  "고양이 화장실을 어디에 두면 좋나요?",
  "동물이 시설에서 사라졌을 때 첫 조치는 무엇인가요?",
];

export const triageChips = [
  { label: "구토", question: "반려동물이 구토를 했을 때 어떤 증상을 기록하고 언제 병원에 가야 하나요?" },
  { label: "설사", question: "반려동물이 설사를 할 때 사료, 간식, 응급 신호를 어떤 순서로 확인해야 하나요?" },
  { label: "초콜릿 섭취", question: "강아지가 초콜릿을 조금 먹었는데 어떻게 해야 하나요?" },
  { label: "분리불안", question: "혼자 두면 계속 짖고 문을 긁어요. 분리불안일까요?" },
  { label: "물을 많이 마심", question: "노령묘가 물을 많이 마시고 화장실을 자주 가요." },
  { label: "화장실 문제", question: "고양이 화장실을 어디에 두면 좋나요?" },
  { label: "시설 입실", question: "신규 입실 시 현장 직원이 확인해야 할 내부 체크리스트는 무엇인가요?" },
  { label: "탈출 사고", question: "동물이 시설에서 사라졌을 때 첫 조치는 무엇인가요?" },
];
