import pytest
from app.core.units import UnitConverter, UnknownUnitError, InvalidMeasurementError


def test_temperature_normalization():
    # Celsius identity
    c_res = UnitConverter.normalize_temperature(4.0, "°C")
    assert c_res.normalized_value == 4.0
    assert c_res.normalized_unit == "°C"

    # Fahrenheit to Celsius: (68 - 32) * 5/9 = 20.0
    f_res = UnitConverter.normalize_temperature(68.0, "°F")
    assert f_res.normalized_value == 20.0
    assert f_res.normalized_unit == "°C"

    # Freezing: 32°F = 0°C
    f_zero = UnitConverter.normalize_temperature(32.0, "F")
    assert f_zero.normalized_value == 0.0

    # Kelvin to Celsius: 273.15 K = 0°C
    k_res = UnitConverter.normalize_temperature(293.15, "K")
    assert k_res.normalized_value == 20.0

    # Negative Kelvin impossible
    with pytest.raises(InvalidMeasurementError):
        UnitConverter.normalize_temperature(-5.0, "K")

    # Unknown unit
    with pytest.raises(UnknownUnitError):
        UnitConverter.normalize_temperature(100.0, "Rankine")


def test_thickness_normalization():
    # Microns identity
    um_res = UnitConverter.normalize_thickness(25.0, "µm")
    assert um_res.normalized_value == 25.0

    # Mil to Microns: 1 mil = 25.4 µm
    mil_res = UnitConverter.normalize_thickness(1.0, "mil")
    assert mil_res.normalized_value == 25.4

    # 2 mil = 50.8 µm
    mil_res2 = UnitConverter.normalize_thickness(2.0, "mils")
    assert mil_res2.normalized_value == 50.8

    # mm to Microns: 0.03 mm = 30.0 µm
    mm_res = UnitConverter.normalize_thickness(0.03, "mm")
    assert mm_res.normalized_value == 30.0

    # Non-positive thickness
    with pytest.raises(InvalidMeasurementError):
        UnitConverter.normalize_thickness(0.0, "µm")
    with pytest.raises(InvalidMeasurementError):
        UnitConverter.normalize_thickness(-10.0, "mil")

    # Unknown unit
    with pytest.raises(UnknownUnitError):
        UnitConverter.normalize_thickness(5.0, "cubits")


def test_otr_normalization():
    # Standard cc/(m²·day·atm) identity
    std = UnitConverter.normalize_otr(1500.0, "cc/(m2*day*atm)")
    assert std.normalized_value == 1500.0
    assert std.normalized_unit == "cc/(m²·day·atm)"

    # Pressure unit bar to atm: 1000 * 1.01325 = 1013.25
    bar_res = UnitConverter.normalize_otr(1000.0, "cm3/(m2*day*bar)")
    assert bar_res.normalized_value == 1013.25

    # Area unit 100 in² to m²: 10 * 15.500031 = 155.0
    in_res = UnitConverter.normalize_otr(10.0, "cc/(100in2*day*atm)")
    assert abs(in_res.normalized_value - 155.0) < 0.1

    # Negative OTR
    with pytest.raises(InvalidMeasurementError):
        UnitConverter.normalize_otr(-100.0, "cc/(m2*day*atm)")

    # Unknown unit
    with pytest.raises(UnknownUnitError):
        UnitConverter.normalize_otr(50.0, "liters/minute")


def test_wvtr_normalization():
    # Standard g/(m²·day) identity
    std = UnitConverter.normalize_wvtr(4.5, "g/(m2*day)")
    assert std.normalized_value == 4.5
    assert std.normalized_unit == "g/(m²·day)"

    # US Customary 100 in² to m²
    us_res = UnitConverter.normalize_wvtr(0.5, "g/(100in2*day)")
    assert abs(us_res.normalized_value - 7.75) < 0.1

    # mg to g
    mg_res = UnitConverter.normalize_wvtr(2500.0, "mg/(m2*day)")
    assert mg_res.normalized_value == 2.5

    # Negative WVTR
    with pytest.raises(InvalidMeasurementError):
        UnitConverter.normalize_wvtr(-2.0, "g/(m2*day)")

    # Unknown unit
    with pytest.raises(UnknownUnitError):
        UnitConverter.normalize_wvtr(1.0, "slugs/acre")


def test_respiration_rate_normalization():
    # Standard mg CO2/(kg·hr) identity
    std = UnitConverter.normalize_respiration_rate(22.0, "mg CO2/(kg*hr)")
    assert std.normalized_value == 22.0

    # Volume mL CO2/(kg·hr) to mg via ideal gas density
    # At 0°C, density of CO2 ~ 1.9635 mg/mL => 10 mL = ~19.64 mg
    vol_res = UnitConverter.normalize_respiration_rate(10.0, "mL CO2/(kg*hr)", temperature_c=0.0)
    assert abs(vol_res.normalized_value - 19.64) < 0.1

    # At 20°C, density ~ 1.8295 mg/mL => 10 mL = ~18.3 mg
    vol_res2 = UnitConverter.normalize_respiration_rate(10.0, "mL CO2/(kg*hr)", temperature_c=20.0)
    assert abs(vol_res2.normalized_value - 18.3) < 0.1

    # Unknown unit
    with pytest.raises(UnknownUnitError):
        UnitConverter.normalize_respiration_rate(5.0, "furlongs/fortnight")


def test_shelf_life_normalization():
    # Days identity
    d = UnitConverter.normalize_shelf_life(14.0, "days")
    assert d.normalized_value == 14.0

    # Weeks to days
    w = UnitConverter.normalize_shelf_life(2.0, "weeks")
    assert w.normalized_value == 14.0

    # Months to days
    m = UnitConverter.normalize_shelf_life(3.0, "months")
    assert m.normalized_value == 90.0

    # Hours to days
    h = UnitConverter.normalize_shelf_life(48.0, "hours")
    assert h.normalized_value == 2.0

    # Negative shelf life
    with pytest.raises(InvalidMeasurementError):
        UnitConverter.normalize_shelf_life(-1.0, "days")

    # Unknown unit
    with pytest.raises(UnknownUnitError):
        UnitConverter.normalize_shelf_life(10.0, "lightyears")


def test_percentage_normalization():
    # Percentage identity
    p = UnitConverter.normalize_percentage(85.5, "%")
    assert p.normalized_value == 85.5

    # Fraction ratio to %
    f = UnitConverter.normalize_percentage(0.85, "fraction")
    assert f.normalized_value == 85.0

    # Out of range
    with pytest.raises(InvalidMeasurementError):
        UnitConverter.normalize_percentage(150.0, "%")
    with pytest.raises(InvalidMeasurementError):
        UnitConverter.normalize_percentage(1.5, "fraction")
    with pytest.raises(UnknownUnitError):
        UnitConverter.normalize_percentage(50.0, "parts_per_billion")
