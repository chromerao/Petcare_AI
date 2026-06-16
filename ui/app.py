# ruff: noqa: E501

import html
import os
from typing import Any

import httpx
import streamlit as st

API_BASE_URL = os.getenv("DOCQA_API_BASE_URL", "http://localhost:8000")

PET_PROFILES = {
    "Bella": {
        "kind": "강아지",
        "breed": "골든 리트리버",
        "age": "5세",
        "weight": "27kg",
        "note": "위장이 예민하고 긴 산책 후 다리 피로가 가끔 있습니다.",
        "vet": "오크리지 동물병원",
        "status": "관찰 안정",
    },
    "Max": {
        "kind": "고양이",
        "breed": "코리안 숏헤어",
        "age": "12세",
        "weight": "5.1kg",
        "note": "노령묘로 음수량, 배뇨 횟수, 식욕 변화를 주기적으로 관찰합니다.",
        "vet": "동네동물의료센터",
        "status": "노령 케어",
    },
}

TRIAGE_CHIPS = (
    "구토",
    "설사",
    "초콜릿 섭취",
    "분리불안",
    "물을 많이 마심",
    "화장실 문제",
    "시설 입실",
    "탈출 사고",
)

SUGGESTED_QUESTIONS = (
    "강아지가 초콜릿을 조금 먹었는데 어떻게 해야 하나요?",
    "사료를 바꾸고 설사를 하는데 어떤 순서로 확인해야 하나요?",
    "혼자 두면 계속 짖고 문을 긁어요. 분리불안일까요?",
    "노령묘가 물을 많이 마시고 화장실을 자주 가요.",
    "고양이 화장실을 어디에 두면 좋나요?",
    "동물이 시설에서 사라졌을 때 첫 조치는 무엇인가요?",
)

CHIP_QUESTIONS = {
    "구토": "반려동물이 구토를 했을 때 어떤 증상을 기록하고 언제 병원에 가야 하나요?",
    "설사": "반려동물이 설사를 할 때 사료, 간식, 응급 신호를 어떤 순서로 확인해야 하나요?",
    "초콜릿 섭취": "강아지가 초콜릿을 조금 먹었는데 어떻게 해야 하나요?",
    "분리불안": "혼자 두면 계속 짖고 문을 긁어요. 분리불안일까요?",
    "물을 많이 마심": "노령묘가 물을 많이 마시고 화장실을 자주 가요.",
    "화장실 문제": "고양이 화장실을 어디에 두면 좋나요?",
    "시설 입실": "신규 입실 시 현장 직원이 확인해야 할 내부 체크리스트는 무엇인가요?",
    "탈출 사고": "동물이 시설에서 사라졌을 때 첫 조치는 무엇인가요?",
}


