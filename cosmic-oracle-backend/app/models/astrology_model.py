from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from app.core.database import Base, engine

class BirthProfile(Base):
    """
    Stores the INPUT data required to calculate a chart.
    This is the "source of truth" for a person's chart.
    """
    __tablename__ = 'birth_profiles'

    id = Column(Integer, primary_key=True, index=True)
    profile_name = Column(String, nullable=False, index=True)
    birth_datetime_utc = Column(DateTime, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation_m = Column(Float, nullable=False, default=0.0)
    city_name = Column(String, nullable=True)

    natal_chart = relationship("NatalChart", back_populates="birth_profile", uselist=False, cascade="all, delete-orphan")

class NatalChart(Base):
    """
    Stores the final OUTPUT of a calculated natal chart.
    This acts as a cache to avoid expensive recalculations.
    """
    __tablename__ = 'natal_charts'
    
    id = Column(Integer, primary_key=True, index=True)
    birth_profile_id = Column(Integer, ForeignKey('birth_profiles.id'), unique=True, nullable=False)
    
    # Store the entire complex chart dictionary as a JSON object.
    chart_data = Column(JSONB if 'postgresql' in engine.url.drivername else JSON, nullable=False)

    birth_profile = relationship("BirthProfile", back_populates="natal_chart")