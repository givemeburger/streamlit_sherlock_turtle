import streamlit as st
import time
import sys
import os

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from game_logic import TurtleSoupGame
    from episodes import EPISODE_TITLES, EPISODES
    from config import GAME_TITLE, GAME_DESCRIPTION, API_KEY_VALID, API_KEY_ERROR
    from security import check_api_security, security_manager
except ImportError as e:
    st.error(f"모듈을 불러올 수 없습니다: {e}")
    st.error("파일 구조를 확인해주세요.")
    st.stop()

# 페이지 설정
st.set_page_config(
    page_title=GAME_TITLE,
    page_icon="🐢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
try:
    if 'game' not in st.session_state:
        st.session_state.game = TurtleSoupGame()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
except Exception as e:
    st.error(f"게임 초기화 중 오류가 발생했습니다: {e}")
    st.error("페이지를 새로고침하거나 다시 시작해주세요.")
    st.stop()

def main():
    try:
        # API 키 상태 확인
        if not API_KEY_VALID:
            st.error("🚫 API 키 설정 오류")
            st.error(API_KEY_ERROR)
            st.info("💡 해결 방법:")
            st.info("1. 프로젝트 루트에 .env 파일을 생성하세요")
            st.info("2. .env 파일에 OPENAI_API_KEY=sk-your_key_here를 추가하세요")
            st.info("3. Streamlit Cloud에서는 환경 변수로 STREAMLIT_OPENAI_API_KEY를 설정하세요")
            st.info("4. 앱을 다시 시작하세요")
            st.stop()
    except Exception as e:
        st.error(f"설정 확인 중 오류가 발생했습니다: {e}")
        st.info("페이지를 새로고침하거나 다시 시작해주세요.")
        st.stop()
    
    # 보안 검증
    session_id = check_api_security()
    
    # 헤더
    st.title("🐢 " + GAME_TITLE)
    st.markdown(f"*{GAME_DESCRIPTION}*")
    
    # 사이드바
    with st.sidebar:
        st.header("🎮 게임 메뉴")
        
        # 에피소드 선택
        if st.session_state.game.game_state == "episode_selection":
            st.subheader("에피소드 선택")
            selected_episode = st.selectbox(
                "플레이할 에피소드를 선택하세요:",
                ["에피소드를 선택하세요"] + EPISODE_TITLES
            )
            
            if selected_episode != "에피소드를 선택하세요":
                if st.button("게임 시작"):
                    st.session_state.game.select_episode(selected_episode)
                    st.session_state.chat_history = []
                    st.rerun()
        
        # 게임 진행 중일 때
        elif st.session_state.game.game_state == "playing":
            episode_info = st.session_state.game.get_current_episode_info()
            if episode_info:
                st.subheader(f"📖 {episode_info['title']}")
                st.write(f"**질문:** {episode_info['question']}")
            
            # 진행 상황
            progress = st.session_state.game.get_game_progress()
            if progress:
                st.subheader("📊 진행 상황")
                st.progress(progress['progress_percentage'] / 100)
                st.write(f"단서: {progress['found_clues']}/{progress['total_clues']}")
                
                # 디버깅 정보 (개발 중에만 표시)
                st.info(f"진행률: {progress['progress_percentage']:.1f}%")
                
                if progress['found_clues_list']:
                    st.write("**발견된 단서:**")
                    for clue in progress['found_clues_list']:
                        st.write(f"✅ {clue}")
                
                if progress['remaining_clues']:
                    st.write("**남은 단서:**")
                    for clue in progress['remaining_clues']:
                        st.write(f"❓ ")
            
            # 게임 리셋
            if st.button("🔄 새 게임"):
                st.session_state.game.reset_game()
                st.session_state.chat_history = []
                st.rerun()
        
        # 게임 완료 시
        elif st.session_state.game.game_state == "finished":
            st.subheader("🎉 게임 완료!")
            st.success("모든 단서를 찾았습니다!")
            
            episode_info = st.session_state.game.get_current_episode_info()
            if episode_info:
                st.write(f"**에피소드:** {episode_info['title']}")
                st.write(f"**정답:** {st.session_state.game.current_episode.answer}")
            
            if st.button("🔄 새 게임"):
                st.session_state.game.reset_game()
                st.session_state.chat_history = []
                st.rerun()
        
        # 보안 정보 (간소화)
        st.header("🔒 보안 정보")
        stats = security_manager.get_session_stats(session_id)
        if stats["is_blocked"]:
            st.error("🚫 세션 차단됨")
        else:
            st.success("✅ 정상")
        
        if st.button("🔄 세션 초기화"):
            security_manager.reset_session(session_id)
            st.rerun()
    
    # 메인 컨텐츠
    if st.session_state.game.game_state == "episode_selection":
        st.info("👈 왼쪽 사이드바에서 에피소드를 선택하여 게임을 시작하세요!")
        
        # 에피소드 미리보기
        st.subheader("📚 에피소드 미리보기")
        for i, title in enumerate(EPISODE_TITLES):
            with st.expander(f"📖 {title}"):
                # 에피소드 정보 찾기
                for episode in EPISODES:
                    if episode.title == title:
                        st.write(f"**질문:** {episode.question}")
                        st.write(f"**단서 개수:** {len(episode.clues)}개")
                        break
    
    elif st.session_state.game.game_state == "playing":
        # 게임 인터페이스 - 세로 배치
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 에피소드 정보
            episode_info = st.session_state.game.get_current_episode_info()
            if episode_info:
                st.subheader(f"📖 {episode_info['title']}")
                st.write(f"**사건:** {episode_info['question']}")
                st.divider()
            
            # 진행 상황
            progress = st.session_state.game.get_game_progress()
            if progress:
                st.metric(
                    label="진행률",
                    value=f"{progress['found_clues']}/{progress['total_clues']}",
                    delta=f"{progress['progress_percentage']:.1f}%"
                )
                
                # 디버깅: 조사 횟수 표시
                question_count = getattr(st.session_state.game, 'question_count', 0)
                st.info(f"🔍 조사 횟수: {question_count}회")
                
                if progress['found_clues_list']:
                    st.write("**발견된 단서:**")
                    for clue in progress['found_clues_list']:
                        st.success(f"✅ {clue}")
            
            st.divider()
            
            # 채팅 히스토리 표시 (넓은 영역)
            st.subheader("💬 대화 기록")
            chat_container = st.container()
            with chat_container:
                for message in st.session_state.chat_history:
                    if message['type'] == 'user':
                        st.chat_message("user").write(message['content'])
                    else:
                        st.chat_message("assistant").write(message['content'])
        
        with col2:
            # 게임 정보 표시 (토글)
            if st.session_state.get('show_game_info', False):
                with st.expander("📖 게임 정보", expanded=True):
                    episode_info = st.session_state.game.get_current_episode_info()
                    if episode_info:
                        st.write(f"**에피소드:** {episode_info['title']}")
                        st.write(f"**사건:** {episode_info['question']}")
                        
                        # 정답 미리보기 (게임 완료 시에만)
                        if st.session_state.game.game_state == "finished":
                            st.write(f"**정답:** {st.session_state.game.current_episode.answer}")
                        else:
                            st.write("**정답:** 게임 완료 후 확인 가능")
                    
                    st.divider()
                    
                    # 게임 방법 안내
                    st.write("**🎮 게임 방법:**")
                    st.write("1. **조사하기**: 질문이나 단서를 입력")
                    st.write("2. **질문 예시**: '남자는 왜 죽었을까요?'")
                    st.write("3. **단서 예시**: '금붕어가 물을 마셨다'")
                    st.write("4. **목표**: 모든 단서를 찾아 정답 도출")
                    
                    st.divider()
                    
                    # AI 응답 가이드
                    st.write("**🤖 AI 응답 가이드:**")
                    st.write("• **네.** - 맞는 방향")
                    st.write("• **네, 아주 중요한 질문입니다.** - 핵심 단서 발견")
                    st.write("• **아니오.** - 틀린 방향")
                    st.write("• **아니오. 중요하지 않습니다.** - 관련 없음")
                    st.write("• **예, 아니오로 대답할 수 없는 질문입니다.** - 재질문 필요")
        
        # 조사하기 섹션 - 전체 너비로 배치
        st.subheader("🔍 조사하기")
        
        st.write("질문을 통해 사건을 조사하거나, 단서를 찾아보세요!")
        st.info("💡 **팁**: '남자는 왜 죽었을까요?' 같은 질문이나 '금붕어가 물을 마셨다' 같은 단서를 입력해보세요!")
        
        investigation_input = st.text_input("조사 내용을 입력하세요:", key="investigation_input", placeholder="예: 남자는 왜 죽었을까요? 또는 금붕어가 물을 마셨다", max_chars=30)
        
        col1_btn, col2_btn, col3_btn = st.columns([1, 1, 1])
        with col1_btn:
            if st.button("🔍 조사하기", key="investigate_btn", type="primary"):
                if investigation_input.strip():
                    # 사용자 메시지 추가
                    st.session_state.chat_history.append({
                        'type': 'user',
                        'content': f"🔍 {investigation_input}"
                    })
                    
                    # AI 응답 생성 (통합 프롬프트)
                    with st.spinner("사건을 조사하고 있습니다..."):
                        # 조사 횟수 증가 (안전하게 접근)
                        if not hasattr(st.session_state.game, 'question_count'):
                            st.session_state.game.question_count = 0
                        st.session_state.game.question_count += 1
                        # 통합 조사 메서드 호출
                        ai_response = st.session_state.game.investigate(investigation_input, session_id)
                    
                    # AI 응답 추가
                    st.session_state.chat_history.append({
                        'type': 'assistant',
                        'content': ai_response
                    })
                    
                    # 단서 발견 시 즉시 페이지 새로고침하여 진행상황 업데이트
                    if "단서 발견!" in ai_response:
                        # 발견된 단서 개수 확인
                        progress = st.session_state.game.get_game_progress()
                        if progress:
                            before_count = progress['found_clues'] - 1  # 현재 추가된 단서 제외
                            after_count = progress['found_clues']
                            if after_count > before_count:
                                st.success(f"🎉 {after_count - before_count}개의 단서를 발견했습니다!")
                            else:
                                st.success("🎉 단서를 발견했습니다!")
                        else:
                            st.success("🎉 단서를 발견했습니다!")
                        st.rerun()
                    else:
                        st.rerun()
        
        with col2_btn:
            if st.button("💰 유료 힌트", key="paid_hint_btn", type="secondary"):
                # 유료 힌트 제공
                hint_response = st.session_state.game.get_paid_hint()
                
                # 힌트 응답 추가
                st.session_state.chat_history.append({
                    'type': 'assistant',
                    'content': hint_response
                })
                
                # 모든 유료 힌트 사용 완료 시 토스트 메시지
                if "모든 유료 힌트를 사용했습니다" in hint_response:
                    st.warning("모든 유료 힌트를 사용했습니다")
                
                st.rerun()
        
        with col3_btn:
            if st.button("🗑️ 대화 초기화", key="clear_btn"):
                st.session_state.chat_history = []
                st.rerun()
    
    elif st.session_state.game.game_state == "finished":
        st.success("🎉 축하합니다! 모든 단서를 찾았습니다!")
        
        episode_info = st.session_state.game.get_current_episode_info()
        if episode_info:
            st.subheader(f"📖 {episode_info['title']}")
            st.write(f"**질문:** {episode_info['question']}")
            st.write(f"**정답:** {st.session_state.game.current_episode.answer}")
        
        # 발견된 모든 단서 표시
        progress = st.session_state.game.get_game_progress()
        if progress and progress['found_clues_list']:
            st.subheader("🔍 발견된 모든 단서")
            for clue in progress['found_clues_list']:
                st.success(f"✅ {clue}")
        
        st.info("👈 왼쪽 사이드바에서 새 게임을 시작할 수 있습니다!")

if __name__ == "__main__":
    main()
