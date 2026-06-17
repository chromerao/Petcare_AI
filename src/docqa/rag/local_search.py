import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from docqa.domain.t12.source_catalog import list_t12_sources
from docqa.rag.contracts import RetrievedChunk, SearchContext

TOKEN_PATTERN = re.compile(r"[가-힣A-Za-z0-9]+")
DEFAULT_SAMPLE_DIR = Path(__file__).resolve().parents[3] / "data" / "samples"
KOREAN_SUFFIXES = (
    "했을",
    "하면",
    "해야",
    "하나요",
    "인가요",
    "에서는",
    "에서",
    "으로",
    "에게",
    "에는",
    "보다",
    "까지",
    "부터",
    "의",
    "을",
    "를",
    "은",
    "는",
    "이",
    "가",
    "과",
    "와",
)
STOPWORDS = {"무엇", "어떻게", "오늘", "정확히", "몇", "경우", "관련", "알려줘"}
ALLOWED_SINGLE_CHARACTER_TOKENS = {"약"}
CONCEPT_GROUPS = (
    ("입실", "체크인", "맡길", "맡기", "신규", "들어올"),
    ("퇴실", "체크아웃", "데려갈", "돌아갈", "반환"),
    ("탈출", "행방", "도망", "사라졌", "없어졌", "이탈"),
    (
        "질병",
        "이상증상",
        "이상",
        "증상",
        "아픈",
        "기침",
        "설사",
        "구토",
        "고열",
        "전염",
        "격리",
        "분리",
    ),
    ("투약", "약", "의약품", "복용", "먹여"),
    ("상해", "교상", "사고", "다쳤", "물렸", "부상"),
    ("환불", "취소", "위약금", "돌려받", "예약금"),
    ("보상", "배상", "책임", "손해", "치료비"),
    ("위생", "청소", "소독", "배설물", "급식", "급수"),
    ("교육", "법정의무교육", "이수", "훈련", "주기"),
    ("시설", "인력", "기준", "법령", "규정", "시행규칙", "법적근거"),
    ("등록업체", "인허가", "현황", "공공데이터", "지역별", "업소"),
    ("음식", "사료", "간식", "급여", "영양", "비만", "알레르기", "토핑", "물"),
    ("독성", "중독", "초콜릿", "포도", "자일리톨", "양파", "마늘", "백합", "먹었"),
    ("행동", "짖", "분리불안", "공격", "배변실수", "사회화", "스트레스", "훈련"),
    ("산책", "운동", "놀이", "환경", "더위", "추위", "실내", "풍부화"),
    ("예방", "접종", "구충", "검진", "치아", "중성화", "나이", "노령"),
)


@dataclass(frozen=True)
class IndexedChunk:
    chunk_id: str
    document_id: str
    title: str
    locator: str
    text: str
    acl: tuple[str, ...]
    term_counts: Counter[str]
    character_ngrams: frozenset[str]
    source_url: str | None = None


def tokenize(text: str) -> list[str]:
    normalized: list[str] = []
    for raw_token in TOKEN_PATTERN.findall(text):
        token = raw_token.lower()
        for suffix in KOREAN_SUFFIXES:
            if token.endswith(suffix) and len(token) - len(suffix) >= 1:
                token = token[: -len(suffix)]
                break
        if (len(token) > 1 or token in ALLOWED_SINGLE_CHARACTER_TOKENS) and token not in STOPWORDS:
            normalized.append(token)
    return normalized


def expand_concepts(text: str, tokens: list[str]) -> set[str]:
    expanded = set(tokens)
    compact_text = re.sub(r"\s+", "", text.lower())
    for group in CONCEPT_GROUPS:
        if any(term in compact_text for term in group):
            expanded.update(group)
    return expanded


def character_ngrams(text: str, size: int = 2) -> frozenset[str]:
    compact = re.sub(r"[^가-힣a-z0-9]", "", text.lower())
    return frozenset(compact[index : index + size] for index in range(len(compact) - size + 1))


def _parse_metadata(lines: list[str]) -> tuple[str, ...]:
    for line in lines[:5]:
        if "ACL:" in line:
            acl_value = line.split("ACL:", maxsplit=1)[1].strip().strip("> ")
            return tuple(item.strip() for item in acl_value.split(",") if item.strip())
    return ("public",)


def _parse_source_url(lines: list[str]) -> str | None:
    for line in lines[:8]:
        if "Source:" in line:
            source_url = line.split("Source:", maxsplit=1)[1].strip().strip("> ")
            return source_url or None
    return None


