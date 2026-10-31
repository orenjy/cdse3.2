"""
Firestore에 data_samsung.json 시계열 데이터를 일괄 적재(Seeding)하는 스크립트
"""

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from config import settings


def seed_stock_data():
    json_path = os.path.join(os.path.dirname(__file__), "data_samsung.json")
    if not os.path.exists(json_path):
        print(f"[-] '{json_path}' 파일을 찾을 수 없습니다. collect_stock.py를 먼저 실행하세요.")
        return

    # Firebase 자격 증명 확인
    cred = None
    if settings.FIREBASE_SERVICE_ACCOUNT_JSON:
        cred = credentials.Certificate(json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON))
    elif os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    else:
        print("[-] Firebase 자격 증명을 찾을 수 없습니다.")
        print(f"   -> '{settings.FIREBASE_CREDENTIALS_PATH}' 파일이 있거나, .env에 FIREBASE_SERVICE_ACCOUNT_JSON을 설정해야 합니다.")
        return

    # Firebase 앱 초기화
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    data_ref = db.collection("data")

    # JSON 데이터 읽기
    with open(json_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"\n[시작] 총 {len(records)}개의 레코드를 Firestore 'data' 컬렉션에 업로드합니다...")

    # Firestore Batch 쓰기 (최대 500개 단위)
    batch_size = 400
    total_uploaded = 0

    try:
        for i in range(0, len(records), batch_size):
            chunk = records[i:i + batch_size]
            batch = db.batch()
            for item in chunk:
                doc_ref = data_ref.document()
                batch.set(doc_ref, {
                    "date": item["date"],
                    "value": round(float(item["value"]), 2),
                    "memo": item["memo"]
                })
            batch.commit()
            total_uploaded += len(chunk)
            print(f"   -> {total_uploaded}/{len(records)} 개 업로드 완료")

        print(f"\n[성공] 총 {total_uploaded}개의 데이터가 Firestore에 성공적으로 적재되었습니다.\n")
    except Exception as e:
        print(f"\n[오류] Firestore 업로드 실패: {e}\n")
        raise e


if __name__ == "__main__":
    seed_stock_data()
