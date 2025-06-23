# Supabase 인증 설정

이 문서는 LangConnect에서 Supabase 인증을 사용하는 방법을 설명합니다.

## 사전 준비

1. `.env` 파일에 URL과 anon 키가 설정된 Supabase 프로젝트:
  ```
  SUPABASE_URL=https://your-project.supabase.co
  SUPABASE_KEY=your-anon-key
  ```

2. 인증을 활성화하려면 `.env` 파일에서 `IS_TESTING=false`로 설정하세요

## API 엔드포인트

### 인증 엔드포인트

- **POST /auth/signup** - 새 사용자 계정 생성
  ```json
  {
   "email": "user@example.com",
   "password": "password123"
  }
  ```

- **POST /auth/signin** - 기존 계정으로 로그인
  ```json
  {
   "email": "user@example.com",
   "password": "password123"
  }
  ```

- **POST /auth/signout** - 로그아웃 (클라이언트 측 정리)

- **POST /auth/refresh** - 액세스 토큰 갱신
  ```json
  {
   "refresh_token": "your-refresh-token"
  }
  ```

- **GET /auth/me** - 현재 사용자 정보 조회 (인증 필요)

### 응답 형식

인증에 성공하면 다음과 같은 응답이 반환됩니다:
```json
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "user_id": "user-uuid",
  "email": "user@example.com"
}
```

## 인증 사용법

### API 요청에서

Authorization 헤더에 액세스 토큰을 포함하세요:
```
Authorization: Bearer your-access-token
```

### Streamlit 앱에서

Streamlit 앱(`Main.py`)에는 다음 기능이 포함되어 있습니다:
- 로그인/회원가입 폼
- 자동 토큰 관리
- 세션 유지
- 로그아웃 기능

### 인증 테스트

테스트 스크립트 실행:
```bash
python test_supabase_auth.py
```

이 스크립트는 다음을 테스트합니다:
1. 사용자 회원가입
2. 사용자 로그인
3. 인증된 API 요청
4. 현재 사용자 정보 조회

## 보안 참고사항

1. `.env`의 `SUPABASE_KEY`는 **anon** 키여야 하며, 서비스 역할 키가 아니어야 합니다
2. 토큰은 일정 시간이 지나면 만료됩니다 - 새 토큰을 받으려면 refresh 엔드포인트를 사용하세요
3. `IS_TESTING=false`일 때 모든 API 엔드포인트(/health 및 /auth/* 제외)는 인증이 필요합니다

## 인증 지속성

### 페이지 새로고침 후 로그인 상태 유지

Streamlit 앱은 인증을 지속하기 위해 두 가지 방법을 지원합니다:

1. **자동 파일 기반 저장** (기본값)
  - 인증 토큰이 자동으로 `~/.langconnect_auth_cache`에 저장됩니다
  - 토큰은 7일 동안 유효합니다
  - 앱 재시작 시 자동으로 로드됩니다

2. **환경 변수 사용** (선택 사항)
  - `.env` 파일에 다음을 추가하세요:
  ```
  LANGCONNECT_TOKEN=your-access-token
  LANGCONNECT_EMAIL=your-email@example.com
  ```
  - 개발 또는 공유 환경에서 유용합니다

### 보안 참고사항
- 인증 캐시 파일은 홈 디렉터리에 저장됩니다
- 토큰은 보안을 위해 7일 후 만료됩니다
- 환경 변수는 안전한 환경에서만 사용하세요

## 중요 참고사항

### 이메일 인증

기본적으로 Supabase는 신규 회원가입 시 이메일 인증을 요구합니다. 사용자가 회원가입하면:
1. 인증 이메일을 받게 됩니다
2. 이메일의 링크를 클릭해 계정을 인증해야 합니다
3. 인증 후에만 로그인할 수 있습니다

이메일 인증을 비활성화하려면(테스트용):
1. Supabase 프로젝트 대시보드로 이동
2. Authentication → Settings로 이동
3. "Email Auth"에서 "Confirm email"을 비활성화

### Docker로 테스트할 때

Docker Compose로 실행할 때 인증을 활성화하려면 docker-compose.yml에서 `IS_TESTING=false`로 설정하세요.

## 문제 해결

- **"Authentication endpoints are disabled in testing mode"** - `.env` 또는 docker-compose.yml에서 `IS_TESTING=false`로 설정하세요
- **"Email not confirmed"** - 인증 이메일을 확인하거나 Supabase 대시보드에서 이메일 인증을 비활성화하세요
- **"Invalid token or user not found"** - 토큰이 유효하고 만료되지 않았는지 확인하세요
- **Connection errors** - SUPABASE_URL과 SUPABASE_KEY가 올바른지 확인하세요
