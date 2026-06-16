# PetCare AI Frontend

`DESIGN/`의 HTML 시안을 React/Vite 앱으로 구현한 프론트엔드입니다. RAG, OpenAI, 문서 검색, 권한 처리는 모두 FastAPI 백엔드가 담당하고 프론트는 `/api/v1/*`만 호출합니다.

## 실행

```powershell
cd frontend
npm install
npm run dev
```

백엔드는 별도 터미널에서 실행합니다.

```powershell
uv run uvicorn docqa.api.main:app --reload --host 127.0.0.1 --port 8000
```

API 주소를 바꿔야 하면 `frontend/.env`에 다음 값을 둡니다.

```env
VITE_DOCQA_API_BASE_URL=http://127.0.0.1:8000
```

## 구현된 화면

- 랜딩 히어로
- 서비스 상태 대시보드
- 반려동물 프로필 선택
- 트리아지 증상/상황 칩
- AI 상담 채팅
- 답변 유형/신뢰도/안전 고지
- 출처 카드와 외부 링크
- 최근 상담 이력

## 아직 데모 처리인 기능

- 진료 예약: 실제 예약 API 대신 병원 방문 준비 가이드 질문으로 연결
- 건강 기록 관리: 영구 DB 대신 브라우저 세션 상태로 관리
- 이미지 업로드: 백엔드 미지원으로 문진 중심 UX 유지