def _document_id(path: Path) -> str:
    if path.parent.name == "t12_internal":
        return f"internal.{path.stem}"
    return f"care.{path.stem}"


def _make_chunk(
    *,
    chunk_id: str,
    document_id: str,
    title: str,
    locator: str,
    text: str,
    acl: tuple[str, ...],
    source_url: str | None = None,
) -> IndexedChunk:
    searchable = f"{title} {locator} {text}"
    tokens = tokenize(searchable)
    return IndexedChunk(
        chunk_id=chunk_id,
        document_id=document_id,
        title=title,
        locator=locator,
        text=text,
        acl=acl,
        term_counts=Counter(tokens),
        character_ngrams=character_ngrams(searchable),
        source_url=source_url,
    )


def _append_markdown_section(
    chunks: list[IndexedChunk],
    *,
    path: Path,
    title: str,
    locator: str,
    lines: list[str],
    acl: tuple[str, ...],
    source_url: str | None,
    section_number: int,
) -> None:
    text = "\n".join(lines).strip()
    if not text:
        return
    document_id = _document_id(path)
    chunks.append(
        _make_chunk(
            chunk_id=f"{document_id}:{section_number}",
            document_id=document_id,
            title=title,
            locator=locator,
            text=text,
            acl=acl,
            source_url=source_url,
        )
    )


def load_markdown_chunks(document_dir: Path = DEFAULT_SAMPLE_DIR) -> tuple[IndexedChunk, ...]:
    chunks: list[IndexedChunk] = []
    for path in sorted(document_dir.rglob("*.md")):
        if path.name == "README.md":
            continue

        lines = path.read_text(encoding="utf-8").splitlines()
        title = next((line[2:].strip() for line in lines if line.startswith("# ")), path.stem)
        acl = _parse_metadata(lines)
        source_url = _parse_source_url(lines)
        section_title = "문서 개요"
        section_lines: list[str] = []
        section_number = 0

        for line in lines:
            if line.startswith("## "):
                section_number += 1
                _append_markdown_section(
                    chunks,
                    path=path,
                    title=title,
                    locator=section_title,
                    lines=section_lines,
                    acl=acl,
                    source_url=source_url,
                    section_number=section_number,
                )
                section_title = line[3:].strip()
                section_lines = []
            elif not line.startswith("# ") and not line.startswith(">"):
                section_lines.append(line)

        section_number += 1
        _append_markdown_section(
            chunks,
            path=path,
            title=title,
            locator=section_title,
            lines=section_lines,
            acl=acl,
            source_url=source_url,
            section_number=section_number,
        )

    return tuple(chunks)


def load_official_source_chunks() -> tuple[IndexedChunk, ...]:
    return tuple(
        _make_chunk(
            chunk_id=f"{source.source_id}:catalog",
            document_id=source.source_id,
            title=source.title,
            locator="공식 출처 안내",
            text=(
                f"발행기관: {source.publisher}. 자료 유형: {source.source_kind}. "
                f"활용 안내: {source.notes}"
            ),
            acl=("public",),
            source_url=source.url,
        )
        for source in list_t12_sources()
    )


def intent_boost(query: str, chunk: IndexedChunk) -> float:
    compact_query = re.sub(r"\s+", "", query.lower())
    compact_chunk = re.sub(r"\s+", "", f"{chunk.title}{chunk.locator}{chunk.text}".lower())
    query_tokens = set(tokenize(query))
    chunk_tokens = set(chunk.term_counts)
    boost = 0.0

    intent_rules = (
        (("입실", "체크인", "맡길", "신규"), ("입실", "체크인"), 5.0),
        (("퇴실", "체크아웃", "데려갈"), ("퇴실", "체크아웃"), 5.0),
        (("탈출", "도망", "사라졌"), ("탈출", "행방불명"), 5.0),
        (("환불", "취소", "예약금"), ("환불", "예약취소"), 5.0),
        (("교육", "이수"), ("교육", "법정의무교육"), 5.0),
        (("초콜릿", "포도", "자일리톨", "독성", "중독", "먹었"), ("독성", "중독", "응급"), 6.0),
        (("사료", "간식", "급여", "비만", "알레르기"), ("식이", "급여", "영양"), 5.0),
        (("짖", "분리불안", "공격", "배변실수"), ("행동", "훈련", "환경"), 5.0),
        (("접종", "검진", "구충", "치아", "노령"), ("예방", "검진", "수의사"), 5.0),
    )
    for query_terms, chunk_terms, weight in intent_rules:
        if any(term in compact_query for term in query_terms) and any(
            term in compact_chunk for term in chunk_terms
        ):
            boost += weight

    if query_tokens.intersection({"약", "투약", "의약품", "먹여"}) and chunk_tokens.intersection(
        {"약", "투약", "의약품"}
    ):
        boost += 4.5
        if any(term in compact_chunk for term in ("임의로투여", "사람용의약품", "투여하지")):
            boost += 5.0

    if any(term in compact_query for term in ("공식", "법령", "법적근거", "시행규칙")):
        if chunk.source_url:
            boost += 6.0
    if any(term in compact_query for term in ("인허가", "지역별", "공공데이터", "등록업체")):
        if chunk.document_id == "data.local_permits":
            boost += 6.0

    if any(term in compact_query for term in ("탈출", "행방", "도망", "이탈", "사라졌")):
        if chunk.document_id == "internal.04_incident_response":
            boost += 12.0
        elif chunk.document_id.startswith("care."):
            boost -= 5.0

    food_care_query = any(
        term in compact_query
        for term in ("사료", "간식", "급여", "식이", "영양", "설사", "구토", "체중", "비만")
    )
    facility_query = any(
        term in compact_query for term in ("입실", "퇴실", "시설", "호텔", "유치원")
    )
    if food_care_query and not facility_query:
        if chunk.document_id.startswith("care.03_nutrition_weight"):
            boost += 8.0
        elif chunk.document_id.startswith("internal."):
            boost -= 4.0

    return boost


