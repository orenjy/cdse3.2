import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from main import app
import firebase_db

# 로컬 테스트 초기화
firebase_db.init_firebase()

def run_tests():
    print("\n================== API 테스트 시작 ==================")
    with TestClient(app) as client:
        # 1. 헬스체크
        res = client.get("/api/health")
        print(f"1. Health Check: {res.status_code} -> {res.json()}")
        assert res.status_code == 200
        assert "gemini_configured" in res.json()

        # 2. 데이터 요약
        res = client.get("/api/data/summary")
        summary = res.json()
        print(f"2. Data Summary: {res.status_code} -> count={summary.get('count')}, period={summary.get('period')}, trend={summary.get('trend')}")
        assert res.status_code == 200
        assert summary.get("count") > 0

        # 3. 데이터 목록 조회
        res = client.get("/api/data")
        records = res.json()
        print(f"3. Data List: {res.status_code} -> {len(records)}개 조회됨")
        assert res.status_code == 200
        assert len(records) > 0

        # 4. 데이터 추가 (POST)
        new_data = {
            "date": "2026-11-01",
            "value": 85000.0,
            "memo": "테스트 추가 종가"
        }
        res = client.post("/api/data", json=new_data)
        print(f"4. Add Data: {res.status_code} -> id={res.json().get('id')}")
        assert res.status_code == 201
        created_id = res.json()["id"]

        # 5. 데이터 수정 (PUT)
        update_data = {
            "value": 86000.0,
            "memo": "수정된 테스트 종가"
        }
        res = client.put(f"/api/data/{created_id}", json=update_data)
        print(f"5. Update Data: {res.status_code} -> value={res.json().get('value')}")
        assert res.status_code == 200
        assert res.json()["value"] == 86000.0

        # 6. 데이터 삭제 (DELETE)
        res = client.delete(f"/api/data/{created_id}")
        print(f"6. Delete Data: {res.status_code} -> {res.json().get('message')}")
        assert res.status_code == 200

        # 7. AI 대화 (POST /api/chat)
        chat_payload = {
            "message": "현재 주가 데이터의 평균과 최고가를 알려줘."
        }
        res = client.post("/api/chat", json=chat_payload)
        print(f"7. Chat API: {res.status_code}")
        chat_res = res.json()
        assert res.status_code == 200
        conv_id = chat_res.get("conversation_id")
        print(f"   Conversation ID: {conv_id}")

        # 8. 대화 목록 조회
        res = client.get("/api/conversations")
        print(f"8. Conversation List: {res.status_code} -> {len(res.json())}개 대화 존재")
        assert res.status_code == 200

        # 9. 대화 상세 조회 (대화 불러오기)
        res = client.get(f"/api/conversations/{conv_id}")
        print(f"9. Conversation Detail: {res.status_code} -> messages 수={len(res.json().get('messages', []))}")
        assert res.status_code == 200
        assert len(res.json().get("messages", [])) >= 2

        # 10. 대화 삭제
        res = client.delete(f"/api/conversations/{conv_id}")
        print(f"10. Delete Conversation: {res.status_code} -> {res.json().get('message')}")
        assert res.status_code == 200

        # 11. 정적 프론트엔드 서빙 확인
        res = client.get("/")
        print(f"11. Frontend Index: {res.status_code} -> Content length={len(res.text)}")
        assert res.status_code == 200
        assert "FinAssistant" in res.text

    print("\n================== 모든 테스트 완벽 통과! ==================\n")

if __name__ == "__main__":
    run_tests()
