# ADR 0001: Topic-neutral platform baseline

- Status: Accepted for bootstrap
- Date: 2026-06-15

## Context

프로젝트 주제가 아직 정해지지 않았지만 팀 협업, API 계약, 보안 기준, 평가 기반은 먼저 필요합니다. 특정 모델이나 검색 저장소를 지금 선택하면 데이터 특성을 확인하기 전에 불필요한 결합이 생길 수 있습니다.

## Decision

- Python 3.11과 `uv`를 공통 실행 환경으로 사용합니다.
- FastAPI를 API 경계로 사용합니다.
- 초기 UI는 Streamlit으로 연결 가능하게 두되 교체 가능한 클라이언트로 취급합니다.
- 수집, RAG, 공급자 계층을 분리하고 Protocol 기반 계약을 둡니다.
- LLM, 임베딩, 벡터 DB, 인증, 최종 배포 플랫폼은 주제 선정 후 별도 ADR로 결정합니다.

## Consequences

- 팀이 즉시 문서/평가/API 작업을 병렬로 시작할 수 있습니다.
- 주제 선정 후 어댑터와 실제 오케스트레이션 구현이 추가로 필요합니다.
- 초기 골격은 실행되지만 질의 엔드포인트는 의도적으로 비활성 상태입니다.

