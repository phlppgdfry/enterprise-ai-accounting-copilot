from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Invoice(BaseModel):
    model_config = ConfigDict(extra="forbid")
    supplier_id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    invoice_number: str = Field(min_length=1, max_length=80, pattern=r"^[a-zA-Z0-9/_-]+$")
    invoice_date: date
    currency: Literal["EUR"] = "EUR"
    net: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    vat: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    total: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    description: str = Field(min_length=1, max_length=2000)

    @field_validator("net", "vat", "total")
    @classmethod
    def finite_money(cls, value):
        if not value.is_finite():
            raise ValueError("Money must be finite")
        return value.quantize(Decimal("0.01"))

    @model_validator(mode="after")
    def balanced(self):
        if self.net + self.vat != self.total:
            raise ValueError("net + vat must equal total exactly")
        if self.vat > self.net:
            raise ValueError("VAT exceeds net; investigate source document")
        return self


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approve: bool = Field(strict=True)
    reason: str = Field(min_length=5, max_length=500)
    expected_version: int = Field(ge=1)


class Principal(BaseModel):
    actor: str
    tenant: str
    role: Literal["operator", "reviewer", "exporter", "auditor"]


class Category(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Literal["office", "software", "travel", "other"]
    rationale: str = Field(min_length=1, max_length=500)
