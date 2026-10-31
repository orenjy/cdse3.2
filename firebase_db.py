import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

import firebase_admin
from firebase_admin import credentials, firestore
from config import settings

_db_instance = None
_is_firebase_connected = False

# 로컬 폴백 저장소 (Firebase 키 미설정 시 개발/테스트용)
_local_data_store: Dict[str, Dict[str, Any]] = {}
_local_conversations_store: Dict[str, Dict[str, Any]] = {}


def init_firebase():
    """
    Firebase Firestore 연결을 초기화합니다.
    1. FIREBASE_SERVICE_ACCOUNT_JSON 환경변수(JSON 문자열)
    2. FIREBASE_CREDENTIALS_PATH 파일 경로 (기본 serviceAccountKey.json)
    설정되지 않았거나 초기화 실패 시 로컬 인메모리 폴백 모드로 동작합니다.
    """
    global _db_instance, _is_firebase_connected

    if _db_instance is not None:
        return _db_instance

    try:
        # 1. 환경 변수 JSON 문자열 확인
        if settings.FIREBASE_SERVICE_ACCOUNT_JSON:
            cred_dict = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            _db_instance = firestore.client()
            _is_firebase_connected = True
            print(">>> [Firebase] 환경 변수 JSON 자격 증명으로 Firestore에 성공적으로 연결되었습니다.")
            return _db_instance

        # 2. 로컬 파일 확인
        if os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            _db_instance = firestore.client()
            _is_firebase_connected = True
            print(f">>> [Firebase] 서비스 계정 파일({settings.FIREBASE_CREDENTIALS_PATH})로 Firestore에 연결되었습니다.")
            return _db_instance

    except Exception as e:
        print(f"⚠️ [Firebase] Firestore 초기화 실패: {e}")

    # 자격 증명이 없을 경우 로컬 개발 모드 안내
    print("ℹ️ [Firebase] 유효한 Firebase 자격 증명이 없습니다.")
    print("ℹ️ [Firebase] 로컬 저장소 모드(Fallback)로 실행됩니다. (Firebase 키 설정 시 자동으로 Firestore 사용)")
    _is_firebase_connected = False

    # 로컬 저장소에 초기 데이터가 없으면 data_samsung.json 로드
    _init_local_store_from_file()
    return None


def _init_local_store_from_file():
    """로컬 테스트를 위해 data_samsung.json이 있다면 메모리 스토어에 기본 적재"""
    json_path = os.path.join(os.path.dirname(__file__), "data_samsung.json")
    if os.path.exists(json_path) and not _local_data_store:
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                records = json.load(f)
                for item in records:
                    doc_id = str(uuid.uuid4())
                    _local_data_store[doc_id] = {
                        "id": doc_id,
                        "date": item["date"],
                        "value": float(item["value"]),
                        "memo": item["memo"]
                    }
            print(f">>> [LocalStore] data_samsung.json에서 {len(_local_data_store)}개 레코드를 로컬 메모리에 로드했습니다.")
        except Exception as err:
            print(f"⚠️ [LocalStore] 기본 데이터 로드 실패: {err}")


def is_connected_to_firebase() -> bool:
    return _is_firebase_connected


# ==============================================================================
# DATA 컬렉션 CRUD 연산
# ==============================================================================

def add_data_record(date: str, value: float, memo: str) -> Dict[str, Any]:
    """새 시계열 데이터 추가 (POST /api/data)"""
    record = {
        "date": date,
        "value": round(float(value), 2),
        "memo": memo
    }

    if _is_firebase_connected and _db_instance:
        doc_ref = _db_instance.collection("data").document()
        doc_ref.set(record)
        record["id"] = doc_ref.id
        return record
    else:
        doc_id = str(uuid.uuid4())
        record["id"] = doc_id
        _local_data_store[doc_id] = record
        return record


def get_all_data_records() -> List[Dict[str, Any]]:
    """모든 데이터 목록 조회 (GET /api/data) - 날짜순 정렬"""
    records = []

    if _is_firebase_connected and _db_instance:
        docs = _db_instance.collection("data").order_by("date").stream()
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            records.append(d)
    else:
        records = list(_local_data_store.values())
        records.sort(key=lambda x: x.get("date", ""))

    return records


