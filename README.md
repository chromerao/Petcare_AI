# DocQA Lab

내부 문서와 외부 공개 문서를 함께 검색해 근거와 출처를 제시하는 LLM 기반 질의응답 시스템의 팀 프로젝트 저장소입니다.

선정 주제는 **PetCare Expert Guide**입니다. 반려동물 호텔/유치원 운영 규정 Q&A에서 출발해, 보호자가 겪는 건강 이상 신호, 독성 섭취, 식이·체중, 행동, 생활 환경 문제까지 안내하는 반려동물 케어 전문가형 질의응답 시스템으로 확장합니다. 특정 LLM, 임베딩 모델, 벡터 DB, 배포 사업자는 데이터 기준선을 측정한 뒤 ADR(Architecture Decision Record)로 확정합니다.

## 현재 제공되는 것

- 구현 가능성과 참신성을 함께 평가한 주제 후보 12개
- 4인/5인 팀 역할 분담과 코드 오너십 기준
- FastAPI 기반 API와 React/Vite 제품형 프론트엔드
- 수집과 RAG 계층의 공급자 독립 인터페이스
- 시설 운영 합성 문서와 보호자 케어 샘플 문서 기반 로컬 검색
- OpenAI `gpt-4.1-mini` 선택 모드와 문서 근거 부족 시 AI 일반 조언 fallback
- 루트 및 파트별 `AGENTS.md` 작업 지침
- 보안, 데이터 거버넌스, 평가, 기여 규칙
- GitHub Actions CI, PR/이슈 템플릿, Docker 실행 기반

## 먼저 읽을 문서

1. [PetCare MVP](docs/T12_MVP.md)에서 범위와 데이터 출처를 확인합니다.
2. [주제 선정 기록](docs/TOPIC_SELECTION.md)에서 성공 지표와 제외 범위를 확인합니다.
3. [역할 분담](docs/TEAM_ROLES.md)에서 4인 또는 5인 구성을 확정합니다.
4. [아키텍처](docs/ARCHITECTURE.md)와 [데이터 거버넌스](docs/DATA_GOVERNANCE.md)를 검토합니다.
5. 모든 작업자는 [AGENTS.md](AGENTS.md)와 작업 디렉터리의 추가 지침을 따릅니다.

## 권장 기술 베이스라인

| 영역 | 초기 선택 | 비고 |
|---|---|---|
| 언어 | Python 3.11 | 기존 `uv` 프로젝트 유지 |
| API | FastAPI | 비동기 처리 및 명확한 API 계약 |
| Frontend | React + Vite | `DESIGN/` HTML 시안을 제품형 UI로 구현 |
| Prototype UI | Streamlit | 빠른 내부 검증용 보조 데모 |
| 패키지/환경 | uv | 빠른 재현과 lockfile 관리 |
| 테스트/품질 | pytest, Ruff, mypy | CI에서 자동 검사 |
| 저장소 | 미정 | 로컬/pgvector/관리형 벡터 DB를 ADR로 결정 |
| LLM | OpenAI `gpt-4.1-mini` | 개발 기준선, Responses API, 800 출력토큰 상한 |
| 임베딩 | 미정 | 검색 기준선 측정 후 ADR로 결정 |

## 빠른 시작

```powershell
Copy-Item .env.example .env
uv sync --all-extras --dev
uv run uvicorn docqa.api.main:app --reload
```

별도 터미널에서 React 프론트엔드를 실행합니다.

```powershell
cd frontend
npm install
npm run dev
```

Node.js가 설치되어 있으면 Windows 실행 스크립트를 사용할 수도 있습니다.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_frontend.ps1
```

API와 React 프론트엔드를 한 터미널에서 함께 실행하려면 아래 명령을 사용합니다. 이 방법을 쓰면 프론트가 실제 API 포트를 자동으로 바라보므로 `Failed to fetch`를 피하기 쉽습니다.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_fullstack.ps1
```

Streamlit 프로토타입은 보조 데모로 남겨두었습니다.

```powershell
uv run --extra ui streamlit run ui/app.py
```

- API 문서: `http://localhost:8000/docs`
- 상태 확인: `http://localhost:8000/api/v1/health`
- React UI: `http://localhost:5173`
- Streamlit prototype: `http://localhost:8501`

`/api/v1/query`는 합성 내부 SOP와 보호자 케어 문서를 로컬 키워드 검색합니다. 기본 `local` 모드는 과금 없이 문서 근거를 보여줍니다. UI에서 **AI 일반 조언 허용**을 켜면 `gpt-4.1-mini`가 문서 근거 답변을 작성하고, 검색 근거가 없을 때는 `ai_general` 유형으로 일반 교육 목적의 조언을 생성합니다.

