import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import pandas as pd
from datetime import datetime
import time
import pickle
from pathlib import Path

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8080")
# 환경 변수에서 저장된 인증 자격 증명 확인
SAVED_TOKEN = os.getenv("LANGCONNECT_TOKEN", "")
SAVED_EMAIL = os.getenv("LANGCONNECT_EMAIL", "")

st.set_page_config(page_title="LangConnect Client", page_icon="🔗", layout="wide")

# 인증 캐시 파일 경로 정의
AUTH_CACHE_FILE = Path.home() / ".langconnect_auth_cache"


# 인증 데이터를 파일에 저장하는 함수
def save_auth_to_file(token: str, email: str):
    """인증 데이터를 로컬 파일에 저장합니다."""
    try:
        auth_data = {"token": token, "email": email, "timestamp": time.time()}
        with open(AUTH_CACHE_FILE, "wb") as f:
            pickle.dump(auth_data, f)
    except Exception as e:
        print(f"인증 데이터 저장 실패: {e}")


# 파일에서 인증 데이터를 로드하는 함수
def load_auth_from_file():
    """로컬 파일에서 인증 데이터를 로드합니다."""
    try:
        if AUTH_CACHE_FILE.exists():
            with open(AUTH_CACHE_FILE, "rb") as f:
                auth_data = pickle.load(f)
                # 인증 데이터가 너무 오래되지 않았는지 확인 (예: 7일)
                if time.time() - auth_data.get("timestamp", 0) < 7 * 24 * 3600:
                    return auth_data.get("token"), auth_data.get("email")
    except Exception as e:
        print(f"인증 데이터 로드 실패: {e}")
    return None, None


# 인증 파일 삭제 함수
def clear_auth_file():
    """인증 캐시 파일을 삭제합니다."""
    try:
        if AUTH_CACHE_FILE.exists():
            AUTH_CACHE_FILE.unlink()
    except Exception as e:
        print(f"인증 파일 삭제 실패: {e}")


# 인증을 위한 세션 상태 초기화
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "auth_loaded" not in st.session_state:
    st.session_state.auth_loaded = False

# 처음 로드 시 파일 또는 환경에서 인증을 로드하려고 시도
if not st.session_state.auth_loaded:
    # 먼저 파일에서 로드 시도
    token, email = load_auth_from_file()

    # 파일에서 찾을 수 없으면 환경 변수에서 시도
    if not token and SAVED_TOKEN and SAVED_EMAIL:
        token = SAVED_TOKEN
        email = SAVED_EMAIL

    # 유효한 자격 증명이 있으면 설정
    if token and email:
        st.session_state.authenticated = True
        st.session_state.access_token = token
        st.session_state.user_email = email

    st.session_state.auth_loaded = True


def get_headers(include_content_type=True):
    headers = {
        "Accept": "application/json",
    }
    # SUPABASE에서 access_token 사용
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if include_content_type:
        headers["Content-Type"] = "application/json"
    return headers


def make_request(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    files: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
) -> tuple[bool, Any]:
    url = f"{API_BASE_URL}{endpoint}"

    try:
        if method == "GET":
            headers = get_headers()
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            if files:
                headers = get_headers(include_content_type=False)
                response = requests.post(url, headers=headers, data=data, files=files)
            else:
                headers = get_headers()
                response = requests.post(url, headers=headers, json=json_data)
        elif method == "DELETE":
            headers = get_headers()
            response = requests.delete(url, headers=headers)
        elif method == "PATCH":
            headers = get_headers()
            response = requests.patch(url, headers=headers, json=json_data)
        else:
            return False, f"지원되지 않는 메서드: {method}"

        if response.status_code in [200, 201, 204]:
            if response.status_code == 204:
                return True, "성공 (내용 없음)"
            try:
                return True, response.json()
            except:
                return True, response.text
        else:
            try:
                error_detail = response.json()
                return (
                    False,
                    f"오류 {response.status_code}: {json.dumps(error_detail, indent=2)}",
                )
            except:
                return False, f"오류 {response.status_code}: {response.text}"
    except requests.exceptions.ConnectionError:
        return (
            False,
            f"연결 실패. API가 {API_BASE_URL}에서 실행 중인지 확인하십시오.",
        )
    except Exception as e:
        return False, f"요청 실패: {str(e)}"


# Collections 탭이 pages/1_Collections.py로 이동되었습니다.


# API 테스터 탭이 pages/4_API_Tester.py로 이동되었습니다.

# 문서 업로드 탭이 pages/2_Documents.py로 이동되었습니다.

# 벡터 검색 탭이 pages/3_Search.py로 이동되었습니다.

# 문서 관리 탭이 pages/2_Documents.py로 이동되었습니다.


