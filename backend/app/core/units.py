"""
PackWise AI - Unit Normalization Engine
Provides deterministic, testable scientific unit conversions.
Strict anti-fabrication: Never guesses unknown units; raises UnknownUnitError.
"""
from dataclasses import dataclass
from typing import Optional


class UnknownUnitError(ValueError):
    """Raised when a physical quantity is accompanied by an unrecognized or missing unit."""
    pass


class InvalidMeasurementError(ValueError):
    """Raised when a measurement value is physically impossible (e.g., negative Kelvin)."""
    pass


@dataclass(frozen=True)
class ConversionResult:
    """Audit record capturing raw vs normalized values and conversion method."""
    original_value: float
    original_unit: str
    normalized_value: float
    normalized_unit: str
    conversion_method: str


class UnitConverter:
    """
    Scientific unit conversion utilities for food properties, barrier transmission,
    and storage conditions.
    """

    # -------------------------------------------------------------------------
    # 1. Temperature Normalization (Target: Celsius [°C])
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_temperature(value: float, unit: str) -> ConversionResult:
        clean_unit = unit.strip().upper()
        if clean_unit in ("C", "°C", "CELSIUS", "CENTIGRADE"):
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(value, 2),
                normalized_unit="°C",
                conversion_method="identity"
            )
        elif clean_unit in ("F", "°F", "FAHRENHEIT"):
            celsius = (value - 32.0) * (5.0 / 9.0)
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(celsius, 2),
                normalized_unit="°C",
                conversion_method="formula: (F - 32) * 5/9"
            )
        elif clean_unit in ("K", "KELVIN"):
            if value < 0:
                raise InvalidMeasurementError(f"Negative absolute temperature: {value} K")
            celsius = value - 273.15
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(celsius, 2),
                normalized_unit="°C",
                conversion_method="formula: K - 273.15"
            )
        else:
            raise UnknownUnitError(f"Unrecognized temperature unit: '{unit}'")

    # -------------------------------------------------------------------------
    # 2. Thickness Normalization (Target: Microns [µm])
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_thickness(value: float, unit: str) -> ConversionResult:
        if value <= 0:
            raise InvalidMeasurementError(f"Thickness must be strictly positive, got: {value}")
        clean_unit = unit.strip().lower()
        if clean_unit in ("um", "µm", "micron", "microns", "micrometer", "micrometers"):
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(value, 2),
                normalized_unit="µm",
                conversion_method="identity"
            )
        elif clean_unit in ("mil", "mils", "thou"):
            # 1 mil = 0.001 inch = 25.4 µm
            microns = value * 25.4
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(microns, 2),
                normalized_unit="µm",
                conversion_method="multiplication: mil * 25.4"
            )
        elif clean_unit in ("mm", "millimeter", "millimeters"):
            microns = value * 1000.0
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(microns, 2),
                normalized_unit="µm",
                conversion_method="multiplication: mm * 1000"
            )
        elif clean_unit in ("in", "inch", "inches"):
            microns = value * 25400.0
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(microns, 2),
                normalized_unit="µm",
                conversion_method="multiplication: in * 25400"
            )
        else:
            raise UnknownUnitError(f"Unrecognized thickness unit: '{unit}'")

    # -------------------------------------------------------------------------
    # 3. Oxygen Transmission Rate (Target: cc / (m²·day·atm))
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_otr(value: float, unit: str) -> ConversionResult:
        if value < 0:
            raise InvalidMeasurementError(f"OTR cannot be negative, got: {value}")
        clean_unit = unit.strip().lower().replace(" ", "").replace("^2", "2").replace("·", "*")
        
        # Standard: cc/(m2*day*atm) or ml/(m2*day*atm) or cm3/(m2*24h*atm)
        if clean_unit in (
            "cc/(m2*day*atm)", "cc/(m2*day)", "ml/(m2*day*atm)", "ml/(m2*day)",
            "cm3/(m2*day*atm)", "cm3/(m2*24h*atm)", "cm3/(m2*day)", "cc/m2/day/atm",
            "cc/m2/day", "cm3/m2/day"
        ):
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(value, 3),
                normalized_unit="cc/(m²·day·atm)",
                conversion_method="identity"
            )
        # Bar pressure unit: 1 bar = 0.986923 atm => divide by 0.986923 (or multiply by 1.01325)
        elif clean_unit in ("cm3/(m2*day*bar)", "cc/(m2*day*bar)", "ml/(m2*day*bar)"):
            normalized = value * 1.01325
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(normalized, 3),
                normalized_unit="cc/(m²·day·atm)",
                conversion_method="pressure_adjustment: bar * 1.01325"
            )
        # US Customary: cc / (100 in² · day · atm)
        # 1 m² = 1550.0031 in² => factor = 1550.0031 / 100 = 15.500031
        elif clean_unit in (
            "cc/(100in2*day*atm)", "cc/(100in2*day)", "cc/100in2/day",
            "ml/(100in2*day*atm)", "ml/(100in2*day)"
        ):
            normalized = value * 15.500031
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(normalized, 3),
                normalized_unit="cc/(m²·day·atm)",
                conversion_method="area_conversion: (cc/100in2) * 15.500031"
            )
        else:
            raise UnknownUnitError(f"Unrecognized OTR unit: '{unit}'")

    # -------------------------------------------------------------------------
    # 4. Water Vapor Transmission Rate (Target: g / (m²·day))
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_wvtr(value: float, unit: str) -> ConversionResult:
        if value < 0:
            raise InvalidMeasurementError(f"WVTR cannot be negative, got: {value}")
        clean_unit = unit.strip().lower().replace(" ", "").replace("^2", "2").replace("·", "*")
        
        # Standard: g/(m2*day) or g/(m2*24h)
        if clean_unit in ("g/(m2*day)", "g/(m2*24h)", "g/m2/day", "g/m2/24h", "g/m2*day"):
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(value, 3),
                normalized_unit="g/(m²·day)",
                conversion_method="identity"
            )
        # US Customary: g / (100 in² · day)
        elif clean_unit in ("g/(100in2*day)", "g/(100in2*24h)", "g/100in2/day", "g/100in2/24h"):
            normalized = value * 15.500031
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(normalized, 3),
                normalized_unit="g/(m²·day)",
                conversion_method="area_conversion: (g/100in2) * 15.500031"
            )
        # mg / (m² · day)
        elif clean_unit in ("mg/(m2*day)", "mg/m2/day", "mg/(m2*24h)"):
            normalized = value / 1000.0
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(normalized, 3),
                normalized_unit="g/(m²·day)",
                conversion_method="mass_conversion: mg / 1000"
            )
        else:
            raise UnknownUnitError(f"Unrecognized WVTR unit: '{unit}'")

    # -------------------------------------------------------------------------
    # 5. Produce Respiration Rate (Target: mg CO₂ / (kg·hr))
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_respiration_rate(
        value: float,
        unit: str,
        temperature_c: Optional[float] = None
    ) -> ConversionResult:
        """
        Normalizes respiration rate to mg CO2 / (kg·hr).
        If unit is volume-based (mL CO2 / (kg·hr)), converts using ideal gas law at
        the observation temperature (or STP 0°C if temperature is unspecified).
        Density of CO2 at T: rho(T) = (P * M) / (R * T_kelvin) = 44.01 / (0.082057 * T_k) g/L = mg/mL.
        At 0°C: 1.9635 mg/mL. At 5°C: 1.9282 mg/mL. At 20°C: 1.8295 mg/mL.
        """
        if value < 0:
            raise InvalidMeasurementError(f"Respiration rate cannot be negative, got: {value}")
        clean_unit = unit.strip().lower().replace(" ", "").replace("·", "*")

        if clean_unit in (
            "mgco2/(kg*hr)", "mgco2/kg/hr", "mgco2/(kg*h)", "mg/kg/hr", "mg/(kg*hr)", "mgco2/kg-hr"
        ):
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(value, 2),
                normalized_unit="mg CO₂/(kg·hr)",
                conversion_method="identity"
            )
        elif clean_unit in (
            "mlco2/(kg*hr)", "mlco2/kg/hr", "mlco2/(kg*h)", "ml/kg/hr", "ml/(kg*hr)",
            "cm3co2/(kg*hr)", "cm3/kg/hr", "mlco2/kg-hr"
        ):
            temp_c = 0.0 if temperature_c is None else temperature_c
            temp_k = temp_c + 273.15
            # Density in mg / mL: M_CO2 / V_molar(T) = 44010 mg / (22414 mL * (T_k / 273.15))
            # = (44.01 * 1000) / (82.057 * temp_k)
            co2_density_mg_ml = (44.01 * 1000.0) / (82.0574 * temp_k)
            mg_co2 = value * co2_density_mg_ml
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(mg_co2, 2),
                normalized_unit="mg CO₂/(kg·hr)",
                conversion_method=f"ideal_gas_conversion: mL * {co2_density_mg_ml:.4f} mg/mL at {temp_c}°C"
            )
        else:
            raise UnknownUnitError(f"Unrecognized respiration rate unit: '{unit}'")

    # -------------------------------------------------------------------------
    # 6. Shelf Life (Target: Days)
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_shelf_life(value: float, unit: str) -> ConversionResult:
        if value <= 0:
            raise InvalidMeasurementError(f"Shelf life must be positive, got: {value}")
        clean_unit = unit.strip().lower()
        if clean_unit in ("day", "days", "d"):
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(value, 1),
                normalized_unit="days",
                conversion_method="identity"
            )
        elif clean_unit in ("week", "weeks", "wk", "wks"):
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(value * 7.0, 1),
                normalized_unit="days",
                conversion_method="multiplication: weeks * 7"
            )
        elif clean_unit in ("month", "months", "mo", "mos"):
            # Standard postharvest convention: 1 month = 30 days
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(value * 30.0, 1),
                normalized_unit="days",
                conversion_method="multiplication: months * 30"
            )
        elif clean_unit in ("hour", "hours", "hr", "hrs", "h"):
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(value / 24.0, 2),
                normalized_unit="days",
                conversion_method="division: hours / 24"
            )
        else:
            raise UnknownUnitError(f"Unrecognized shelf-life unit: '{unit}'")

    # -------------------------------------------------------------------------
    # 7. Percentage Normalization (Target: Percentage [0 - 100%])
    # -------------------------------------------------------------------------
    @staticmethod
    def normalize_percentage(value: float, unit: str) -> ConversionResult:
        clean_unit = unit.strip().lower()
        if clean_unit in ("%", "percent", "pct", "percentage"):
            if value < 0.0 or value > 100.0:
                raise InvalidMeasurementError(f"Percentage out of range [0, 100]: {value}")
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(value, 2),
                normalized_unit="%",
                conversion_method="identity"
            )
        elif clean_unit in ("fraction", "ratio", "decimal"):
            if value < 0.0 or value > 1.0:
                raise InvalidMeasurementError(f"Fractional ratio out of range [0, 1]: {value}")
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(value * 100.0, 2),
                normalized_unit="%",
                conversion_method="multiplication: fraction * 100"
            )
        elif clean_unit in ("g/100g", "g/100 g"):
            if value < 0.0 or value > 100.0:
                raise InvalidMeasurementError(f"g/100g out of range [0, 100]: {value}")
            return ConversionResult(
                original_value=value,
                original_unit=unit,
                normalized_value=round(value, 2),
                normalized_unit="%",
                conversion_method="identity: g/100g = %"
            )
        else:
            raise UnknownUnitError(f"Unrecognized percentage unit: '{unit}'")
