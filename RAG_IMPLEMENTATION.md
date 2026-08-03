# RAG-Dcpl Implementation Checklist

This document is the living implementation record for the local Retrieval-Augmented Generation application.

For the detailed architecture, API contracts, component responsibilities, and Mermaid flow diagrams, see [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md).

Update the checkboxes after each verified milestone. A checkbox is marked complete only when the feature has been implemented and tested.

## Status Legend

- `[x]` Complete and verified
- `[~]` Started or partially implemented
- `[ ]` Planned or remaining
- `[!]` Blocked, needs a decision, or needs repair

## 1. Project Goal

Build a local document question-answering application with:

- Vue 3 frontend
- Django backend API
- Existing Python `rag` package as the RAG engine
- Ollama for embeddings and answer generation
- ChromaDB for vector storage
- Optional SQLite storage for Django application metadata

The application should allow a user to index documents, ask questions, receive grounded answers, and inspect the source chunks used for each answer.

## 2. Current Architecture

```text
Vue browser application
        |
        | Axios HTTP/JSON
        v
Django API
        |
        | calls existing Python modules
        v
rag package
  |          |             |
  v          v             v
Ollama    ChromaDB      document loaders
embedding vector store  PDF/DOCX/TXT/MD
  |
  v
Ollama chat model
```

### Responsibility by service

| Service | Responsibility | Current state |
|---|---|---|
| Vue/Vite | Browser UI, question form, answer and source display | Partially implemented |
| Axios | Sends requests from Vue to Django | Implemented |
| Django | HTTP routing, validation, JSON responses, CORS | Implemented for initial API |
| `rag` package | Loading, chunking, embedding, retrieval, prompting | Working from CLI and API |
| Ollama | Local embeddings and chat answers | Working locally |
| ChromaDB | Persistent vector similarity search | Working with indexed data |
| SQLite | Django document metadata and lifecycle status | Implemented |

## 3. Repository Structure

```text
RAG-dcpl/
├── RAG-FE/                         Vue frontend
│   ├── src/
│   │   ├── App.vue                 Root shell
│   │   ├── main.js                 Vue bootstrap
│   │   ├── services/api.js         Axios API client
│   │   ├── views/HomeView.vue      RAG workspace
│   │   └── assets/                 Frontend styles
│   └── package.json
│
├── RAG_BE/                         Django backend
│   ├── api/
│   │   ├── views.py                Django API endpoints
│   │   └── urls.py                 API routes
│   ├── rag/
│   │   ├── config.py               RAG settings
│   │   ├── document_loader.py      PDF/DOCX/TXT/MD loading
│   │   ├── chunker.py              Text chunking
│   │   ├── embeddings.py           Ollama embeddings
│   │   ├── vectordb.py             ChromaDB wrapper
│   │   ├── ingest.py               Ingestion pipeline
│   │   ├── query.py                Retrieval and prompt pipeline
│   │   └── llm.py                  Ollama chat generation
│   ├── data/                       Source documents
│   ├── chroma_db/                  Persistent vector database
│   ├── media/                      Reserved uploaded-file location
│   ├── manage.py
│   └── requirements.txt
│
└── RAG_IMPLEMENTATION.md           This checklist
```

## 4. Completed Work

### 4.1 Existing RAG engine

- [x] Added the `rag` package to the Django backend.
- [x] Centralized paths and model settings in `rag/config.py`.
- [x] Configured `phi3` as the chat model.
- [x] Configured `nomic-embed-text` as the embedding model.
- [x] Configured 500-character chunks.
- [x] Configured 100-character overlap.
- [x] Configured ChromaDB collection `documents`.
- [x] Configured Top-K retrieval value of 3.
- [x] Added TXT loading.
- [x] Added Markdown loading.
- [x] Added PDF loading with `pypdf`.
- [x] Added DOCX loading with `python-docx`.
- [x] Added character-based chunking.
- [x] Added Ollama embedding generation.
- [x] Added ChromaDB insert and duplicate detection.
- [x] Added ChromaDB similarity search.
- [x] Added context construction.
- [x] Added grounded answer prompt construction.
- [x] Added Ollama answer generation.

### 4.2 Package and dependency stabilization

