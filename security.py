import time
from collections import defaultdict
from datetime import datetime, timedelta
import streamlit as st

class SecurityManager:
    def __init__(self):
        self.request_counts = defaultdict(int)  # 세션별 요청 수
        self.request_timestamps = defaultdict(list)  # 세션별 요청 타임스탬프
        self.blocked_sessions = set()  # 차단된 세션
        
    def check_rate_limit(self, session_id: str) -> tuple[bool, str]:
        """요청 제한 확인"""
        current_time = time.time()
        
        # 차단된 세션인지 확인
        if session_id in self.blocked_sessions:
            return False, "🚫 이 세션은 API 남용으로 인해 차단되었습니다."
        
        # 세션당 최대 요청 수 확인
        if self.request_counts[session_id] >= 50:
            self.blocked_sessions.add(session_id)
            return False, "🚫 세션당 최대 요청 수(50회)를 초과했습니다."
        
        # 분당 최대 요청 수 확인
        timestamps = self.request_timestamps[session_id]
        current_minute = current_time - 60
        
        # 1분 이전의 타임스탬프 제거
        timestamps = [ts for ts in timestamps if ts > current_minute]
        self.request_timestamps[session_id] = timestamps
        
        if len(timestamps) >= 100:
            return False, "🚫 분당 최대 요청 수(100회)를 초과했습니다. 잠시 후 다시 시도해주세요."
        
        return True, ""
    
    def record_request(self, session_id: str):
        """요청 기록"""
        current_time = time.time()
        self.request_counts[session_id] += 1
        self.request_timestamps[session_id].append(current_time)
    
    def get_session_stats(self, session_id: str) -> dict:
        """세션 통계 반환"""
        return {
            "total_requests": self.request_counts[session_id],
            "remaining_requests": max(0, 50 - self.request_counts[session_id]),
            "is_blocked": session_id in self.blocked_sessions
        }
    
    def reset_session(self, session_id: str):
        """세션 초기화"""
        self.request_counts[session_id] = 0
        self.request_timestamps[session_id] = []
        if session_id in self.blocked_sessions:
            self.blocked_sessions.remove(session_id)

# 전역 보안 관리자 인스턴스
security_manager = SecurityManager()

def check_api_security():
    """API 보안 상태 확인"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"user_{int(time.time())}_{id(st.session_state)}"
    
    session_id = st.session_state.session_id
    
    # 요청 제한 확인
    is_allowed, message = security_manager.check_rate_limit(session_id)
    
    if not is_allowed:
        st.error(message)
        st.stop()
    
    # 요청 기록
    security_manager.record_request(session_id)
    
    return session_id
