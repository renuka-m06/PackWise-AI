"""initial_schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-09-26 23:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. commodities table
    op.create_table(
        'commodities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(120), nullable=False, unique=True),
        sa.Column('scientific_name', sa.String(150), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('respiration_rate_mg_co2_kg_hr', sa.Numeric(8, 2), nullable=True),
        sa.Column('optimal_temperature_min_c', sa.Numeric(4, 1), nullable=False, server_default='4.0'),
        sa.Column('optimal_temperature_max_c', sa.Numeric(4, 1), nullable=False, server_default='8.0'),
        sa.Column('optimal_rh_min_percent', sa.Numeric(5, 2), nullable=False, server_default='85.0'),
        sa.Column('optimal_rh_max_percent', sa.Numeric(5, 2), nullable=False, server_default='95.0'),
        sa.Column('water_activity_aw', sa.Numeric(4, 3), nullable=True),
        sa.Column('moisture_sensitive', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('oxygen_sensitive', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('ethylene_sensitive', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('light_sensitive', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('target_shelf_life_unpacked_days', sa.Integer(), nullable=True)
    )
    op.create_index('ix_commodities_name', 'commodities', ['name'])
    op.create_index('ix_commodities_category', 'commodities', ['category'])

    # 2. materials table
    op.create_table(
        'materials',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('name', sa.String(150), nullable=False, unique=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('polymer_type', sa.String(60), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('thickness_micron', sa.Numeric(6, 2), nullable=False, server_default='25.0'),
        sa.Column('otr_cc_m2_day_atm', sa.Numeric(10, 3), nullable=False),
        sa.Column('wvtr_g_m2_day', sa.Numeric(10, 3), nullable=False),
        sa.Column('tensile_strength_mpa', sa.Numeric(6, 2), nullable=True),
        sa.Column('seal_strength_n_15mm', sa.Numeric(6, 2), nullable=True),
        sa.Column('transparency_pct', sa.Numeric(5, 2), nullable=True),
        sa.Column('is_biodegradable', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('biodegradation_standard', sa.String(80), nullable=True),
        sa.Column('recyclability_code', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('cost_index_relative', sa.Numeric(5, 2), nullable=False, server_default='1.0'),
        sa.Column('carbon_footprint_kg_co2_per_kg', sa.Numeric(6, 3), nullable=True),
        sa.Column('food_contact_certified', sa.Boolean(), nullable=False, server_default='true')
    )
    op.create_index('ix_materials_name', 'materials', ['name'])
    op.create_index('ix_materials_code', 'materials', ['code'])
    op.create_index('ix_materials_polymer_type', 'materials', ['polymer_type'])

    # 3. map_compositions table
    op.create_table(
        'map_compositions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('composition_name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('oxygen_pct', sa.Numeric(5, 2), nullable=False),
        sa.Column('carbon_dioxide_pct', sa.Numeric(5, 2), nullable=False),
        sa.Column('nitrogen_pct', sa.Numeric(5, 2), nullable=False),
        sa.Column('target_application', sa.String(150), nullable=True)
    )
    op.create_index('ix_map_compositions_name', 'map_compositions', ['composition_name'])

    # 4. storage_conditions table
    op.create_table(
        'storage_conditions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('condition_profile_name', sa.String(100), nullable=False, unique=True),
        sa.Column('temperature_c', sa.Numeric(5, 2), nullable=False),
        sa.Column('relative_humidity_pct', sa.Numeric(5, 2), nullable=False),
        sa.Column('target_shelf_life_days', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('cold_chain_type', sa.String(50), nullable=False, server_default='STRICT_COLD_CHAIN')
    )

    # 5. recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('commodity_name_input', sa.String(120), nullable=False),
        sa.Column('matched_commodity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('commodities.id', ondelete='SET NULL'), nullable=True),
        sa.Column('recommended_material_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('materials.id', ondelete='SET NULL'), nullable=True),
        sa.Column('suggested_map_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('map_compositions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('request_payload', sa.JSON(), nullable=False),
        sa.Column('rule_filtering_summary', sa.JSON(), nullable=True),
        sa.Column('topsis_scores', sa.JSON(), nullable=True),
        sa.Column('engine_version', sa.String(50), nullable=False, server_default='M0-foundation'),
        sa.Column('user_feedback', sa.String(50), nullable=True),
        sa.Column('feedback_notes', sa.String(500), nullable=True)
    )


def downgrade() -> None:
    op.drop_table('recommendations')
    op.drop_table('storage_conditions')
    op.drop_table('map_compositions')
    op.drop_table('materials')
    op.drop_table('commodities')