- [x] Updated RAG imports to use the package namespace, for example `from rag.config import ...`.
- [x] Verified `from rag.query import search_documents` through Django shell.
- [x] Installed `pypdf==6.4.0`.
- [x] Installed `python-docx==1.2.0`.
- [x] Added both dependencies to `RAG_BE/requirements.txt`.
- [x] Verified both existing PDFs can be read.
- [x] Verified `pip check` reports no broken requirements.
- [x] Verified Python compilation with `compileall`.

### 4.3 RAG runtime verification

- [x] Verified Ollama is installed.
- [x] Verified `phi3` models are available.
- [x] Verified `nomic-embed-text` is available.
- [x] Verified ChromaDB persistent storage opens correctly.
- [x] Verified the database contains indexed chunks.
- [x] Verified CLI ingestion.
- [x] Verified duplicate chunks are skipped.
- [x] Verified CLI query and retrieval.
- [x] Verified Ollama generates an answer from retrieved context.

Current known indexed data:

- `Developer Profile.pdf`
- `Understanding the Retrieval-Augmented Generation (RAG) Pipeline.pdf`
- 24 total chunks currently present in ChromaDB
- Re-ingestion correctly skips existing chunks

### 4.4 Django API integration

- [x] Registered `api` in Django `INSTALLED_APPS`.
- [x] Added `api/urls.py`.
- [x] Included API URLs under `/api/`.
- [x] Added CORS middleware.
- [x] Allowed `http://localhost:5173`.
- [x] Allowed `http://127.0.0.1:5173`.
- [x] Added `POST /api/ingest/`.
- [x] Added `POST /api/query/`.
- [x] Added JSON parsing and validation for query requests.
- [x] Added `400` response for missing questions.
- [x] Added `400` response for malformed JSON.
- [x] Added `405` response for unsupported HTTP methods.
- [x] Added `500` JSON error responses for pipeline failures.
- [x] Returned answer text from the query endpoint.
- [x] Returned source filename, chunk index, distance, and content.
- [x] Returned ingestion counts before and after indexing.
- [x] Verified Django system checks.
- [x] Verified API endpoints with Django's test client.
- [x] Verified a real API query through ChromaDB and Ollama.

Current API contracts:

```http
POST /api/query/
Content-Type: application/json

{"question":"What is chunking?"}
```

```json
{
  "question": "What is chunking?",
  "answer": "...",
  "sources": [
    {
      "source": "Understanding the Retrieval-Augmented Generation (RAG) Pipeline.pdf",
      "chunk_index": 7,
      "distance": 0.542,
      "content": "..."
    }
  ]
}
```

```http
POST /api/ingest/
Content-Type: application/json
```

```json
{
  "message": "Ingestion completed.",
  "chunks_before": 24,
  "chunks_after": 24,
  "chunks_added": 0
}
```

### 4.5 Vue frontend integration

- [x] Removed the default Vue welcome screen from the root shell.
- [x] Added an Axios service at `RAG-FE/src/services/api.js`.
- [x] Added configurable `VITE_API_BASE_URL` support.
- [x] Connected the question form to `/api/query/`.
- [x] Connected the refresh-index control to `/api/ingest/`.
- [x] Added question input.
- [x] Added answer display.
- [x] Added retrieved source display.
- [x] Added source expansion panels.
- [x] Added loading state.
- [x] Added error state.
- [x] Added clear workspace action.
- [x] Added ingestion status message.
- [x] Added responsive desktop and mobile layout.
- [x] Verified Vue production build.
- [x] Verified Vue file diagnostics.

## 5. Current Active Work

This is the current implementation checkpoint.

- [x] Browser-level manual test of Vue to Django to Ollama flow.
- [x] Decide whether the current minimal RAG workspace UI meets the first UX milestone.
- [~] Repair or intentionally exempt the existing empty Cypress support file so the full frontend lint command passes.

The core frontend API connection is implemented. The next feature milestone is browser document upload.

## 6. Remaining Implementation Phases

### Phase 1: Finish frontend verification

