# Ingestion Agent Guide

- 원본 파일을 Git 또는 테스트 fixture에 그대로 넣지 않는다. 합성/익명 샘플만 사용한다.
- 파싱 전에 파일 크기, MIME, 확장자, 페이지 수를 검증한다.
- 외부 URL 수집은 allowlist, timeout, redirect 재검증, 사설 IP 차단을 적용한다.
- 정규화 과정에서 문서 ID, 버전, 출처 위치, ACL, content hash를 잃지 않는다.
- 같은 문서를 반복 수집해도 중복 청크가 늘지 않도록 idempotency를 보장한다.
- 파서 실패는 문서 단위로 격리하고 재처리 가능한 상태를 기록한다.

