# Evaluation Plan

## 평가셋 구조

각 항목은 `question`, `expected_answer`, `required_evidence`, `forbidden_evidence`, `user_acl`, `category`, `risk_level`을 포함합니다.

## 핵심 지표

- Retrieval Recall@K: 필요한 근거가 상위 K개 안에 포함되는 비율
- MRR/nDCG: 필요한 근거의 순위 품질
- Citation Precision: 표시한 인용이 실제 답변을 지지하는 비율
- Citation Coverage: 검증 가능한 주장 중 인용이 붙은 비율
- Groundedness: 답변의 주장이 제공 근거 안에 있는 비율
- Abstention Accuracy: 근거 부족 질문에서 올바르게 답변을 보류하는 비율
- ACL Leakage Rate: 접근 불가 문서가 검색/답변/인용에 등장한 비율, 목표 0
- P95 Latency와 질문당 추정 비용

## 최소 회귀 세트

- 정상 사실 질문 20개
- 여러 문서를 조합하는 질문 10개
- 최신/구버전이 충돌하는 질문 5개
- 답이 없는 질문 10개
- 권한이 없는 문서 관련 질문 10개
- 프롬프트 인젝션 문서가 검색되는 질문 5개

모델, 프롬프트, 청킹, 임베딩, 검색 설정을 변경할 때 같은 평가셋으로 전후 결과를 기록합니다.

