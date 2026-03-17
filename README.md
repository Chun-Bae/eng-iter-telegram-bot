# Eng-Iter Telegram Bot

텔레그램으로 영어 문장을 반복 학습하는 봇입니다. 문장을 등록해두면 설정한 주기마다 자동으로 발송됩니다.

---

## 기능

- **문장 CRUD** - 영어 원문과 한국어 번역을 등록/조회/수정/삭제
- **자동 반복 발송** - 설정한 주기(초)마다 문장을 순환 발송
- **SQLite 저장** - 로컬 DB에 문장과 발송 이력 관리
- **systemd 서비스** - 서버에서 백그라운드 상시 실행
- **GitHub Actions 자동 배포** - `main` 브랜치 push 시 OCI 서버에 자동 배포

---

## 명령어

| 명령어 | 설명 | 예시 |
|---|---|---|
| `!c 원문ㅡ번역` | 문장 등록 | `!c I love you ㅡ 사랑해` |
| `!r ID` | 문장 조회 | `!r 3` |
| `!u ID 원문ㅡ번역` | 문장 수정 | `!u 3 I miss you ㅡ 보고 싶어` |
| `!d ID` | 문장 삭제 | `!d 3` |
| `!ls` | 전체 목록 조회 | `!ls` |
| `!set 초` | 발송 주기 설정 | `!set 3600` |

> 구분자는 한글 `ㅡ` (대시 아님)

---

## 설치 및 실행

### 로컬 실행

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경변수 설정
echo "TELEGRAM_TOKEN=your_token_here" > .env

# 3. 실행
python studybot.py
```

### 서버 배포 (OCI + systemd)

GitHub Secrets에 다음 값을 설정하세요:

| Secret | 내용 |
|---|---|
| `OCI_ADDR` | 서버 IP 주소 |
| `SSH_PRIVATE_KEY` | SSH 개인키 |
| `TELEGRAM_TOKEN` | 텔레그램 봇 토큰 |

`main` 브랜치에 push하면 자동 배포됩니다.

수동으로 서비스 등록 시:

```bash
sudo cp scripts/studybot.service /etc/systemd/system/studybot.service
sudo systemctl daemon-reload
sudo systemctl enable studybot
sudo systemctl start studybot
```

---

## 구조

```
eng-iter-telegram-bot/
├── studybot.py              # 봇 메인 코드
├── requirements.txt         # Python 의존성
├── scripts/
│   └── studybot.service     # systemd 서비스 파일
└── .github/
    └── workflows/
        └── deploy.yml       # GitHub Actions 배포 워크플로우
```

---

## 환경

- Python 3.x
- pyTelegramBotAPI
- python-dotenv
- SQLite3 (별도 설치 불필요)
