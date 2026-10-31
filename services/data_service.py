from typing import List, Dict, Any, Optional
import firebase_db
from schemas import DataSummary, SummaryMetrics, DataCreate, DataUpdate, DataResponse


def fetch_all_data() -> List[Dict[str, Any]]:
    """모든 데이터 조회 (날짜 오름차순 정렬)"""
    return firebase_db.get_all_data_records()


def create_data(data: DataCreate) -> Dict[str, Any]:
    """새 데이터 등록"""
    return firebase_db.add_data_record(
        date=data.date,
        value=data.value,
        memo=data.memo
    )


def update_data(record_id: str, data: DataUpdate) -> Optional[Dict[str, Any]]:
    """기존 데이터 수정"""
    return firebase_db.update_data_record(
        record_id=record_id,
        update_fields=data.model_dump(exclude_unset=True)
    )


def delete_data(record_id: str) -> bool:
    """데이터 삭제"""
    return firebase_db.delete_data_record(record_id)


def compute_summary() -> DataSummary:
    """
    현재 저장된 시계열 데이터를 분석하여 요약 통계(기간, 개수, 주요 지표, 트렌드)를 생성합니다.
    """
    records = fetch_all_data()

    if not records:
        return DataSummary(
            period="데이터 없음",
            count=0,
            metrics=SummaryMetrics(total=0.0, average=0.0, max=0.0, min=0.0),
            trend="데이터 없음"
        )

    # 날짜 정렬 확인
    records.sort(key=lambda x: x.get("date", ""))

    first_date = records[0].get("date", "")
    last_date = records[-1].get("date", "")
    period = f"{first_date} ~ {last_date}"
    count = len(records)

    values = [float(r.get("value", 0.0)) for r in records]
    total_val = round(sum(values), 2)
    avg_val = round(total_val / count, 2)
    max_val = round(max(values), 2)
    min_val = round(min(values), 2)

    # 최근 추세(Trend) 계산
    # 최근 30개(약 1.5개월) 또는 전체 데이터 기준 변화율 산출
    window = min(30, count)
    recent_records = records[-window:]
    start_recent = float(recent_records[0].get("value", 0.0))
    end_recent = float(recent_records[-1].get("value", 0.0))

    if start_recent > 0:
        change_pct = round(((end_recent - start_recent) / start_recent) * 100, 2)
        if change_pct > 1.0:
            trend = f"상승 (최근 {window}거래일 대비 +{change_pct}%)"
        elif change_pct < -1.0:
            trend = f"하락 (최근 {window}거래일 대비 {change_pct}%)"
        else:
            trend = f"보합 유지 (최근 {window}거래일 변동폭 {change_pct}%)"
    else:
        trend = "변동성 미미"

    return DataSummary(
        period=period,
        count=count,
        metrics=SummaryMetrics(
            total=total_val,
            average=avg_val,
            max=max_val,
            min=min_val
        ),
        trend=trend
    )