def update_data_record(record_id: str, update_fields: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """데이터 수정 (PUT /api/data/{id})"""
    clean_fields = {k: v for k, v in update_fields.items() if v is not None}
    if "value" in clean_fields:
        clean_fields["value"] = round(float(clean_fields["value"]), 2)

    if _is_firebase_connected and _db_instance:
        doc_ref = _db_instance.collection("data").document(record_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        doc_ref.update(clean_fields)
        updated = doc_ref.get().to_dict()
        updated["id"] = record_id
        return updated
    else:
        if record_id not in _local_data_store:
            return None
        _local_data_store[record_id].update(clean_fields)
        return _local_data_store[record_id]


def delete_data_record(record_id: str) -> bool:
    """데이터 삭제 (DELETE /api/data/{id})"""
    if _is_firebase_connected and _db_instance:
        doc_ref = _db_instance.collection("data").document(record_id)
        if not doc_ref.get().exists:
            return False
        doc_ref.delete()
        return True
    else:
        if record_id in _local_data_store:
            del _local_data_store[record_id]
            return True
        return False


# ==============================================================================
# CONVERSATIONS 컬렉션 CRUD 연산
# ==============================================================================

def create_conversation(title: str, messages: List[Dict[str, str]], conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """대화 저장 (POST /api/conversations)"""
    cid = conversation_id or str(uuid.uuid4())
    now_str = datetime.now().isoformat()
    conv_data = {
        "title": title,
        "created_at": now_str,
        "messages": messages
    }

    if _is_firebase_connected and _db_instance:
        doc_ref = _db_instance.collection("conversations").document(cid)
        doc_ref.set(conv_data)
        conv_data["id"] = cid
        return conv_data
    else:
        conv_data["id"] = cid
        _local_conversations_store[cid] = conv_data
        return conv_data


def append_message_to_conversation(conversation_id: str, new_messages: List[Dict[str, str]], title: Optional[str] = None) -> Dict[str, Any]:
    """기존 대화에 메시지 추가 또는 신규 생성"""
    if _is_firebase_connected and _db_instance:
        doc_ref = _db_instance.collection("conversations").document(conversation_id)
        doc = doc_ref.get()
        if doc.exists:
            existing = doc.to_dict()
            msgs = existing.get("messages", []) + new_messages
            doc_ref.update({"messages": msgs})
            existing["messages"] = msgs
            existing["id"] = conversation_id
            return existing
        else:
            t = title or (new_messages[0]["content"][:30] if new_messages else "새 대화")
            return create_conversation(t, new_messages, conversation_id=conversation_id)
    else:
        if conversation_id in _local_conversations_store:
            existing = _local_conversations_store[conversation_id]
            existing["messages"].extend(new_messages)
            return existing
        else:
            t = title or (new_messages[0]["content"][:30] if new_messages else "새 대화")
            return create_conversation(t, new_messages, conversation_id=conversation_id)


def get_all_conversations() -> List[Dict[str, Any]]:
    """대화 목록 조회 (GET /api/conversations) - 최신순 정렬"""
    convs = []

    if _is_firebase_connected and _db_instance:
        docs = _db_instance.collection("conversations").stream()
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            convs.append(d)
    else:
        convs = list(_local_conversations_store.values())

    convs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return convs


def get_conversation_by_id(conversation_id: str) -> Optional[Dict[str, Any]]:
    """특정 대화 전체 조회 (GET /api/conversations/{id})"""
    if _is_firebase_connected and _db_instance:
        doc = _db_instance.collection("conversations").document(conversation_id).get()
        if not doc.exists:
            return None
        d = doc.to_dict()
        d["id"] = doc.id
        return d
    else:
        return _local_conversations_store.get(conversation_id)


def delete_conversation_by_id(conversation_id: str) -> bool:
    """대화 삭제 (DELETE /api/conversations/{id})"""
    if _is_firebase_connected and _db_instance:
        doc_ref = _db_instance.collection("conversations").document(conversation_id)
        if not doc_ref.get().exists:
            return False
        doc_ref.delete()
        return True
    else:
        if conversation_id in _local_conversations_store:
            del _local_conversations_store[conversation_id]
            return True
        return False
