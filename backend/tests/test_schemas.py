import pytest
from pydantic import ValidationError
from app.schemas.commodity import CommodityBase
from app.schemas.material import PackagingMaterialBase
from app.schemas.map_composition import MAPCompositionBase
from app.schemas.storage_condition import StorageConditionBase, ColdChainRegime


def test_commodity_schema_validation():
    commodity = CommodityBase(
        name="Apple",
        category="FRUIT",
        respiration_rate_mg_co2_kg_hr=12.5,
        optimal_temperature_min_c=0.0,
        optimal_temperature_max_c=4.0
    )
    assert commodity.name == "Apple"
    assert commodity.optimal_temperature_max_c == 4.0


def test_material_schema_validation():
    material = PackagingMaterialBase(
        name="Oriented Polypropylene (OPP)",
        code="OPP-30",
        polymer_type="PP",
        thickness_micron=30.0,
        otr_cc_m2_day_atm=1500.0,
        wvtr_g_m2_day=5.5
    )
    assert material.code == "OPP-30"
    assert material.food_contact_certified is True


def test_map_composition_gas_sum_validation():
    # Valid gas mixture: 5% O2, 10% CO2, 85% N2 = 100%
    valid_map = MAPCompositionBase(
        composition_name="Fresh Berry MAP",
        oxygen_pct=5.0,
        carbon_dioxide_pct=10.0,
        nitrogen_pct=85.0
    )
    assert valid_map.nitrogen_pct == 85.0

    # Invalid gas mixture (sums to 50%) -> must raise ValidationError
    with pytest.raises(ValidationError):
        MAPCompositionBase(
            composition_name="Invalid Gas Mix",
            oxygen_pct=10.0,
            carbon_dioxide_pct=10.0,
            nitrogen_pct=30.0
        )


def test_storage_condition_validation():
    condition = StorageConditionBase(
        storage_temperature_c=4.0,
        ambient_rh_percent=90.0,
        target_shelf_life_days=14,
        cold_chain_reliability=ColdChainRegime.STRICT_COLD_CHAIN
    )
    assert condition.target_shelf_life_days == 14
