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
        self.question_count = 0  # 질문 횟수 카운터
        self.used_paid_hints = set()  # 사용된 유료 힌트 인덱스
        
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
                self.question_count = 0  # 질문 횟수 초기화
                self.used_paid_hints = set()  # 유료 힌트 사용 기록 초기화
                return True
        return False

    def investigate(self, user_input, session_id):
        """통합 조사 메서드 - 질문과 단서 찾기를 하나의 프롬프트로 처리"""
        if not self.current_episode:
            return "에피소드를 먼저 선택해주세요."

        # 보안 검증
        is_allowed, message = security_manager.check_rate_limit(session_id)
        if not is_allowed:
            return message

        # API 사용 가능 여부 확인
        if not self.api_available:
            return f"🚫 AI 서비스를 사용할 수 없습니다: {self.api_error}"

        system_prompt = f"""
You are the judge of the Sea Turtle Soup game.  

질문: {self.current_episode.question}
줄거리: {self.current_episode.answer}
정답: {self.current_episode.clues}

# 사용자 입력을 분석하여 다음 중 하나로 응답하세요:

1. **질문인 경우** (왜, 어떻게, 언제, 어디서, 누가, 무엇을, ? 등이 포함된 경우):
   - "네." → True and related to the story
   - "네, 아주 중요한 질문입니다." → True and highly related to the story  
   - "아니오." → False but related to the story
   - "아니오. 아주 중요한 질문입니다." → False and highly related to the story
   - "아니오. 중요하지 않습니다." → False and unrelated to the story
   - "예, 아니오로 대답할 수 없는 질문입니다." → Cannot be answered with Yes/No

2. **단서인 경우** (구체적인 사실이나 상황을 제시한 경우):
   - 단서와 85% 이상 유사하거나 의미/맥락이 같으면 → "단서 발견!" + 정확한 단서 내용 출력
   - 단서와 75% 이상 85% 미만 유사하면 → "거의 찾았어요!"
   - 단서와 매칭되지 않으면 → "추리에 실패했습니다."

**중요**: 
- 질문과 단서를 구분하여 적절한 응답 형식을 사용하세요.
- 단서 발견 시에는 정확한 단서 내용을 그대로 출력하세요.
- 모든 응답은 한국어로만 하세요.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
            )
            ai_response = response.choices[0].message.content
            
            # 단서 발견 여부 확인 및 처리
            if "단서 발견!" in ai_response:
                # AI 응답에서 발견된 단서들을 모두 찾기
                found_clues = []
                
                # 1. AI 응답에서 직접 단서 내용을 찾기
                for clue in self.current_episode.clues:
                    if clue not in self.found_clues and clue in ai_response:
                        found_clues.append(clue)
                
                # 2. AI 응답에서 단서를 찾지 못한 경우, 사용자 입력과 단서를 비교
                if not found_clues:
                    for clue in self.current_episode.clues:
                        if clue not in self.found_clues:
                            # 더 정확한 매칭을 위한 다양한 방법 시도
                            user_words = set(user_input.lower().split())
                            clue_words = set(clue.lower().split())
                            
                            # 공통 단어가 2개 이상이거나, 핵심 단어가 포함된 경우
                            common_words = user_words.intersection(clue_words)
                            if (len(common_words) >= 2 or 
                                any(keyword in clue.lower() for keyword in user_input.lower().split()) or
                                any(keyword in user_input.lower() for keyword in clue_words)):
                                found_clues.append(clue)
                
                # 발견된 모든 단서를 추가
                if found_clues:
                    for clue in found_clues:
                        self.found_clues.add(clue)
                    
                    # 모든 단서를 찾았는지 확인
                    if len(self.found_clues) == len(self.current_episode.clues):
                        self.game_state = "finished"
            
            # 4번째 조사마다 무료 힌트 제공
            if self.question_count % 4 == 0 and self.current_episode.hint_free:
                hint_index = (self.question_count // 4) - 1
                if hint_index < len(self.current_episode.hint_free):
                    hint = self.current_episode.hint_free[hint_index]
                    ai_response += f"\n\n💡 **무료 힌트 ({self.question_count}번째 조사)**: {hint}"
            
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

    def get_paid_hint(self):
        """유료 힌트 제공"""
        if not self.current_episode or not self.current_episode.hint_paid:
            return "유료 힌트가 없습니다."
        
        # 사용 가능한 힌트 인덱스 찾기
        available_hints = []
        for i, hint in enumerate(self.current_episode.hint_paid):
            if i not in self.used_paid_hints:
                available_hints.append((i, hint))
        
        if not available_hints:
            return "모든 유료 힌트를 사용했습니다."
        
        # 무작위로 힌트 선택
        import random
        selected_index, selected_hint = random.choice(available_hints)
        self.used_paid_hints.add(selected_index)
        
        return f"💰 **유료 힌트**: {selected_hint}"
    
    def reset_game(self):
        self.current_episode = None
        self.found_clues = set()
        self.game_state = "episode_selection"
        self.question_count = 0
        self.used_paid_hints = set()
