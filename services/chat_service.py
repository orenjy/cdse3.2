import uuid
from typing import Optional, Dict, Any, List
from google import genai
from google.genai import types

from config import settings
import firebase_db
from services.data_service import compute_summary
from schemas import ChatResponse, DataSummary


def _build_system_prompt(summary: DataSummary) -> str:
    """
    데이터 요약을 시스템 프롬프트(system_instruction)에 주입합니다.
    """
    metrics_str = f"합계: {summary.metrics.total:,.2f}, 평균: {summary.metrics.average:,.2f}, 최고가: {summary.metrics.max:,.2f}, 최저가: {summary.metrics.min:,.2f}"

    prompt = f"""당신은 사용자의 금융/주식 데이터를 깊이 있게 분석하고 친절히 설명하는 전문 AI 데이터 비서입니다.

[사용자 데이터 요약]
- 데이터 기간: {summary.period}
- 총 레코드: {summary.count}개
- 주요 지표: {metrics_str}
- 최근 트렌드: {summary.trend}

위 데이터를 기반으로 사용자의 질문에 전문적이고 친절한 맞춤형 답변을 한국어로 제공하세요.
데이터와 관련된 수치(평균, 최고가, 최저가 등)를 질문받으면 위 요약 정보를 인용하여 정확하게 답변하세요."""
    return prompt


def process_chat(message: str, conversation_id: Optional[str] = None) -> ChatResponse:
    """
    1. 데이터 요약 조회
    2. 요약을 시스템 인스트럭션에 주입 (컨텍스트 주입)
    3. 이전 대화 기록 로드 및 Google Gemini API 호출
    4. 대화 내용을 conversations 컬렉션에 자동 저장
    """
    # 1. 요약 정보 계산
    summary = compute_summary()
    system_prompt = _build_system_prompt(summary)

    cid = conversation_id or str(uuid.uuid4())

    # 2. 기존 대화 기록 가져오기
    existing_conv = firebase_db.get_conversation_by_id(cid)
    history_messages: List[Dict[str, str]] = []
    if existing_conv and "messages" in existing_conv:
        history_messages = existing_conv["messages"]

    reply_content = ""

    # 3. Gemini API 호출
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
        try:
            client = genai.Client(api_key=settings.GEMINI_API_KEY)

            # 멀티턴 대화 컨텐츠 구성
            contents = []
            for msg in history_messages[-10:]:
                # Gemini에서는 assistant 역할을 'model'로 매핑
                role = "user" if msg.get("role") == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg.get("content", ""))]
                ))
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=message)]
            ))

            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
                max_output_tokens=1000
            )

            # 시도할 모델 우선순위 리스트 (현재 설정 모델 우선, 실패 시 fallback)
            candidate_models = [settings.GEMINI_MODEL, "gemini-3.5-flash", "gemini-3.8-flash", "gemini-flash-latest"]
            # 중복 제거
            models_to_try = []
            for m in candidate_models:
                if m not in models_to_try:
                    models_to_try.append(m)

            last_err = None
            for model_name in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=config
                    )
                    reply_content = response.text or ""
                    if reply_content:
                        break
                except Exception as err:
                    last_err = err
                    continue

            if not reply_content and last_err:
                reply_content = f"⚠️ [Gemini API 오류]: {str(last_err)}\n\n(참고: Gemini API 키 및 Google AI Studio 할당량을 확인해주세요.)"
        except Exception as e:
            reply_content = f"⚠️ [Gemini API 오류]: {str(e)}"
    else:
        # API 키가 아직 없을 때 사용자에게 안내하는 로컬 스마트 요약 답변
        reply_content = (
            f"안녕하세요! 현재 Gemini API 키가 설정되지 않아 로컬 요약 데이터를 직접 안내해 드립니다.\n\n"
            f"📊 **데이터 분석 요약**\n"
            f"- **데이터 기간**: {summary.period}\n"
            f"- **총 데이터 수**: {summary.count}개\n"
            f"- **평균 종가**: {summary.metrics.average:,.2f}원\n"
            f"- **최고가**: {summary.metrics.max:,.2f}원 / **최저가**: {summary.metrics.min:,.2f}원\n"
            f"- **최근 추세**: {summary.trend}\n\n"
            f"💡 `.env` 파일에 `GEMINI_API_KEY=AIzaSy...`를 설정하시면 Gemini AI와의 실시간 맞춤 대화가 활성화됩니다."
        )

    # 4. 대화 내용 자동 저장
    new_exchanges = [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reply_content}
    ]
    title_snippet = message[:25] + ("..." if len(message) > 25 else "")
    firebase_db.append_message_to_conversation(
        conversation_id=cid,
        new_messages=new_exchanges,
        title=title_snippet
    )

    return ChatResponse(
        reply=reply_content,
        conversation_id=cid,
        summary=summary
    )
