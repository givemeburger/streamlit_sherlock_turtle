import os
from dotenv import load_dotenv

# .env 파일 로드 (선택적)
try:
    load_dotenv()
except Exception:
    pass  # .env 파일이 없어도 계속 진행

# OpenAI API 키 설정 (Streamlit Cloud 환경 변수도 확인)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("STREAMLIT_OPENAI_API_KEY")

# 게임 설정
GAME_TITLE = "AI 바다거북수프 게임"
GAME_DESCRIPTION = "AI와 함께하는 추리 게임! 질문을 통해 단서를 찾아 정답을 맞춰보세요."

# 보안 설정
MAX_REQUESTS_PER_SESSION = 50  # 세션당 최대 요청 수
MAX_REQUESTS_PER_MINUTE = 10   # 분당 최대 요청 수

# API 키 검증 함수
def validate_api_key():
    """API 키 유효성 검증"""
    if not OPENAI_API_KEY:
        return False, "OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요."
    
    if not OPENAI_API_KEY.startswith("sk-"):
        return False, "올바르지 않은 OpenAI API 키 형식입니다."
    
    return True, ""

# API 키 상태 확인
API_KEY_VALID, API_KEY_ERROR = validate_api_key()
