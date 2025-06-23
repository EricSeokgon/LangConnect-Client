#!/bin/bash

# 이 스크립트가 위치한 디렉토리를 가져옵니다.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 프로젝트 디렉토리로 변경합니다.
cd "$DIR"

# uv를 사용하여 MCP 서버를 실행합니다.
exec uv run python mcp/mcp_server.py
