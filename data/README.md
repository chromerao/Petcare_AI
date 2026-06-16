# Local Data Directory

이 디렉터리는 로컬 개발 데이터의 위치만 정의합니다. 실제 내부 문서와 파생 인덱스는 Git에 커밋하지 않습니다.

- `raw/`: 권한이 확인된 원본 문서
- `processed/`: 정규화/청킹 결과
- `indexes/`: 로컬 검색 인덱스
- `uploads/`: 개발 중 임시 업로드
- `samples/`: 공개 또는 합성된 작은 예제만 허용

팀 공유 데이터는 승인된 저장소를 사용하고 접근 권한, 보존 기간, 삭제 담당자를 `docs/DATA_GOVERNANCE.md`에 기록합니다.

