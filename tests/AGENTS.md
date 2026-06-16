# Test Agent Guide

- 테스트에 실제 개인정보, 내부 문서, 실제 API 키를 사용하지 않는다.
- 기본 테스트는 네트워크와 유료 API 없이 반복 실행 가능해야 한다.
- 외부 연동은 fake/fixture/contract test를 우선하고 실제 호출은 `external` 마커로 분리한다.
- RAG 변경은 retrieval 지표와 answer groundedness를 별도로 검증한다.
- 권한 우회, 프롬프트 인젝션, 빈 검색 결과를 회귀 테스트에 포함한다.

