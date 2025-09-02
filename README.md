# 🐢 AI 바다거북수프 게임

AI와 함께하는 추리 게임! 질문을 통해 단서를 찾아 정답을 맞춰보세요.

## 🚀 시작하기

### 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 OpenAI API 키를 설정하세요:

```bash
# .env 파일 생성
OPENAI_API_KEY=sk-your_openai_api_key_here
```

**API 키 발급 방법:**
1. [OpenAI Platform](https://platform.openai.com/api-keys) 접속
2. 로그인 후 "Create new secret key" 클릭
3. 생성된 키를 복사하여 `.env` 파일에 붙여넣기

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 앱 실행

```bash
streamlit run app.py
```

## 🎮 게임 방법

1. **에피소드 선택**: 왼쪽 사이드바에서 플레이할 에피소드를 선택
2. **질문하기**: AI에게 질문하여 단서를 찾는 힌트 얻기
3. **단서찾기**: 직접 단서를 입력하여 정답 찾기
4. **게임 완료**: 모든 단서를 찾으면 정답 확인!

## 🔒 보안 기능

### 요청 제한
- **세션당 최대 요청**: 50회
- **분당 최대 요청**: 10회
- **초과 시**: 자동으로 세션 차단

### 세션 관리
- 각 사용자마다 고유 세션 ID 생성
- 요청 수 실시간 모니터링
- 세션 초기화 기능 제공

## 🛠️ 문제 해결

### API 키 오류가 발생하는 경우

**오류 메시지**: `OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.`

**해결 방법**:
1. 프로젝트 루트에 `.env` 파일이 있는지 확인
2. `.env` 파일에 `OPENAI_API_KEY=sk-your_key_here` 형식으로 API 키 추가
3. 앱을 다시 시작

### .env 파일 생성 방법

**Windows**:
```cmd
echo OPENAI_API_KEY=sk-your_key_here > .env
```

**macOS/Linux**:
```bash
echo "OPENAI_API_KEY=sk-your_key_here" > .env
```

## 📁 프로젝트 구조

```
turtle_soup/
├── app.py              # 메인 Streamlit 앱
├── game_logic.py       # 게임 로직 및 AI 상호작용
├── episodes.py         # 에피소드 데이터
├── config.py           # 설정 및 환경 변수
├── security.py         # 보안 및 요청 제한
├── requirements.txt    # Python 의존성
└── README.md          # 프로젝트 문서
```

## ⚠️ 주의사항

- **절대 하지 말 것**:
  - API 키를 코드에 직접 입력
  - API 키를 GitHub에 업로드
  - `.env` 파일을 공개 저장소에 커밋

- **안전한 공유 방법**:
  - `.env` 파일은 개별적으로 설정
  - 실제 API 키는 개별적으로 전달
  - 팀원들에게 직접 API 키 발급 안내

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
