import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class RecommendationRecord(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Audit log of recommendations made by the system.
    Records the input criteria, candidate rankings, TOPSIS scores, and user validation feedback.
    """
    __tablename__ = "recommendations"

    commodity_name_input: Mapped[str] = mapped_column(String(120), nullable=False)
    matched_commodity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("commodities.id", ondelete="SET NULL"), 
        nullable=True
    )

    recommended_material_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("materials.id", ondelete="SET NULL"), 
        nullable=True
    )

    suggested_map_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("map_compositions.id", ondelete="SET NULL"), 
        nullable=True
    )

    # Full Input and Output JSON Payloads for Audit & Traceability
    request_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    rule_filtering_summary: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    topsis_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    engine_version: Mapped[str] = mapped_column(String(50), nullable=False, default="M0-foundation")

    # Feedback loop
    user_feedback: Mapped[str | None] = mapped_column(String(50), nullable=True)  # ACCEPTED, REJECTED, MODIFIED
    feedback_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
