import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.commodity import Commodity
from app.models.material import PackagingMaterial
from app.models.map_composition import MAPComposition
from app.models.storage_condition import StorageCondition
from database.seeds.seed_m1_data import seed_database


@pytest.fixture
def in_memory_db():
    """Provides a fresh isolated in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_seed_database_execution_and_idempotency(in_memory_db):
    # First seed run
    run1 = seed_database(in_memory_db)
    assert len(run1["errors"]) == 0
    assert run1["commodities_inserted"] > 0
    assert run1["materials_inserted"] == 15
    assert run1["map_inserted"] == 10
    assert run1["storage_inserted"] == 5

    # Check total rows in database after first run
    comm_count_1 = len(in_memory_db.scalars(select(Commodity)).all())
    mat_count_1 = len(in_memory_db.scalars(select(PackagingMaterial)).all())
    map_count_1 = len(in_memory_db.scalars(select(MAPComposition)).all())
    storage_count_1 = len(in_memory_db.scalars(select(StorageCondition)).all())

    assert mat_count_1 == 15
    assert map_count_1 == 10

    # Second seed run (must be completely idempotent: 0 inserted, only updated)
    run2 = seed_database(in_memory_db)
    assert len(run2["errors"]) == 0
    assert run2["commodities_inserted"] == 0
    assert run2["materials_inserted"] == 0
    assert run2["map_inserted"] == 0
    assert run2["storage_inserted"] == 0
    assert run2["materials_updated"] == 15
    assert run2["map_updated"] == 10

    # Row counts must remain strictly identical
    comm_count_2 = len(in_memory_db.scalars(select(Commodity)).all())
    mat_count_2 = len(in_memory_db.scalars(select(PackagingMaterial)).all())
    map_count_2 = len(in_memory_db.scalars(select(MAPComposition)).all())
    storage_count_2 = len(in_memory_db.scalars(select(StorageCondition)).all())

    assert comm_count_1 == comm_count_2
    assert mat_count_1 == mat_count_2
    assert map_count_1 == map_count_2
    assert storage_count_1 == storage_count_2


def test_seeded_records_preserve_provenance(in_memory_db):
    seed_database(in_memory_db)

    # Check strawberry commodity
    strawberry = in_memory_db.scalars(select(Commodity).where(Commodity.name == "Strawberry")).first()
    assert strawberry is not None
    assert "SRC-FOOD-001" in strawberry.description
    assert strawberry.respiration_rate_mg_co2_kg_hr > 0
    assert strawberry.optimal_temperature_min_c == 0.0

    # Check PLA packaging material
    pla = in_memory_db.scalars(select(PackagingMaterial).where(PackagingMaterial.code == "PLA-25")).first()
    assert pla is not None
    assert "SRC-PKG-003" in pla.description
    assert pla.is_biodegradable is True
    assert pla.otr_cc_m2_day_atm == 550.0
    assert pla.wvtr_g_m2_day == 175.0

    # Check berry MAP composition
    berry_map = in_memory_db.scalars(select(MAPComposition).where(MAPComposition.composition_name == "High CO2 Fresh Berry MAP")).first()
    assert berry_map is not None
    assert "SRC-MAP-001" in berry_map.description
    assert berry_map.oxygen_pct == 4.0
    assert berry_map.carbon_dioxide_pct == 12.0
    assert berry_map.nitrogen_pct == 84.0
