from sqlalchemy import String, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class MAPComposition(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Modified Atmosphere Packaging (MAP) headspace gas formulation.
    """
    __tablename__ = "map_compositions"

    composition_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Gas Volume Percentages (Summing to 100%)
    oxygen_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    carbon_dioxide_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    nitrogen_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    target_application: Mapped[str | None] = mapped_column(String(150), nullable=True)
