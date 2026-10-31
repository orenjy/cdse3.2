import json
import warnings
import pandas as pd
import yfinance as yf

# yfinance 내부 라이브러리 경고 메시지 무시
warnings.filterwarnings("ignore")


def fetch_stock_data(ticker_symbol: str, min_count: int = 100) -> pd.DataFrame:
    """
    yfinance를 사용해 지정된 종목의 시계열 주가 데이터를 수집합니다.
    
    기본적으로 최근 1년(period="1y") 데이터를 조회하며,
    수집된 데이터 개수가 min_count(기본 100개) 미만인 경우 최근 2년(period="2y")으로 조회 기간을 늘립니다.
    수정 종가를 반영하기 위해 auto_adjust=True 옵션을 사용합니다.

    Args:
        ticker_symbol (str): 야후 파이낸스 티커 심볼 (예: '005930.KS', 'AAPL')
        min_count (int): 최소 필요 데이터 개수 (기본값: 100)

    Returns:
        pd.DataFrame: 수집된 주가 데이터프레임
    """
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="1y", auto_adjust=True)

    if len(df) < min_count:
        print(f"[{ticker_symbol}] 1년 데이터 개수({len(df)}개)가 {min_count}개 미만이므로 2년치 데이터를 수집합니다.")
        df = ticker.history(period="2y", auto_adjust=True)

    return df


def transform_stock_data(df: pd.DataFrame, memo: str) -> list[dict]:
    """
    수집된 주가 DataFrame을 지정된 JSON 포맷의 딕셔너리 리스트로 변환합니다.

    각 데이터는 다음 구조를 갖습니다:
    {
      "date": "YYYY-MM-DD",
      "value": 70000.0,
      "memo": memo
    }

    Args:
        df (pd.DataFrame): yfinance에서 반환된 주가 데이터프레임
        memo (str): 각 데이터 레코드에 부여할 메모 문자열 (예: '삼성전자 종가')

    Returns:
        list[dict]: 변환된 데이터 딕셔너리 리스트
    """
    result = []
    for date, row in df.iterrows():
        date_str = date.strftime("%Y-%m-%d")
        close_val = round(float(row["Close"]), 2)
        result.append({
            "date": date_str,
            "value": close_val,
            "memo": memo
        })
    return result


def save_to_json(data: list[dict], filepath: str) -> None:
    """
    변환된 주가 데이터 리스트를 JSON 파일로 저장합니다.
    한글 깨짐 방지를 위해 UTF-8 인코딩 및 ensure_ascii=False를 적용합니다.

    Args:
        data (list[dict]): 저장할 데이터 리스트
        filepath (str): 저장할 파일 경로
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def collect_and_save_stock(ticker_symbol: str, memo: str, output_path: str) -> int:
    """
    주가 데이터 수집, 변환, JSON 저장을 일괄 수행하고 수집된 데이터 개수를 출력합니다.

    Args:
        ticker_symbol (str): 티커 심볼
        memo (str): 메모 내용
        output_path (str): 출력 JSON 파일 경로

    Returns:
        int: 수집 및 저장된 데이터 개수
    """
    print(f"\n>>> [{ticker_symbol}] 데이터 수집 시작...")
    df = fetch_stock_data(ticker_symbol)
    data = transform_stock_data(df, memo)
    save_to_json(data, output_path)

    count = len(data)
    print(f"[{ticker_symbol}] 수집된 데이터 개수: {count}개")
    print(f"[{ticker_symbol}] 파일 저장 완료: {output_path}")
    return count


if __name__ == "__main__":
    # 1. 삼성전자(005930.KS) 데이터 수집 및 저장
    collect_and_save_stock(
        ticker_symbol="005930.KS",
        memo="삼성전자 종가",
        output_path="data_samsung.json"
    )

    # 2. (선택) 애플(AAPL) 데이터 수집 예시 - 필요 시 주석 해제하여 실행 가능
    # collect_and_save_stock(
    #     ticker_symbol="AAPL",
    #     memo="애플 종가",
    #     output_path="data_aapl.json"
    # )
