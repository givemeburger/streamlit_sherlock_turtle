import openai
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from config import OPENAI_API_KEY, API_KEY_VALID, API_KEY_ERROR
    from episodes import Episode, EPISODES
    from security import security_manager
except ImportError as e:
    print(f"모듈을 불러올 수 없습니다: {e}")
    raise

class TurtleSoupGame:
    def __init__(self):
        self.current_episode = None
        self.found_clues = set()
        self.game_state = "episode_selection"
        
        # API 키가 유효한 경우에만 OpenAI 클라이언트 초기화
        if API_KEY_VALID:
            try:
                self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
                self.api_available = True
            except Exception as e:
                self.api_available = False
                self.api_error = str(e)
        else:
            self.api_available = False
            self.api_error = API_KEY_ERROR

    def select_episode(self, episode_title):
        for episode in EPISODES:
            if episode.title == episode_title:
                self.current_episode = episode
                self.found_clues = set()
                self.game_state = "playing"
                return True
        return False

    def ask_question(self, user_question, session_id):
        if not self.current_episode:
            return "에피소드를 먼저 선택해주세요."

        # 보안 검증
        is_allowed, message = security_manager.check_rate_limit(session_id)
        if not is_allowed:
            return message

        # API 사용 가능 여부 확인
        if not self.api_available:
            return f"🚫 AI 서비스를 사용할 수 없습니다: {self.api_error}"

        prompt = f"""
        당신은 '바다거북수프' 게임의 게임마스터입니다.

        질문: {self.current_episode.question}
        줄거리: {self.current_episode.answer}
        
        게임의 질문과 줄거리의 전체 내용을 파악하고 사용자의 질문에 다음과 같이 응답하세요.

## Possible Outputs
[
"네.",
"네, 아주 중요한 질문입니다.",
"아니오.",
"아니오. 중요하지 않습니다.",
"예, 아니오로 대답할 수 없는 질문입니다.",
]

## Response Rules
If the question is moving in the right direction → "네."

If it’s on the right track and reveals a critical clue → "네, 아주 중요한 질문입니다."

If it’s going in the wrong direction → "아니오."

If it’s irrelevant or unimportant → "아니오. 중요하지 않습니다."

If the question cannot be answered with Yes/No or completely unrelated to the story → "예, 아니오로 대답할 수 없는 질문입니다."

---
사용자 질문: "{user_question}"

        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "당신은 '바다거북수프' 게임의 게임마스터입니다."},
                    {"role": "user", "content": prompt}
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI 응답 생성 중 오류가 발생했습니다: {str(e)}"

    def find_clue(self, user_input, session_id):
        if not self.current_episode:
            return "에피소드를 먼저 선택해주세요."

        # 보안 검증
        is_allowed, message = security_manager.check_rate_limit(session_id)
        if not is_allowed:
            return message

        # API 사용 가능 여부 확인
        if not self.api_available:
            return f"🚫 AI 서비스를 사용할 수 없습니다: {self.api_error}"

        prompt = f"""
        당신은 '바다거북수프' 게임의 게임마스터입니다.

        사용자의 입력이 다음 중 하나의 단서와 일치하는지 판단해주세요:
        {self.current_episode.clues}
        
        #기준
        사용자의 입력이 단서와 90% 이상 일치하거나 단어나 표현이 달라도 맥락이 일치하는 경우에만 단서를 발견한것으로 간주
        
        #단서 발견
        1. "단서 발견!"이라고 시작하고
        2. 발견한 단서가 무엇인지 데이터에 있는 그대로 응답해줘.

        #일치하지 않음
        1. "추리에 실패했습니다."

        답변은 한국어로 해줘
--------------------------------
        사용자 입력: "{user_input}"

        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": "당신은 '바다거북수프' 게임의 게임마스터입니다."},
                    {"role": "user", "content": prompt}
                ],
            )
            
            ai_response = response.choices[0].message.content
            
            # 단서 발견 여부 확인
            if "단서 발견!" in ai_response:
                # AI 응답에서 발견된 단서를 정확히 찾기
                found_clue = None
                
                # 1. AI 응답에서 직접 단서 내용을 찾기
                for clue in self.current_episode.clues:
                    if clue not in self.found_clues and clue in ai_response:
                        found_clue = clue
                        break
                
                # 2. AI 응답에서 단서를 찾지 못한 경우, 사용자 입력과 단서를 비교
                if not found_clue:
                    for clue in self.current_episode.clues:
                        if clue not in self.found_clues:
                            # 더 정확한 매칭을 위한 다양한 방법 시도
                            user_words = set(user_input.lower().split())
                            clue_words = set(clue.lower().split())
                            
                            # 공통 단어가 2개 이상이거나, 핵심 단어가 포함된 경우
                            common_words = user_words.intersection(clue_words)
                            if (len(common_words) >= 2 or 
                                any(keyword in clue.lower() for keyword in user_input.lower().split()) or
                                any(keyword in user_input.lower() for keyword in clue.lower().split())):
                                found_clue = clue
                                break
                
                if found_clue:
                    self.found_clues.add(found_clue)
                    
                    # 모든 단서를 찾았는지 확인
                    if len(self.found_clues) == len(self.current_episode.clues):
                        self.game_state = "finished"
            
            return ai_response
        except Exception as e:
            return f"AI 응답 생성 중 오류가 발생했습니다: {str(e)}"

    def get_current_episode_info(self):
        if not self.current_episode:
            return None
        return {
            "title": self.current_episode.title,
            "question": self.current_episode.question
        }

    def get_game_progress(self):
        if not self.current_episode:
            return None
        
        total_clues = len(self.current_episode.clues)
        found_clues = len(self.found_clues)
        progress_percentage = (found_clues / total_clues) * 100 if total_clues > 0 else 0
        
        found_clues_list = list(self.found_clues)
        remaining_clues = [clue for clue in self.current_episode.clues if clue not in self.found_clues]
        
        return {
            "total_clues": total_clues,
            "found_clues": found_clues,
            "progress_percentage": progress_percentage,
            "found_clues_list": found_clues_list,
            "remaining_clues": remaining_clues
        }

    def reset_game(self):
        self.current_episode = None
        self.found_clues = set()
        self.game_state = "episode_selection"