st.set_page_config(
    page_title="PetCare AI",
    page_icon="P",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
    :root {
        --surface: #faf9f6;
        --surface-low: #f4f3f1;
        --surface-container: #efeeeb;
        --surface-high: #e3e2e0;
        --primary: #074469;
        --primary-container: #2a5c82;
        --mint: #d9e6da;
        --leaf: #386300;
        --text: #1a1c1a;
        --muted: #41474e;
        --outline: #c1c7cf;
        --error: #ba1a1a;
        --error-soft: #ffdad6;
        --shadow: 0 4px 20px rgba(42, 92, 130, 0.08);
    }
    html, body, [class*="css"] { font-family: Inter, sans-serif; }
    .stApp { background: var(--surface); color: var(--text); }
    .block-container { max-width: 1200px; padding-top: 1.5rem; padding-bottom: 3rem; }
    [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid var(--outline); }
    [data-testid="stSidebar"] * { color: var(--text); }
    h1, h2, h3 { font-family: "Plus Jakarta Sans", Inter, sans-serif; letter-spacing: -0.01em; }
    .brand-row { display: flex; align-items: center; gap: 10px; margin-bottom: 18px; }
    .brand-mark { width: 38px; height: 38px; border-radius: 999px; display: grid; place-items: center; background: var(--mint); color: var(--primary); font-weight: 900; }
    .brand-name { font: 800 1.35rem "Plus Jakarta Sans"; color: var(--primary); }
    .hero {
        background: radial-gradient(circle at 80% 20%, rgba(217,230,218,.95), transparent 32%),
            linear-gradient(135deg, #ffffff 0%, #faf9f6 48%, #e8f0e8 100%);
        border: 1px solid var(--outline);
        border-radius: 24px;
        padding: 34px;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
        min-height: 292px;
    }
    .kicker { display: inline-flex; align-items: center; gap: 8px; background: var(--mint); color: var(--primary); border-radius: 999px; padding: 8px 12px; font-size: .78rem; font-weight: 800; letter-spacing: .02em; }
    .hero h1 { color: var(--primary); font-size: clamp(2.1rem, 5vw, 3.4rem); line-height: 1.04; margin: 18px 0 14px; max-width: 720px; }
    .hero p { color: var(--muted); font-size: 1.05rem; line-height: 1.7; max-width: 720px; }
    .hero-actions { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 22px; }
    .soft-card, .metric-card, .pet-card, .source-card, .history-card {
        background: #ffffff;
        border: 1px solid var(--outline);
        border-radius: 20px;
        box-shadow: var(--shadow);
    }
    .metric-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 18px 0 22px; }
    .metric-card { padding: 18px; }
    .metric-label { font-size: .74rem; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); font-weight: 800; }
    .metric-value { color: var(--primary); font: 800 1.4rem "Plus Jakarta Sans"; margin-top: 6px; }
    .pet-card { padding: 20px; border-top: 3px solid var(--primary); }
    .pet-avatar { width: 82px; height: 82px; border-radius: 999px; display: grid; place-items: center; background: var(--mint); color: var(--primary); font: 800 1.8rem "Plus Jakarta Sans"; margin-bottom: 12px; }
    .pet-title { color: var(--primary); font: 800 1.45rem "Plus Jakarta Sans"; }
    .pet-meta { color: var(--muted); line-height: 1.7; margin-top: 8px; }
    .alert-card { background: var(--error-soft); color: #93000a; border: 1px solid #ffb4ab; border-radius: 16px; padding: 14px 16px; display: flex; gap: 10px; align-items: flex-start; font-weight: 600; }
    .section-title { display: flex; align-items: center; justify-content: space-between; margin: 28px 0 12px; }
    .section-title h2 { color: var(--primary); margin: 0; font-size: 1.5rem; }
    .chip-wrap { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
    .chip { border: 1px solid var(--primary); color: var(--primary); border-radius: 999px; padding: 8px 12px; background: #ffffff; font-size: .88rem; font-weight: 700; }
    .progress { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 10px 0 18px; }
    .progress span { height: 6px; border-radius: 999px; background: var(--mint); }
    .progress .done { background: var(--primary); }
    .source-card { border-left: 4px solid var(--primary); padding: 14px 16px; margin: 9px 0; }
    .source-card strong { color: var(--primary); }
    .source-meta { color: var(--muted); font-size: .82rem; margin: 4px 0 7px; }
    .source-snippet { color: #38483e; font-size: .9rem; line-height: 1.55; }
    .confidence { display: inline-block; background: var(--mint); color: var(--primary); padding: 6px 10px; border-radius: 999px; font-size: .78rem; font-weight: 800; margin-top: 8px; }
    .mode-ai { background: #fff4d7; color: #7a5415; }
    .mode-safety { background: var(--error-soft); color: #93000a; }
    .notice { background: #fff7df; border: 1px solid #efd589; border-radius: 14px; padding: 12px 14px; color: #5b4316; margin-top: 10px; }
    .history-card { padding: 14px; margin-bottom: 10px; }
    .history-card strong { color: var(--primary); }
    .history-card p { color: var(--muted); margin: 5px 0 0; font-size: .88rem; }
    .stButton > button { border-radius: 16px; font-weight: 800; border-color: var(--outline); min-height: 42px; }
    .stButton > button[kind="primary"] { background: var(--primary); border-color: var(--primary); color: white; }
    [data-testid="stChatMessage"] { background: #ffffff; border: 1px solid var(--outline); border-radius: 20px; padding: 10px; box-shadow: var(--shadow); }
    textarea { border-radius: 14px !important; }
    @media (max-width: 900px) { .metric-grid { grid-template-columns: 1fr 1fr; } }
    @media (max-width: 640px) { .metric-grid { grid-template-columns: 1fr; } .hero { padding: 24px; } }
    </style>
    """,
    unsafe_allow_html=True,
)


if "messages" not in st.session_state:
    st.session_state.messages = []
if "suggested_question" not in st.session_state:
    st.session_state.suggested_question = ""
if "selected_pet" not in st.session_state:
    st.session_state.selected_pet = "Bella"


def get_api_status() -> tuple[bool, int]:
    try:
        health = httpx.get(f"{API_BASE_URL}/api/v1/health", timeout=2.0)
        health.raise_for_status()
        sources = httpx.get(f"{API_BASE_URL}/api/v1/sources", timeout=2.0)
        sources.raise_for_status()
    except httpx.HTTPError:
        return False, 0
    payload = sources.json()
    return True, len(payload.get("sources", []))


def ask_api(question: str, use_openai: bool) -> dict[str, Any]:
    response = httpx.post(
        f"{API_BASE_URL}/api/v1/query",
        json={
            "question": question,
            "generation_mode": "openai" if use_openai else "local",
        },
        timeout=40.0,
    )
    response.raise_for_status()
    return response.json()


def pet_contextualize(question: str, pet_name: str) -> str:
    pet = PET_PROFILES[pet_name]
    return f"{question}\n\n상담 대상은 {pet['age']} {pet['kind']}입니다."


def render_citations(citations: list[dict[str, object]]) -> None:
    for index, citation in enumerate(citations, start=1):
        title = html.escape(str(citation["title"]))
        locator = html.escape(str(citation["locator"]))
        snippet = html.escape(str(citation.get("snippet") or ""))
        score = float(citation.get("score") or 0)
        source_url = citation.get("source_url")
        title_html = (
            f'<a href="{html.escape(str(source_url))}" target="_blank">{title}</a>'
            if source_url
            else title
        )
        st.markdown(
            f"""
            <div class="source-card">
                <strong>{index}. {title_html}</strong>
                <div class="source-meta">{locator} · 검색 점수 {score:.2f}</div>
                <div class="source-snippet">{snippet}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_answer_meta(message: dict[str, object]) -> None:
    confidence = round(float(message.get("confidence") or 0) * 100)
    mode = str(message.get("mode", "local"))
    answer_type = str(message.get("answer_type", "document_grounded"))
    mode_class = " mode-ai" if answer_type == "ai_general" else ""
    if answer_type == "safety":
        mode_class = " mode-safety"
    st.markdown(
        f'<span class="confidence{mode_class}">신뢰도 {confidence}% · {mode} · {answer_type}</span>',
        unsafe_allow_html=True,
    )
    if message.get("safety_notice"):
        st.markdown(
            f'<div class="notice">{html.escape(str(message["safety_notice"]))}</div>',
            unsafe_allow_html=True,
        )


def render_pet_profile(pet_name: str) -> None:
    pet = PET_PROFILES[pet_name]
    st.markdown(
        f"""
        <div class="pet-card">
            <div class="pet-avatar">{html.escape(pet_name[0])}</div>
            <div class="pet-title">{html.escape(pet_name)}</div>
            <div class="pet-meta">
                {html.escape(pet["kind"])} · {html.escape(pet["breed"])} · {html.escape(pet["age"])} · {html.escape(pet["weight"])}<br/>
                상태: <strong>{html.escape(pet["status"])}</strong><br/>
                전담 동물병원: {html.escape(pet["vet"])}<br/>
                {html.escape(pet["note"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def assistant_messages() -> list[dict[str, object]]:
    return [message for message in st.session_state.messages if message["role"] == "assistant"]


api_ready, source_count = get_api_status()
answer_count = len(assistant_messages())
grounded_count = sum(
    1
    for message in assistant_messages()
    if message.get("answer_type") == "document_grounded" and message.get("citations")
)

with st.sidebar:
    st.markdown(
        """
        <div class="brand-row">
            <div class="brand-mark">P</div>
            <div class="brand-name">PetCare AI</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Empathetic Professionalism · 보호자 케어 + 시설 운영")
    st.divider()
    selected_pet = st.selectbox(
        "상담할 반려동물",
        options=list(PET_PROFILES),
        index=list(PET_PROFILES).index(st.session_state.selected_pet),
    )
    st.session_state.selected_pet = selected_pet
    use_pet_context = st.toggle("프로필을 질문에 반영", value=True)
    use_openai = st.toggle(
        "AI 일반 조언 허용",
        value=False,
        help="끄면 문서 근거만 사용합니다. 켜면 문서에 없는 질문도 gpt-4.1-mini가 일반 조언으로 답합니다.",
    )
    st.markdown(f"**API 상태**  {'정상' if api_ready else '연결 필요'}")
    st.markdown(f"**출처 카탈로그**  {source_count}개")
    st.markdown(f"**답변 모드**  {'문서 + AI 일반 조언' if use_openai else '문서 근거 전용'}")
    st.divider()
    st.markdown("#### 응급 경계")
    st.caption(
        "호흡곤란, 발작, 의식 저하, 독성 섭취, 반복 구토/설사, 심한 통증은 온라인 답변을 기다리지 말고 동물병원에 연락하세요."
    )
    if st.button("응급 상담 체크리스트", use_container_width=True, type="primary"):
        st.session_state.suggested_question = "응급 신호가 보일 때 보호자가 즉시 확인하고 병원에 전달해야 할 정보는 무엇인가요?"
    if st.button("병원 방문 준비 가이드", use_container_width=True):
        st.session_state.suggested_question = "동물병원에 가기 전 보호자가 기록하고 준비해야 할 정보는 무엇인가요?"
    if st.button("대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

left, right = st.columns([1.9, 1], gap="large")
with left:
    st.markdown(
        """
        <section class="hero">
            <span class="kicker">AI 기반 반려동물 케어 상담</span>
            <h1>아이들이 말하지 못하는 신호를, 근거와 함께 읽어드립니다.</h1>
            <p>문서 기반 검색, 공식 출처 인용, AI 일반 조언 fallback을 하나의 상담 흐름으로 연결했습니다. 응급과 투약 경계는 더 엄격하게, 보호자에게는 더 차분하게 안내합니다.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    hero_a, hero_b = st.columns(2)
    with hero_a:
        if st.button("상담 시작하기", type="primary", use_container_width=True):
            st.session_state.suggested_question = "우리 반려동물 상태를 설명하면 어떤 순서로 확인하면 좋을까요?"
    with hero_b:
        if st.button("시설 운영 규정 묻기", use_container_width=True):
            st.session_state.suggested_question = "동물위탁관리업 시설 및 인력 기준의 공식 근거 문서는 무엇인가요?"

with right:
    render_pet_profile(st.session_state.selected_pet)

st.markdown(
    f"""
    <div class="metric-grid">
        <div class="metric-card"><div class="metric-label">System</div><div class="metric-value">{"Online" if api_ready else "Offline"}</div></div>
        <div class="metric-card"><div class="metric-label">Knowledge Sources</div><div class="metric-value">{source_count}</div></div>
        <div class="metric-card"><div class="metric-label">Consultations</div><div class="metric-value">{answer_count}</div></div>
        <div class="metric-card"><div class="metric-label">Grounded Answers</div><div class="metric-value">{grounded_count}</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="alert-card">
        <span>긴급</span>
        <div>호흡곤란, 의식 저하, 발작, 독성 물질 섭취 의심은 즉시 동물병원 또는 응급병원 상담이 우선입니다.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

chat_col, history_col = st.columns([2.1, 1], gap="large")

with chat_col:
    st.markdown('<div class="section-title"><h2>AI 트리아지 상담</h2></div>', unsafe_allow_html=True)
    progress_done = min(3, max(1, answer_count + 1))
    st.markdown(
        "<div class='progress'>"
        + "".join("<span class='done'></span>" if index < progress_done else "<span></span>" for index in range(3))
        + "</div>",
        unsafe_allow_html=True,
    )

    st.markdown("#### 증상/상황 칩")
    chip_columns = st.columns(4)
    for index, chip in enumerate(TRIAGE_CHIPS):
        with chip_columns[index % 4]:
            if st.button(chip, key=f"chip-{chip}", use_container_width=True):
                st.session_state.suggested_question = CHIP_QUESTIONS[chip]

    st.markdown("#### 빠른 질문")
    question_columns = st.columns(2)
    for index, suggested in enumerate(SUGGESTED_QUESTIONS):
        with question_columns[index % 2]:
            if st.button(suggested, key=f"suggestion-{index}", use_container_width=True):
                st.session_state.suggested_question = suggested

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                render_answer_meta(message)
            if message.get("citations"):
                with st.expander(f"근거 문서 {len(message['citations'])}개", expanded=True):
                    render_citations(message["citations"])

    prompt = st.chat_input("메시지를 입력하세요...", disabled=not api_ready)
    if st.session_state.suggested_question:
        prompt = st.session_state.suggested_question
        st.session_state.suggested_question = ""

    if prompt:
        display_prompt = prompt
        api_prompt = pet_contextualize(prompt, st.session_state.selected_pet) if use_pet_context else prompt
        st.session_state.messages.append({"role": "user", "content": display_prompt})
        with st.chat_message("user"):
            st.markdown(display_prompt)

        with st.chat_message("assistant"):
            with st.spinner("케어 문서와 공식 출처를 검색하고 있습니다..."):
                try:
                    result = ask_api(api_prompt, use_openai)
                except httpx.HTTPStatusError as exc:
                    try:
                        detail = exc.response.json().get("detail", {})
                    except ValueError:
                        detail = {}
                    answer = detail.get("message", "질의 처리 중 오류가 발생했습니다.")
                    st.error(answer)
                except httpx.HTTPError:
                    answer = "API 연결이 끊겼습니다. 실행 터미널을 확인해 주세요."
                    st.error(answer)
                else:
                    answer = str(result["answer"])
                    citations = list(result["citations"])
                    message = {
                        "role": "assistant",
                        "content": answer,
                        "confidence": result.get("retrieval_confidence", 0.0),
                        "mode": result.get("generation_mode", "local"),
                        "answer_type": result.get("answer_type", "document_grounded"),
                        "safety_notice": result.get("safety_notice"),
                        "citations": citations,
                    }
                    st.markdown(answer)
                    render_answer_meta(message)
                    if citations:
                        with st.expander(f"근거 문서 {len(citations)}개", expanded=True):
                            render_citations(citations)
                    elif result.get("answer_type") == "no_evidence":
                        st.warning("문서 근거가 없습니다. AI 일반 조언을 허용하면 제한된 범위에서 답변할 수 있습니다.")

                    st.session_state.messages.append(message)

with history_col:
    st.markdown('<div class="section-title"><h2>최근 상담 기록</h2></div>', unsafe_allow_html=True)
    recent = assistant_messages()[-4:][::-1]
    if not recent:
        st.info("아직 상담 이력이 없습니다. 증상 칩이나 빠른 질문으로 시작해보세요.")
    for index, message in enumerate(recent, start=1):
        content = str(message["content"])
        preview = content[:110] + ("..." if len(content) > 110 else "")
        st.markdown(
            f"""
            <div class="history-card">
                <strong>상담 {index} · {html.escape(str(message.get("answer_type", "document_grounded")))}</strong>
                <p>{html.escape(preview)}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-title"><h2>기능 연결 현황</h2></div>', unsafe_allow_html=True)
    st.markdown(
        """
        - AI 상담 어시스턴트: API `/query` 연결
        - 건강 기록 관리: 세션 프로필/상담 이력으로 데모 구현
        - 진료 예약하기: 병원 방문 준비 가이드로 대체 연결
        - 이미지 업로드: 현재 백엔드 미지원, 상담 문진 중심으로 제한
        """
    )
