# 기본 이미지 설정
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    libxml2-dev \
    libxslt1-dev \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# pip를 사용하여 uv 설치
RUN pip install uv

# 더 나은 레이어 캐싱을 위해 requirements 파일 먼저 복사
COPY pyproject.toml uv.lock ./

# 애플리케이션 코드 복사
COPY . .

# uv를 사용하여 Python 의존성 설치
RUN uv sync --frozen

# docx 지원을 위한 추가 의존성 설치
RUN uv pip install streamlit "unstructured[docx]"

# API 및 Streamlit 모두를 위한 포트 노출
# 참고: 실제 Streamlit 포트는 STREAMLIT_PORT 환경 변수를 통해 사용자 정의 가능
EXPOSE 8080 8501 8765

# 기본 명령은 API 서버 실행
# streamlit 서비스를 위해 docker-compose.yml에서 재정의 가능
CMD ["uv", "run", "uvicorn", "langconnect.server:APP", "--host", "0.0.0.0", "--port",
