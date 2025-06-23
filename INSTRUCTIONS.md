당신은 RAG 시스템을 위한 REST API를 구현하고 있습니다. FastAPI와 LangChain을 사용해야 합니다.

다음은 구현해야 할 다양한 엔드포인트에 대한 지침입니다.

# API 엔드포인트 정의

## 컬렉션
벡터 스토어 컬렉션을 관리합니다.

- POST /collections
  - 새 컬렉션을 생성합니다.
  - 요청 본문: 컬렉션 세부 정보가 포함된 JSON (예: {'name': 'my_collection'}).
  - 응답: 생성된 컬렉션의 세부 정보 또는 확인.

- GET /collections
  - 사용 가능한 모든 컬렉션을 나열합니다.
  - 응답: 컬렉션 식별자 또는 객체 목록.

- GET /collections/{collection_id}
  - 특정 컬렉션의 세부 정보를 검색합니다.
  - 경로 매개변수: collection_id - 검색할 컬렉션의 ID.
  - 응답: 지정된 컬렉션의 세부 정보.

- PUT /collections/{collection_id}
  - 기존 컬렉션을 업데이트/대체합니다 (예: 이름 변경).
  - 경로 매개변수: collection_id - 업데이트할 컬렉션의 ID.
  - 요청 본문: 전체 업데이트된 컬렉션 세부 정보가 포함된 JSON.
  - 응답: 업데이트된 컬렉션의 세부 정보.

- PATCH /collections/{collection_id}
  - 기존 컬렉션을 부분적으로 업데이트합니다.
  - 경로 매개변수: collection_id - 업데이트할 컬렉션의 ID.
  - 요청 본문: 업데이트할 특정 필드가 포함된 JSON.
  - 응답: 업데이트된 컬렉션의 세부 정보.

- DELETE /collections/{collection_id}
  - 특정 컬렉션을 삭제합니다.
  - 경로 매개변수: collection_id - 삭제할 컬렉션의 ID.
  - 응답: 삭제 확인.

## 문서 (컬렉션 내)
특정 컬렉션 내에서 문서를 관리합니다 (RAG 기능).

- POST /collections/{collection_id}/documents
  - 지정된 컬렉션에 새 문서를 인덱싱 (추가)합니다.
  - 경로 매개변수: collection_id - 문서를 추가할 컬렉션의 ID.
  - 요청 본문: 인덱싱할 문서 데이터.
  - 응답: 인덱싱된 문서의 식별자 또는 세부 정보.

- GET /collections/{collection_id}/documents
  - 특정 컬렉션 내의 모든 문서를 나열합니다.
  - 경로 매개변수: collection_id - 컬렉션의 ID.
  - 쿼리 매개변수 (선택 사항):
      - query={search_terms}: 검색어를 기반으로 문서를 필터링합니다.
      - limit={N}: 결과 수를 제한합니다.
      - offset={M}: 처음 M개의 결과를 건너뜁니다 (페이지 매김용).
  - 응답: 컬렉션 내의 문서 식별자 또는 객체 목록.

- GET /collections/{collection_id}/documents/{document_id}
  - 컬렉션에서 특정 문서를 검색합니다.
  - 경로 매개변수:
      - collection_id: 컬렉션의 ID.
      - document_id: 검색할 문서의 ID.
  - 응답: 지정된 문서의 내용 또는 세부 정보.

- PUT /collections/{collection_id}/documents/{document_id}
  - 컬렉션에서 기존 문서를 업데이트/대체합니다.
  - 경로 매개변수:
      - collection_id: 컬렉션의 ID.
      - document_id: 업데이트할 문서의 ID.
  - 요청 본문: 전체 업데이트된 문서 데이터.
  - 응답: 업데이트된 문서의 세부 정보.

- PATCH /collections/{collection_id}/documents/{document_id}
  - 컬렉션에서 기존 문서를 부분적으로 업데이트합니다.
  - 경로 매개변수:
      - collection_id: 컬렉션의 ID.
      - document_id: 업데이트할 문서의 ID.
  - 요청 본문: 업데이트할 문서의 특정 필드/부분이 포함된 JSON.
  - 응답: 업데이트된 문서의 세부 정보.

- DELETE /collections/{collection_id}/documents/{document_id}
  - 컬렉션에서 특정 문서를 삭제합니다.
  - 경로 매개변수:
      - collection_id: 컬렉션의 ID.
      - document_id: 삭제할 문서의 ID.
  - 응답: 삭제 확인.

- POST /collections/{collection_id}/documents/search (대체 검색)
  - 잠재적으로 복잡한 기준을 사용하여 특정 컬렉션 내에서 검색을 수행합니다.
  - 쿼리 매개변수가 있는 GET이 충분하지 않은 경우 (예: 요청 본문이 필요한 경우) 사용합니다.
  - 경로 매개변수: collection_id - 검색할 컬렉션의 ID.
  - 요청 본문: 검색 기준이 포함된 JSON.
  - 응답: 일치하는 문서 목록.

## LangChain 통합

이 애플리케이션을 LangChain 문서 로더, 텍스트 분할기 및 벡터 스토어와 함께 설정하십시오.

### 문서 로더

문서를 업로드하기 위한 API 입력에 FastAPI의 `UploadFile` 유형을 사용해야 합니다. 그런 다음 `langchain_core.documents`의 `Blob` 클래스를 사용하여 업로드된 파일을 Blob으로 로드합니다.
마지막으로 `langchain_community.document_loaders.parsers.generic`의 `MimeTypeBasedParser`를 사용하여 Blob을 문서로 파싱합니다. 다음은 예제 코드와 지원해야 하는 문서 유형입니다.

```python
from langchain_community.document_loaders.parsers import BS4HTMLParser, PDFMinerParser
from langchain_community.document_loaders.parsers.generic import MimeTypeBasedParser
from langchain_community.document_loaders.parsers.msword import MsWordParser
from langchain_community.document_loaders.parsers.txt import TextParser

HANDLERS = {
    "application/pdf": PDFMinerParser(),
    "text/plain": TextParser(),
    "text/html": BS4HTMLParser(),
    "application/msword": MsWordParser(),
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": (
        MsWordParser()
    ),
}

SUPPORTED_MIMETYPES = sorted(HANDLERS.keys())

MIMETYPE_BASED_PARSER = MimeTypeBasedParser(
    handlers=HANDLERS,
    fallback_parser=None,
)
```
