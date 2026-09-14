from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    service: str
    env: str


class ReadyResponse(BaseModel):
    status: str
    database: str
    seed: dict[str, int]
    graph: str


class PolicyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_code: str
    name: str
    coverage_text: str
    exclusions: str
    limitations: str


class PolicySearchHit(BaseModel):
    product_code: str
    name: str
    section: str
    snippet: str
    score: int


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    full_name: str
    date_of_birth: date
    email: str
    policy_number: str
    product_code: str
    last4_id: str


class ClaimEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: str
    note: str
    created_at: datetime


class ClaimOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    claim_number: str
    incident_date: date
    incident_type: str
    description: str
    location: str
    estimated_amount: Decimal
    status: str
    summary: str
    customer: CustomerOut
    policy: PolicyOut
    events: list[ClaimEventOut]


class CatalogSummary(BaseModel):
    customers: int
    policies: int
    claims: int


class IdentityVerifyIn(BaseModel):
    full_name: str
    date_of_birth: date
    policy_number: str


class IdentityVerifyOut(BaseModel):
    verified: bool
    message: str
    customer: CustomerOut | None = None


class ClaimCreateIn(BaseModel):
    policy_number: str
    incident_date: date
    incident_type: str
    description: str
    location: str
    estimated_amount: Decimal = Field(gt=0)


class ChatIn(BaseModel):
    session_id: str
    message: str


class ChatOut(BaseModel):
    session_id: str
    reply: str
    state: dict[str, Any]


class SessionOut(BaseModel):
    session_id: str
    state: dict[str, Any]