def auth_page():
    """인증 페이지를 표시합니다."""
    st.title("🔗 LangConnect Client")
    st.subheader("인증")

    tab1, tab2 = st.tabs(["로그인", "가입"])

    with tab1:
        with st.form("signin_form"):
            email = st.text_input("이메일", placeholder="user@example.com")
            password = st.text_input("비밀번호", type="password")
            submitted = st.form_submit_button("로그인", type="primary")

            if submitted:
                if not email or not password:
                    st.error("이메일과 비밀번호를 모두 입력하십시오.")
                else:
                    with st.spinner("로그인 중..."):
                        success, result = make_request(
                            "POST",
                            "/auth/signin",
                            json_data={"email": email, "password": password},
                        )

                    if success:
                        st.session_state.authenticated = True
                        st.session_state.access_token = result["access_token"]
                        st.session_state.user_email = result["email"]
                        # 파일에 저장
                        save_auth_to_file(result["access_token"], result["email"])
                        st.success("성공적으로 로그인되었습니다!")
                        st.rerun()
                    else:
                        st.error(f"로그인 실패: {result}")

    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("이메일", placeholder="user@example.com")
            new_password = st.text_input("비밀번호", type="password")
            confirm_password = st.text_input("비밀번호 확인", type="password")
            submitted = st.form_submit_button("가입", type="primary")

            if submitted:
                if not new_email or not new_password:
                    st.error("이메일과 비밀번호를 모두 입력하십시오.")
                elif new_password != confirm_password:
                    st.error("비밀번호가 일치하지 않습니다.")
                elif len(new_password) < 6:
                    st.error("비밀번호는 6자 이상이어야 합니다.")
                else:
                    with st.spinner("계정 생성 중..."):
                        success, result = make_request(
                            "POST",
                            "/auth/signup",
                            json_data={"email": new_email, "password": new_password},
                        )

                    if success:
                        st.session_state.authenticated = True
                        st.session_state.access_token = result["access_token"]
                        st.session_state.user_email = result["email"]
                        # 파일에 저장
                        save_auth_to_file(result["access_token"], result["email"])
                        st.success("계정이 성공적으로 생성되었습니다!")
                        st.rerun()
                    else:
                        st.error(f"가입 실패: {result}")


def main():
    # 사용자가 인증되었는지 확인
    if not st.session_state.authenticated:
        auth_page()
        return

    st.title("🔗 LangConnect Client")

    st.markdown(
        """
    **LangConnect**에 오신 것을 환영합니다 - LangChain과 PostgreSQL로 구동되는 강력한 문서 관리 및 검색 시스템입니다.

    ## 🚀 기능

    이 애플리케이션은 고급 검색 기능을 갖춘 문서 관리를 위한 포괄적인 인터페이스를 제공합니다:
    """
    )

    # 페이지 탐색
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📚 컬렉션 관리")
        st.markdown(
            """
        - 문서 컬렉션 생성 및 관리
        - 컬렉션 통계 보기
        - 컬렉션 일괄 삭제
        """
        )
        st.page_link("pages/1_Collections.py", label="컬렉션으로 이동", icon="📚")

        st.markdown("### 📄 문서 관리")
        st.markdown(
            """
        - 여러 문서 업로드 (PDF, TXT, MD, DOCX)
        - 문서 청크 보기 및 관리
        - 개별 청크 또는 전체 문서 삭제
        """
        )
        st.page_link("pages/2_Documents.py", label="문서로 이동", icon="📄")

    with col2:
        st.markdown("### 🔍 검색")
        st.markdown(
            """
        - **의미론적 검색**: AI 기반 유사성 검색
        - **키워드 검색**: 기존 전체 텍스트 검색
        - **하이브리드 검색**: 두 접근 방식의 장점 결합
        - 고급 메타데이터 필터링
        """
        )
        st.page_link("pages/3_Search.py", label="검색으로 이동", icon="🔍")

        st.markdown("### 🧪 API 테스터")
        st.markdown(
            """
        - 모든 API 엔드포인트 직접 테스트
        - API 기능 탐색
        - 디버깅 및 통합 개발
        """
        )
        st.page_link("pages/4_API_Tester.py", label="API 테스터로 이동", icon="🧪")

    st.divider()

    # 프로젝트 정보
    st.markdown("## 📌 이 프로젝트에 대하여")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(
            """
        **LangConnect**는 다음의 기능을 결합한 오픈 소스 프로젝트입니다:
        - 🦜 **LangChain**: 문서 처리 및 임베딩
        - 🐘 **PostgreSQL**: 벡터 스토리지를 위한 pgvector 확장
        - ⚡ **FastAPI**: 고성능 API 백엔드
        - 🎨 **Streamlit**: 대화형 사용자 인터페이스

        RAG (검색 증강 생성) 애플리케이션 구축에 적합합니다!
        """
        )

    with col2:
        st.markdown("### 🔗 링크")
        st.markdown(
            """
        - 📦 [GitHub 저장소](https://github.com/teddynote-lab/LangConnect-Client)
        - 👨‍💻 [TeddyNote LAB](https://github.com/teddynote-lab)
        - 📚 [설명서](https://github.com/teddynote-lab/LangConnect-Client#readme)
        """
        )

    st.divider()

    # 바닥글
    st.markdown(
        """
    <div style='text-align: center; color: #666; padding: 20px;'>
        ❤️로 <a href='https://github.com/teddynote-lab' target='_blank'>TeddyNote LAB</a>에서 제작
    </div>
    """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("구성")

        if st.session_state.authenticated:
            st.write(f"**사용자:** {st.session_state.user_email}")
            if st.button("로그아웃", key="signout_btn"):
                st.session_state.authenticated = False
                st.session_state.access_token = None
                st.session_state.user_email = None
                # 인증 파일 삭제
                clear_auth_file()
                st.rerun()
        st.divider()

        st.subheader("연결 상태")
        if st.button("연결 테스트"):
            with st.spinner("연결 테스트 중..."):
                success, result = make_request("GET", "/health")
                if success:
                    st.success("✅ API가 정상입니다.")
                    st.json(result)
                else:
                    st.error("❌ 연결 실패")
                    st.error(result)


if __name__ == "__main__":
    main()
