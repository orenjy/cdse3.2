from typing import List
from fastapi import APIRouter, HTTPException, status
from schemas import DataCreate, DataUpdate, DataResponse, DataSummary
from services.data_service import fetch_all_data, create_data, update_data, delete_data, compute_summary

router = APIRouter(prefix="/api/data", tags=["Data"])


@router.get("/summary", response_model=DataSummary, summary="데이터 요약 정보 조회")
def get_data_summary():
    """
    저장된 시계열 데이터의 기간, 총 개수, 핵심 통계 지표, 최근 추세를 요약하여 반환합니다.
    (AI 시스템 프롬프트 주입 및 대시보드 표시용)
    """
    return compute_summary()


@router.post("", response_model=DataResponse, status_code=status.HTTP_201_CREATED, summary="새 데이터 추가")
def add_data(item: DataCreate):
    """(date, value, memo) 형식의 새 시계열 데이터를 추가합니다."""
    record = create_data(item)
    return record


@router.get("", response_model=List[DataResponse], summary="데이터 목록 조회")
def get_data_list():
    """저장된 모든 시계열 데이터를 날짜순으로 조회합니다."""
    return fetch_all_data()


@router.put("/{id}", response_model=DataResponse, summary="데이터 수정")
def modify_data(id: str, item: DataUpdate):
    """ID에 해당하는 데이터를 부분 또는 전체 수정합니다."""
    updated = update_data(id, item)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID가 '{id}'인 데이터를 찾을 수 없습니다.")
    return updated


@router.delete("/{id}", status_code=status.HTTP_200_OK, summary="데이터 삭제")
def remove_data(id: str):
    """ID에 해당하는 데이터를 삭제합니다."""
    success = delete_data(id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"ID가 '{id}'인 데이터를 찾을 수 없습니다.")
    return {"message": "데이터가 성공적으로 삭제되었습니다.", "id": id}
