from enum import Enum
import sqlalchemy as sa

from eloverblik.db import ModelBase


class MeteringPointType(Enum):
    production = 'E18'
    consumption = 'E17'


class MeteringPoint(ModelBase):
    __tablename__ = 'meteringpoint'
    __table_args__ = (
        sa.UniqueConstraint('gsrn'),
    )

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    created = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    subject = sa.Column(sa.String(), index=True, nullable=False)
    gsrn = sa.Column(sa.String(), index=True, nullable=False)
    type = sa.Column(sa.Enum(MeteringPointType), nullable=False)
    technology_code = sa.Column(sa.String(), nullable=False)
    fuel_code = sa.Column(sa.String(), nullable=False)
    street_code = sa.Column(sa.String())
    street_name = sa.Column(sa.String())
    building_number = sa.Column(sa.String())
    city_name = sa.Column(sa.String())
    postcode = sa.Column(sa.String())
    municipality_code = sa.Column(sa.String())


VERSIONED_DB_MODELS = (
    MeteringPoint,
)
