# 가족 공유 웹앱

카테고리별로 **텍스트(한 줄 + 체크박스)** 와 **사진**을 가족과 공유하는 Streamlit 웹앱입니다.

- 가족 공통 비밀번호 하나
- 카테고리 추가 (예: 편의점) → 텍스트 / 사진 탭
- 무료 배포: **Streamlit Community Cloud** + **Supabase**

## 로컬에서 실행

1. Python 3.10+ 권장

```bash
cd c:\apps\jjellys
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Supabase 준비 (아래 [Supabase 설정](#supabase-설정) 참고)

3. 시크릿 파일 만들기

```bash
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
```

`.streamlit/secrets.toml`에 비밀번호와 Supabase URL / **service_role** 키를 넣습니다.

4. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 로 접속합니다.

## Supabase 설정

1. [supabase.com](https://supabase.com)에서 무료 프로젝트 생성
2. **SQL Editor**에서 [`supabase_schema.sql`](supabase_schema.sql) 전체 실행
3. **Storage**에 `photos` 버킷이 생겼는지 확인 (SQL에서 생성). 공개(public)여야 사진 URL이 보입니다.
4. **Project Settings → API**에서
   - `Project URL` → `SUPABASE_URL`
   - `service_role` (secret) → `SUPABASE_KEY`  
     (`anon` 키가 아닙니다. service_role은 절대 GitHub에 올리지 마세요.)

## 무료 클라우드 배포 (가족이 모두 접속)

### 1) GitHub에 올리기

`secrets.toml`은 `.gitignore`에 포함되어 있습니다. 예시 파일만 커밋하세요.

```bash
git init
git add .
git commit -m "Add family share Streamlit app"
# GitHub에 새 repo 만든 뒤 push
```

### 2) Streamlit Community Cloud

1. [share.streamlit.io](https://share.streamlit.io) 접속 → GitHub 로그인
2. **New app** → 이 저장소 선택, Main file path: `app.py`
3. **Advanced settings → Secrets**에 로컬 `secrets.toml`과 같은 내용을 붙여넣기:

```toml
APP_PASSWORD = "가족이함께쓰는비밀번호"
SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co"
SUPABASE_KEY = "YOUR_SERVICE_ROLE_KEY"
```

4. Deploy 후 나오는 `https://….streamlit.app` 주소를 가족에게 공유

### 왜 두 서비스인가?

| 역할 | 서비스 | 비고 |
|------|--------|------|
| 웹앱 | Streamlit Community Cloud | 무료, URL 공유 |
| DB·사진 | Supabase Free | Cloud 재시작 시 로컬 파일이 사라지므로 필수 |

월 수십 장 사진 규모면 Supabase 무료 스토리지(~1GB)로 충분합니다.

## 사용 방법

1. 비밀번호 입력 후 입장
2. 왼쪽에서 카테고리 추가·선택
3. **텍스트** 탭: 한 줄 입력 → 체크 / 삭제
4. **사진** 탭: 업로드·보기·삭제

## 프로젝트 구조

```
app.py                 # UI · 로그인 · 카테고리 · 텍스트/사진
db.py                  # Supabase CRUD
supabase_schema.sql    # 테이블 · Storage 버킷
requirements.txt
.streamlit/secrets.toml.example
```
