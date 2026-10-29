# Portfolio integration and source review

The console now previews a local synthetic PDF or JSON file. JSON fields are supplied explicitly, without AI or fabricated confidence. A PDF is sent to `/documents/extract` only after an operator selects Azure extraction. Provider failures remain visible. Extracted values are proposals: the user checks the source, maps the supplier and separately submits the normal invoice schema.

Extraction summaries list missing required fields and provider confidences. The 0.8 review threshold is an uncalibrated demo heuristic; it is not measured field accuracy. Even perfect provider confidence never approves an invoice. Source files and extraction results are not retained in the database; the browser preview is not a durable source archive. Production document retention/malware scanning remain open.

The workflow application may use an **auditor** credential to read `GET /invoices/{id}`. Its server configuration binds each tenant/customer to an invoice ID; no LLM selects the credential or resource. No workflow tool has reviewer/exporter credentials. Accounting approval remains `POST /invoices/{id}/decision` with an independent reviewer, reason and `expected_version`; exports remain a separate exporter operation. The integrated runner proves that workflow and automation approvals cannot substitute for accounting approval.

Run all six sibling repositories via `python3 -m integration.scenario --root ..` from the [playbook](https://github.com/phlppgdfry/ai-transformation-playbook). This is actual local HTTP using synthetic JSON fields, a fixture planner and mock sinks. No OCR or live model execution is claimed. Each repository also keeps its independent setup/demo.

All API calls now receive a generated `X-Request-ID`, `Cache-Control: no-store`, bounded request bodies (5 MiB for PDFs; 256 KiB otherwise) and metadata-only request logs. Oversized chunked requests are checked using actual bytes. API errors omit submitted values. Authentication keys are compared as UTF-8 bytes. Deployment still needs a gateway with rate/concurrency limits, TLS and real enterprise identity.