- [x] Start Django with `python manage.py runserver`.
- [x] Start Vue with `npm run dev`.
- [x] Open the Vue page in a browser.
- [x] Submit a real question from the UI.
- [x] Verify the answer appears.
- [x] Verify retrieved source chunks appear.
- [ ] Expand and inspect the full source chunk content.
- [ ] Click refresh index.
- [ ] Verify ingestion status appears.
- [ ] Test an empty question.
- [ ] Stop/restart Django and verify the frontend error message.
- [ ] Fix the existing empty Cypress support file or document the lint exception.
- [ ] Make `npm run lint` pass.

### Phase 2: Browser document upload

- [x] Add a Django upload endpoint: `POST /api/documents/upload/`.
- [x] Accept multipart form data.
- [x] Validate PDF, DOCX, TXT, and Markdown extensions.
- [ ] Validate file size.
- [x] Sanitize uploaded filenames.
- [x] Save uploaded files into the RAG data directory for the existing ingestion pipeline.
- [x] Ingest the uploaded file.
- [x] Return file and chunk statistics.
- [x] Add a file picker to Vue.
- [x] Add upload progress/loading state.
- [x] Display upload success and failure messages.
- [x] Prevent duplicate upload behavior from creating duplicate chunks.
- [x] Complete a browser click-through for upload and status display.

### Phase 3: Document management

- [x] Add `GET /api/documents/`.
- [x] List source documents and chunk counts.
- [x] Add `DELETE /api/documents/<filename>/` source-based contract.
- [x] Implement source chunk deletion in ChromaDB.
- [x] Add `POST /api/documents/<filename>/` re-index support.
- [x] Add Vue indexed document inventory.
- [x] Add Vue re-index action.
- [x] Complete browser click-through for document list, re-index, and delete.
- [x] Add document status: uploaded, indexing, indexed, failed.
- [x] Store document metadata in SQLite through the Django `Document` model.
- [x] Add a delete confirmation flow test.

### Phase 4: Standard RAG experience

- [x] Add conversation history in the browser.
- [x] Add new-chat/reset behavior.
- [x] Render answer Markdown safely with `marked` and `DOMPurify`.
- [x] Show numbered source citations beside answer messages.
- [x] Show a clear no-answer response when context is insufficient.
- [x] Handle an empty vector database gracefully.
- [x] Add similarity threshold configuration through `RAG_SIMILARITY_THRESHOLD`.
- [x] Make Top-K configurable through `RAG_TOP_K_RESULTS`.
- [x] Add optional streaming responses at `POST /api/query/stream/`.
- [x] Add copy-answer action.
- [x] Add answer timestamps to conversation messages.

### Phase 5: Backend tests

- [ ] Add tests for supported document loaders.
- [ ] Add tests for unsupported file types.
- [ ] Add tests for empty documents.
- [ ] Add tests for chunk size and overlap validation.
- [ ] Add tests for duplicate vector records.
- [ ] Add tests for retrieval result formatting.
- [ ] Add tests for prompt construction.
- [ ] Add API test for valid query.
- [ ] Add API test for empty query.
- [ ] Add API test for malformed JSON.
- [ ] Add API test for unsupported methods.
- [ ] Add API test for ingestion.
- [ ] Mock Ollama in automated tests.
- [ ] Mock ChromaDB where appropriate.
- [ ] Verify tests do not require a running Ollama process.

### Phase 6: Frontend tests

- [ ] Add component test for question submission.
- [ ] Add component test for answer rendering.
- [ ] Add component test for source expansion.
- [ ] Add component test for loading state.
- [ ] Add component test for API failure.
- [ ] Add component test for index refresh.
- [ ] Add Cypress test for the complete query flow.
- [ ] Add Cypress test for the upload flow.
- [ ] Add Cypress test for empty input.
- [ ] Add Cypress test for backend unavailable.
- [ ] Replace or fix starter Cypress examples.

### Phase 7: Configuration and security

- [ ] Move Django `SECRET_KEY` to an environment variable.
- [ ] Set `DEBUG` from an environment variable.
- [ ] Configure `ALLOWED_HOSTS` for each environment.
- [ ] Configure CORS per environment.
- [ ] Decide whether CSRF protection can replace current `csrf_exempt` usage.
- [ ] Add authentication if multiple users are required.
- [ ] Add upload size and request time limits.
- [ ] Validate and sanitize all uploaded files.
- [ ] Keep Ollama and ChromaDB inaccessible directly from the browser.
- [ ] Add structured server logging.
- [ ] Avoid returning internal exception details in production.
- [ ] Add rate limiting if the API becomes public.

