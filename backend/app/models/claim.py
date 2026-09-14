from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.policy import Policy


class ClaimStatus(str, Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    INFORMATION_REQUIRED = "information_required"
    APPROVED = "approved"
    PAID = "paid"
    REJECTED = "rejected"


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    claim_number: Mapped[str] = mapped_column(String(24), unique=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id"), nullable=False)
    policy_id: Mapped[str] = mapped_column(ForeignKey("policies.id"), nullable=False)
    incident_date: Mapped[date] = mapped_column(Date, nullable=False)
    incident_type: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    estimated_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    customer: Mapped["Customer"] = relationship(back_populates="claims")
    policy: Mapped["Policy"] = relationship(back_populates="claims")
    events: Mapped[list["ClaimEvent"]] = relationship(
        back_populates="claim",
        cascade="all, delete-orphan",
        order_by="ClaimEvent.created_at",
    )


class ClaimEvent(Base):
    __tablename__ = "claim_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    claim_id: Mapped[str] = mapped_column(ForeignKey("claims.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    claim: Mapped["Claim"] = relationship(back_populates="events")
