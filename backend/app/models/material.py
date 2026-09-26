from sqlalchemy import String, Numeric, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class PackagingMaterial(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Packaging film and barrier material entity.
    Stores ASTM barrier properties (OTR, WVTR), biodegradability, recyclability, and cost indices.
    """
    __tablename__ = "materials"

    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    polymer_type: Mapped[str] = mapped_column(String(60), nullable=False, index=True)  # LDPE, HDPE, PP, PET, PLA, PHA, EVOH
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Physical & Barrier Parameters
    thickness_micron: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False, default=25.0)
    otr_cc_m2_day_atm: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)  # ASTM D3985
    wvtr_g_m2_day: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)      # ASTM F1249
    tensile_strength_mpa: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    seal_strength_n_15mm: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    transparency_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Sustainability & Economics
    is_biodegradable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    biodegradation_standard: Mapped[str | None] = mapped_column(String(80), nullable=True)  # ASTM D6400, EN 13432
    recyclability_code: Mapped[int] = mapped_column(Integer, default=7, nullable=False)      # Resin Identification Code (1-7)
    cost_index_relative: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=1.0)
    carbon_footprint_kg_co2_per_kg: Mapped[float | None] = mapped_column(Numeric(6, 3), nullable=True)
    food_contact_certified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
