# Feature evidence matrix — 29 October 2026

Status vocabulary: **VERIFIED** means the stated local behavior was executed; **IMPLEMENTED BUT NOT VERIFIED** means code/artifacts exist without live acceptance; **MOCKED** means a deliberately substituted external effect; **DOCUMENTED ONLY** is a design/runbook; **PLANNED** is future work. Local tests do not prove production safety, real customer use or legal compliance.

Verification commands and results are in [verification-2026-10-29.json](verification-2026-10-29.json). Original 28 October evidence is retained as historical evidence. The pinned dependency audit reports no known advisories at scan time, not absence of all vulnerabilities. Request logs omit bodies, query strings and credentials.

| Feature | Status | Evidence / limitation |
|---|---|---|
| Invoice validation/duplicates/independent approval/tenant boundaries | VERIFIED | tests/test_workflow.py; actual HTTP runner |
| Source JSON upload, preview, review, export/audit console | VERIFIED | playbook portfolio/browser-qa.json; screenshots/desktop.png |
| Azure extraction/classification transport and field-review code | IMPLEMENTED BUT NOT VERIFIED | HTTP MockTransport contracts pass; no live Azure inference/OCR quality measured |
| Local ERP sink | MOCKED | transactional local SQLite consumer, no external ERP |
| Request limits, strict approval input, safe malformed credential handling | VERIFIED | tests/test_security_regressions.py; tests/test_request_boundary.py |
| Entra, real ERP, durable source retention | PLANNED | docs/runbook.md |
