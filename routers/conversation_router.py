from typing import List
from fastapi import APIRouter, HTTPException, status
import firebase_db
from schemas import ConversationCreate, ConversationResponse

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED, summary="대화 저장")
def save_conversation(conv: ConversationCreate):
    """대화 내용을 저장합니다."""
    messages_dict = [m.model_dump() for m in conv.messages]
    result = firebase_db.create_conversation(title=conv.title, messages=messages_dict)
    return result


@router.get("", response_model=List[ConversationResponse], summary="대화 목록 조회")
def list_conversations():
    """저장된 모든 대화 목록을 최신순으로 조회합니다."""
    return firebase_db.get_all_conversations()


@router.get("/{id}", response_model=ConversationResponse, summary="특정 대화 전체 조회 (대화 불러오기)")
def get_conversation_detail(id: str):
    """특정 대화의 전체 메시지(messages) 목록을 상세 조회합니다."""
    conv = firebase_db.get_conversation_by_id(id)
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"대화 ID '{id}'를 찾을 수 없습니다.")
    return conv


@router.delete("/{id}", status_code=status.HTTP_200_OK, summary="대화 삭제")
def delete_conversation(id: str):
    """지정된 대화를 삭제합니다."""
    success = firebase_db.delete_conversation_by_id(id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"대화 ID '{id}'를 찾을 수 없습니다.")
    return {"message": "대화가 성공적으로 삭제되었습니다.", "id": id}
