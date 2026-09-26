from sqlalchemy import String, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class StorageCondition(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Environmental and cold chain distribution parameters.
    """
    __tablename__ = "storage_conditions"

    condition_profile_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    temperature_c: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    relative_humidity_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    target_shelf_life_days: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    cold_chain_type: Mapped[str] = mapped_column(String(50), nullable=False, default="STRICT_COLD_CHAIN")
