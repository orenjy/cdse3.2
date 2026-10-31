import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import settings
import firebase_db
from routers.data_router import router as data_router
from routers.chat_router import router as chat_router
from routers.conversation_router import router as conversation_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 Firebase 연결 초기화
    firebase_db.init_firebase()
    yield


app = FastAPI(
    title="Data AI Assistant API",
    description="시계열 데이터 분석 및 맞춤형 AI 비서 서비스 백엔드 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(data_router)
app.include_router(chat_router)
app.include_router(conversation_router)


# 헬스체크 엔드포인트
@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "firebase_connected": firebase_db.is_connected_to_firebase(),
        "gemini_configured": bool(settings.GEMINI_API_KEY)
    }


# 프론트엔드 정적 파일 연결 (html=True로 설정하여 index.html, style.css, app.js를 루트 경로로 서빙)
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
