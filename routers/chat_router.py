from fastapi import APIRouter
from schemas import ChatRequest, ChatResponse
from services.chat_service import process_chat

router = APIRouter(prefix="/api/chat", tags=["AI Chat"])


@router.post("", response_model=ChatResponse, summary="AI 대화 (데이터 컨텍스트 주입)")
def chat_with_ai(request: ChatRequest):
    """
    1. 데이터 요약(/api/data/summary)을 시스템 프롬프트에 주입
    2. OpenAI GPT 모델을 호출하여 질문에 답변
    3. 대화 내용을 conversations 컬렉션에 자동 저장
    """
    return process_chat(
        message=request.message,
        conversation_id=request.conversation_id
    )
