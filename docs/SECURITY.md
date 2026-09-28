# DocuAgent AI — Security Policy & Defensive Architecture

This document provides a comprehensive security review and overview of defensive controls implemented across DocuAgent AI.

---

## 🛡️ Key Security Vectors & Controls

### 1. SSRF & Navigation Control (Playwright Engine)
- **Target URL Verification**: All incoming recording targets are validated with strict protocol enforcement (`http` / `https` only).
- **Metadata Protection**: Navigation to Cloud Metadata endpoints (`169.254.169.254`, `metadata.google.internal`) is unconditionally rejected.
- **Protocol Restriction**: Non-web schemes (`file://`, `gopher://`, `dict://`, `ftp://`) are explicitly disallowed.

### 2. Sensitive Data & Credential Protection
- **In-Page Highlight Masking**: The injected DOM script inspects input types (`type="password"`, `autocomplete="password"`, and credential attribute patterns) and replaces input text with masked tokens (`••••••••`).
- **Server-side Trace Masking**: The `ActionTracer` validates and re-masks sensitive fields prior to database persistence and WebSocket broadcasting.

### 3. Path Traversal & Identifier Sanitization
- **Strict Character Constraints**: Session and Document IDs (`session_id`, `document_id`) are validated against regex `^[a-zA-Z0-9_-]{1,64}$`.
- **Protected File Access**: Document download and static image storage endpoints restrict resolution strictly within designated storage bounds.

### 4. PDF Exporter & LFI Protection (WeasyPrint)
- **Restricted URL Fetcher**: WeasyPrint is equipped with a custom `secure_url_fetcher` that prevents remote SSRF calls and restricts local file resolution strictly to `STORAGE_DIR` and template assets.

### 5. Multi-Agent Prompt Injection Defenses
- **Untrusted DOM Isolation**: Action traces and raw DOM payloads are delineated within prompts with explicit system-level instructions treating in-page strings as literal documentation subjects rather than executable instructions.
