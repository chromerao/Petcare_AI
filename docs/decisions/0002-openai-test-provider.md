# ADR 0002: OpenAI test provider

- Status: Accepted for development baseline
- Date: 2026-06-15

## Context

팀은 OpenAI 유료 API 키를 개발 환경에서 사용할 수 있지만, 초기 RAG 실험에서 과도한 토큰 비용과 내부 문서 노출을 피해야 합니다. 로컬 모델 교체 가능성도 유지해야 합니다.

## Decision

- 개발 기본 공급자는 OpenAI Responses API로 둡니다.
- 명시적으로 요청된 테스트 모델 `gpt-4.1-mini`를 기본값으로 사용합니다.
- 기본 출력 상한은 500토큰, 입력은 24,000문자, 타임아웃은 20초, 재시도는 1회입니다.
- API의 응답 저장 옵션은 기본적으로 `false`입니다.
- API 키는 `OPENAI_API_KEY` 또는 `DOCQA_OPENAI_API_KEY`에서 읽으며 `SecretStr`로 보관합니다.
- 프롬프트, 검색 원문, 모델 출력 전문은 애플리케이션 로그에 남기지 않습니다.
- 단위 테스트는 가짜 클라이언트만 사용하고 실제 유료 호출은 `external` 마커로 분리합니다.

## Consequences

- 저비용 모델로 빠르게 품질 기준선을 만들 수 있습니다.
- 모델과 공급자는 환경변수 및 어댑터 경계로 교체할 수 있습니다.
- 실제 시설 문서를 외부 API로 보내기 전 별도 데이터 전송 승인이 필요합니다.

