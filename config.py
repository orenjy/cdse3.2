import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Gemini API 설정 (Google AI Studio)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

    # Firebase 설정 (키 파일 경로 또는 환경변수 JSON 문자열)
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "serviceAccountKey.json")
    FIREBASE_SERVICE_ACCOUNT_JSON: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")

    # CORS 허용 도메인
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")

    # 포트
    PORT: int = int(os.getenv("PORT", "8000"))

    @property
    def cors_origins(self) -> list[str]:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()
