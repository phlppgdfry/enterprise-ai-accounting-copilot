from .security import install_security
import hmac
import json
import os
from importlib.resources import files
from typing import Annotated

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field

from .models import Decision, Invoice, Principal
from .providers import ProviderError, classify, extract_pdf
from .store import Conflict, Missing, Store


class ClassifyRequest(BaseModel):
    description: str = Field(min_length=1, max_length=2000)


def create_app(db_path=None, keys=None):
    app = FastAPI(title="Accounting Review Copilot", version="0.1.0",
                  description="Synthetic portfolio workflow. AI proposes; humans approve; local mock ERP only.")
    store = Store(db_path or os.getenv("ACCOUNTING_DB", "data/accounting.sqlite3"))
    supplied = keys if keys is not None else json.loads(os.getenv("ACCOUNTING_API_KEYS", "{}"))
    principals = {key: Principal.model_validate(value) for key, value in supplied.items()}
    if any(len(k) < 20 for k in principals):
        raise ValueError("API keys must contain at least 20 characters")
    app.state.store = store
    auth_header = APIKeyHeader(name="X-API-Key", auto_error=False)

    def principal(key: Annotated[str | None, Depends(auth_header)]):
        if key:
            for expected, p in principals.items():
                if hmac.compare_digest(key.encode("utf-8"), expected.encode("utf-8")):
                    return p
        raise HTTPException(401, "Missing or invalid API key")

    def require(*roles):
        def check(p: Annotated[Principal, Depends(principal)]):
            if p.role not in roles:
                raise HTTPException(403, "Role does not permit this operation")
            return p
        return check

    @app.exception_handler(Conflict)
    async def conflict(_, exc):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(Missing)
    async def missing(_, exc):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ProviderError)
    async def provider_error(_, exc):
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @app.exception_handler(RequestValidationError)
    async def validation_error(_, exc):
        # Avoid reflecting invoice content or unexpected fields into error logs/clients.
        errors = [{"location": list(error["loc"]), "type": error["type"]} for error in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": errors})

    @app.get("/health", tags=["operations"])
    def health():
        return {"status": "ok", "mode": "synthetic_portfolio", "erp": "local_mock"}

    @app.get("/console", response_class=HTMLResponse, include_in_schema=False)
    def console():
        return HTMLResponse(files("accounting_copilot").joinpath("console.html").read_text(),
                            headers={"Cache-Control": "no-store", "X-Frame-Options": "DENY",
                                     "X-Content-Type-Options": "nosniff"})

    @app.post("/invoices", tags=["invoices"])
    def submit(invoice: Invoice, p: Annotated[Principal, Depends(require("operator"))],
               idempotency_key: Annotated[str, Header(min_length=8, max_length=128)]):
        item, created = store.submit(invoice, idempotency_key, p)
        return JSONResponse(status_code=201 if created else 200, content=item)

    @app.get("/invoices", tags=["invoices"])
    def listing(p: Annotated[Principal, Depends(principal)], limit: int = Query(default=100, ge=1, le=100)):
        return store.list_invoices(p, limit)

    @app.get("/invoices/{identifier}", tags=["invoices"])
    def detail(identifier: str, p: Annotated[Principal, Depends(principal)]):
        return store.get(identifier, p)

    @app.post("/invoices/{identifier}/decision", tags=["review"])
    def decide(identifier: str, decision: Decision, p: Annotated[Principal, Depends(require("reviewer"))]):
        return store.decide(identifier, decision, p)

    @app.post("/exports/run", tags=["exports"])
    def export(p: Annotated[Principal, Depends(require("exporter"))]):
        return store.export_mock(p)

    @app.get("/invoices/{identifier}/audit", tags=["governance"])
    def audit(identifier: str, p: Annotated[Principal, Depends(require("auditor", "reviewer"))]):
        return store.audit(identifier, p)

    @app.get("/metrics", tags=["operations"])
    def metrics(p: Annotated[Principal, Depends(principal)]):
        return store.metrics(p)

    @app.post("/ai/classify", tags=["optional Azure"])
    def category(request: ClassifyRequest, p: Annotated[Principal, Depends(require("operator"))]):
        if os.getenv("ACCOUNTING_AI_MODE", "disabled") != "azure":
            raise HTTPException(503, "Azure AI mode is disabled; no synthetic fallback is used")
        return classify(request.description)

    @app.post("/documents/extract", tags=["optional Azure"])
    def extract(p: Annotated[Principal, Depends(require("operator"))],
                content: Annotated[bytes, Body(media_type="application/pdf")]):
        if os.getenv("ACCOUNTING_AI_MODE", "disabled") != "azure":
            raise HTTPException(503, "Azure AI mode is disabled")
        return extract_pdf(content)

    install_security(app, max_bytes=262144)
    return app


app = create_app()