AI 일반 조언은 실제 수의사의 진단·처방·약물 용량 지시를 대신하지 않습니다. 독성 섭취, 호흡곤란, 발작, 의식 저하, 반복 구토/설사, 심한 통증은 즉시 동물병원 또는 응급병원 상담으로 안내합니다.

`.env`의 키 값은 출력하거나 Git에 추가하지 마세요. 기본 LLM 제한과 선택 근거는 [ADR 0002](docs/decisions/0002-openai-test-provider.md)에 기록되어 있습니다.

## 개발 명령

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run python scripts/evaluate_retrieval.py
cd frontend
npm run build
```

자동 수정은 `uv run ruff check . --fix`와 `uv run ruff format .`을 사용합니다.

## 직접 테스트

무료 로컬 스모크 테스트는 API를 임시 실행해 health, 출처 목록, 현재 query 상태를 확인하고 자동 종료합니다.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/smoke_test.ps1
```

OpenAI 키와 계정 연결을 실제로 확인하려면 아래 명령을 별도로 실행합니다. 이 테스트는 `gpt-4.1-mini`를 최대 64 출력토큰으로 한 번 호출하므로 소액 과금됩니다. 키 값은 출력하지 않습니다.

```powershell
uv run python scripts/openai_smoke_test.py
```

전체 화면을 직접 확인하려면 API와 UI를 각각 실행합니다.

```powershell
uv run uvicorn docqa.api.main:app --reload
cd frontend
npm run dev
```

Windows에서는 프로젝트 경로를 고정한 실행 스크립트를 권장합니다. 기본 포트 8000 또는 8501이 사용 중이면 다음 빈 포트를 자동으로 선택하고 실제 접속 주소를 터미널에 출력합니다.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_app.ps1
```

## 프로젝트 구조

```text
.
|-- .github/                 # CI, PR 및 이슈 템플릿
|-- data/                    # Git에 올리지 않는 로컬 데이터 안내
|-- docs/                    # 주제, 설계, 평가, 운영 문서
|-- infra/                   # 컨테이너 및 배포 설정
|-- DESIGN/                  # 원본 HTML 디자인과 디자인 시스템
|-- frontend/                # React/Vite 제품형 프론트엔드
|-- src/docqa/
|   |-- api/                 # HTTP 계약과 라우팅
|   |-- core/                # 설정, 공통 정책, 로깅
|   |-- ingestion/           # 문서 수집/정규화 계약
|   |-- providers/           # LLM, 임베딩, 저장소 어댑터
|   `-- rag/                 # 검색, 재정렬, 답변 생성 계약
|-- tests/                   # 단위/통합/평가 테스트
`-- ui/                      # Streamlit 보조 프로토타입
```

## Git 협업 규칙

- `main` 직접 push를 금지하고 PR을 통해 병합합니다.
- 브랜치는 `feat/<issue>-내용`, `fix/<issue>-내용`, `docs/<issue>-내용` 형식을 권장합니다.
- 커밋은 Conventional Commits 형식(`feat:`, `fix:`, `docs:`, `test:`, `chore:`)을 사용합니다.
- PR은 가능한 작게 유지하고 최소 1인의 리뷰와 CI 통과 후 병합합니다.
- 비밀키, 원본 내부 문서, 개인정보, 운영 로그를 Git에 커밋하지 않습니다.

자세한 절차는 [CONTRIBUTING.md](CONTRIBUTING.md), 보안 신고 및 금지 사항은 [SECURITY.md](SECURITY.md)를 참고하세요.

## 완료 기준

최종 데모는 단순히 답변을 생성하는 수준이 아니라 아래 조건을 충족해야 합니다.

- 답변 문장에 확인 가능한 문서명, 페이지 또는 URL 출처가 표시된다.
- 문서 근거 답변과 AI 일반 조언을 `answer_type`으로 구분한다.
- 근거가 부족하고 AI 모드가 꺼져 있으면 추측하지 않고 보류한다.
- 내부 문서 권한이 검색과 답변 단계 모두에서 적용된다.
- 프롬프트 인젝션 문서를 신뢰하지 않고 데이터로 취급한다.
- 고정 평가셋으로 검색 품질, 답변 충실도, 지연시간을 재현 가능하게 측정한다.
- 비밀정보 및 원본 문서가 저장소와 로그에 노출되지 않는다.
"# Petcare_AI" 