class LocalKeywordRetriever:
    """Hybrid lexical, vector, and character n-gram retriever for pet care knowledge."""

    def __init__(self, chunks: tuple[IndexedChunk, ...] | None = None) -> None:
        self._chunks = chunks or (*load_markdown_chunks(), *load_official_source_chunks())
        self._document_frequency = Counter(
            token for chunk in self._chunks for token in set(chunk.term_counts)
        )

    def _idf(self, term: str) -> float:
        corpus_size = max(len(self._chunks), 1)
        return math.log(1 + corpus_size / (1 + self._document_frequency[term]))

    def _tfidf_cosine(self, query_counts: Counter[str], chunk: IndexedChunk) -> float:
        query_norm = 0.0
        chunk_norm = 0.0
        dot_product = 0.0

        for term, frequency in query_counts.items():
            weight = (1 + math.log(frequency)) * self._idf(term)
            query_norm += weight * weight
            chunk_frequency = chunk.term_counts.get(term, 0)
            if chunk_frequency:
                dot_product += weight * (1 + math.log(chunk_frequency)) * self._idf(term)

        for term, frequency in chunk.term_counts.items():
            weight = (1 + math.log(frequency)) * self._idf(term)
            chunk_norm += weight * weight

        if not query_norm or not chunk_norm:
            return 0.0
        return dot_product / math.sqrt(query_norm * chunk_norm)

    def search(
        self,
        query: str,
        context: SearchContext,
        *,
        limit: int,
    ) -> list[RetrievedChunk]:
        compact_query = re.sub(r"\s+", "", query.lower())
        if any(pattern in compact_query for pattern in ("빈방", "몇개", "실시간예약")):
            return []
        if any(pattern in compact_query for pattern in ("몇mg", "용량", "몇알")):
            return []

        raw_terms = tokenize(query)
        query_terms = expand_concepts(query, raw_terms)
        query_counts = Counter(query_terms)
        query_ngrams = character_ngrams(query)
        if not query_terms and not query_ngrams:
            return []

        scored: list[RetrievedChunk] = []
        for chunk in self._chunks:
            if not set(chunk.acl).intersection(context.allowed_acl):
                continue

            lexical_score = 0.0
            for term in query_terms:
                frequency = chunk.term_counts.get(term, 0)
                if frequency:
                    inverse_document_frequency = self._idf(term)
                    lexical_score += (1 + math.log(frequency)) * inverse_document_frequency

                if term in chunk.title.lower() or term in chunk.locator.lower():
                    lexical_score += 1.8

            ngram_union = query_ngrams | chunk.character_ngrams
            ngram_similarity = (
                len(query_ngrams & chunk.character_ngrams) / len(ngram_union)
                if ngram_union
                else 0.0
            )
            vector_score = self._tfidf_cosine(query_counts, chunk)
            score = (
                lexical_score
                + vector_score * 12.0
                + ngram_similarity * 8.0
                + intent_boost(query, chunk)
            )
            if score < 1.8:
                continue

            scored.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    title=chunk.title,
                    locator=chunk.locator,
                    text=chunk.text,
                    score=round(score, 4),
                    source_url=chunk.source_url,
                )
            )

        return sorted(scored, key=lambda item: item.score, reverse=True)[:limit]