### Phase 8: Deployment and operations

- [ ] Document the required Python version.
- [ ] Document the required Node version.
- [ ] Document Ollama installation.
- [ ] Document required Ollama models.
- [ ] Document ChromaDB backup and restore.
- [ ] Document uploaded-file backup.
- [ ] Add production frontend build instructions.
- [ ] Configure a production WSGI/ASGI server.
- [ ] Configure static files.
- [ ] Configure media files.
- [ ] Add health-check endpoint.
- [ ] Add startup verification for Ollama and ChromaDB.
- [ ] Test a clean installation from `requirements.txt` and `package-lock.json`.

## 7. Local Runbook

### Start Ollama

Verify Ollama and models:

```powershell
ollama --version
ollama list
```

Required models:

```text
phi3
nomic-embed-text
```

### Start Django

Run from `RAG_BE`, not the workspace root:

```powershell
cd D:\python-projects\RAG-dcpl\RAG_BE
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py runserver
```

Django API:

```text
http://127.0.0.1:8000/
```

### Start Vue

Run in a second terminal:

```powershell
cd D:\python-projects\RAG-dcpl\RAG-FE
npm run dev
```

Vue application:

```text
http://localhost:5173/
```

### Re-index data-folder documents

Run from `RAG_BE`:

```powershell
.\.venv\Scripts\python.exe -m rag.ingest
```

This currently reads supported files from `RAG_BE/data` and skips duplicate chunk IDs.

### Run the CLI query

```powershell
.\.venv\Scripts\python.exe -m rag.query
```

### Verify package imports

```powershell
.\.venv\Scripts\python.exe manage.py shell
```

Then inside the Python prompt:

```python
from rag.query import search_documents
print("Import successful")
exit()
```

## 8. Verification Checklist

Run these after each meaningful change:

- [x] `RAG_BE/.venv/Scripts/python.exe manage.py check`
- [x] `RAG_BE/.venv/Scripts/python.exe -m compileall -q rag api ollama_RAG_BE`
- [x] `RAG_BE/.venv/Scripts/python.exe -m pip check`
- [x] CLI ingestion smoke test
- [x] CLI query smoke test
- [x] Django API validation tests
- [x] Django real query smoke test
- [x] `RAG-FE/npm run build`
- [x] Vue diagnostics for changed files
- [ ] `RAG-FE/npm run lint` with no errors
- [x] Backend automated test suite
- [ ] Frontend component test suite
- [~] Cypress end-to-end suite (delete-confirmation flow passes; broader flows remain)
- [ ] Manual browser query test
- [ ] Manual browser ingestion test

## 9. Definition of Done

The project is complete when all of the following are checked:

- [ ] A user can open the Vue application.
- [ ] A user can upload supported documents from the browser.
- [ ] A user can see indexing progress and results.
- [ ] A user can ask a question about indexed documents.
- [ ] The answer is generated through the Django API.
- [ ] Retrieval uses ChromaDB and Ollama embeddings.
- [ ] The answer is grounded in retrieved context.
- [ ] The UI displays the source chunks.
- [ ] Empty and invalid requests show useful errors.
- [ ] Users can manage indexed documents.
- [ ] Users can start a new conversation.
- [ ] Backend tests pass without requiring live external services.
- [ ] Frontend and Cypress tests pass.
- [ ] Secrets and production configuration are externalized.
- [ ] Deployment and backup instructions are complete.

## 10. Next Tick

The browser query milestone is complete. The next immediate checklist items are:

- [x] Start both servers.
- [x] Test a question from the Vue browser interface.
- [x] Verify the answer and retrieved sources in the browser.
- [x] Test the refresh-index control from Vue.
- [x] Verify the ingestion status message.
- [x] Test empty-question validation in the browser.
- [ ] Decide how to handle the existing empty Cypress support file.
- [ ] Complete browser click-through for document management actions.
- [x] Add document status reporting.
- [ ] Begin automated backend API tests.
