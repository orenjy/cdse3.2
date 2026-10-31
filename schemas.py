from typing import Optional, List
from pydantic import BaseModel, Field


# ==========================================
# 1. 시계열 데이터 스키마
# ==========================================

class DataCreate(BaseModel):
    date: str = Field(..., description="날짜 문자열 (YYYY-MM-DD)", example="2026-10-30")
    value: float = Field(..., description="수치 데이터 (종가)", example=70000.0)
    memo: str = Field(..., description="데이터 메모", example="삼성전자 종가")


class DataUpdate(BaseModel):
    date: Optional[str] = Field(None, description="수정할 날짜 (YYYY-MM-DD)")
    value: Optional[float] = Field(None, description="수정할 수치")
    memo: Optional[str] = Field(None, description="수정할 메모")


class DataResponse(BaseModel):
    id: str = Field(..., description="문서 고유 ID")
    date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    value: float = Field(..., description="수치")
    memo: str = Field(..., description="메모")


# ==========================================
# 2. 데이터 요약 통계 스키마
# ==========================================

class SummaryMetrics(BaseModel):
    total: float = Field(..., description="전체 합계")
    average: float = Field(..., description="평균값")
    max: float = Field(..., description="최댓값")
    min: float = Field(..., description="최솟값")


class DataSummary(BaseModel):
    period: str = Field(..., description="데이터 기간 (시작 ~ 종료)")
    count: int = Field(..., description="총 데이터 개수")
    metrics: SummaryMetrics = Field(..., description="기본 통계 지표")
    trend: str = Field(..., description="최근 추세 분석")


# ==========================================
# 3. 대화 및 챗봇 스키마
# ==========================================

class ChatMessage(BaseModel):
    role: str = Field(..., description="역할: 'user' 또는 'assistant' 또는 'system'")
    content: str = Field(..., description="메시지 내용")


class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 질문 (자연어)")
    conversation_id: Optional[str] = Field(None, description="이전 대화 ID (선택)")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="AI 비서의 답변")
    conversation_id: str = Field(..., description="대화 세션 ID")
    summary: Optional[DataSummary] = Field(None, description="답변에 반영된 데이터 요약")


class ConversationCreate(BaseModel):
    title: str = Field(..., description="대화 제목")
    messages: List[ChatMessage] = Field(default_factory=list, description="대화 메시지 목록")


class ConversationResponse(BaseModel):
    id: str = Field(..., description="대화 ID")
    title: str = Field(..., description="대화 제목")
    created_at: str = Field(..., description="생성 일시")
    messages: Optional[List[ChatMessage]] = Field(None, description="대화 메시지 목록")
