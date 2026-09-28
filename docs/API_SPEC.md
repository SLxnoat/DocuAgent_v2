# DocuAgent AI — REST & WebSocket API Specification

## 1. REST Endpoints (`/api/v1`)

### Session Management (`/api/v1/sessions`)
- **`POST /`**: Create and launch a new recording session with target URL.
- **`GET /{session_id}`**: Get live status and action statistics.
- **`GET /{session_id}/actions`**: Get the full array of captured DOM action traces.
- **`POST /{session_id}/stop`**: Stop browser context, finalize traces.

### Document Generation & Export (`/api/v1/documents`)
- **`POST /generate/{session_id}`**: Invoke LangGraph pipeline to generate SOP manual.
- **`GET /{document_id}`**: Retrieve structured document JSON.
- **`POST /export`**: Export as PDF (`WeasyPrint`) or styled HTML.

### HITL Chat Refinement (`/api/v1/chat`)
- **`POST /refine`**: Submit natural language refinement instruction to modify specific sections or steps.

---

## 2. WebSocket Channels

### Screencast & Input Gateway (`/ws/screencast/{session_id}`)
- **Downlink**: Real-time JPEG frames (`screencast_frame`).
- **Uplink**: Forward mouse clicks and keyboard events (`mouse`, `keyboard`).

### Telemetry Stream (`/ws/events/{session_id}`)
- **Downlink**: Live JSON notifications when DOM actions (`action_recorded`) and pipeline stages complete.
