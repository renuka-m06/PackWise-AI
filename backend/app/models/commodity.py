from sqlalchemy import String, Numeric, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin


class Commodity(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Food / agricultural commodity entity.
    Stores respiration rate, moisture/oxygen sensitivities, and optimal environmental ranges.
    """
    __tablename__ = "commodities"

    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    scientific_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # FRUIT, VEGETABLE, MEAT, etc.
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Biological & Respiration Parameters
    respiration_rate_mg_co2_kg_hr: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    optimal_temperature_min_c: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False, default=4.0)
    optimal_temperature_max_c: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False, default=8.0)
    optimal_rh_min_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=85.0)
    optimal_rh_max_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=95.0)
    water_activity_aw: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)

    # Sensitivity Flags
    moisture_sensitive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    oxygen_sensitive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ethylene_sensitive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    light_sensitive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    target_shelf_life_unpacked_days: Mapped[int | None] = mapped_column(nullable=True)
