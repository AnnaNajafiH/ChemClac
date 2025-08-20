#this is database for SQLalchemy models
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from data.database import Base


class FormulaHistory(Base):
    """SQLAlchemy model for formula history."""
    __tablename__ = "formulas"

    id = Column(Integer, primary_key=True, index=True)
    formula = Column(String(100), index=True)
    molar_mass = Column(Float)
    timestamp = Column(DateTime, default=func.now())
    user_ip = Column(String(45), nullable=True)  # IPv6 addresses can be long
    boiling_point = Column(String(100), nullable=True)
    melting_point = Column(String(100), nullable=True)
    density = Column(String(100), nullable=True)
    state_at_room_temp = Column(String(50), nullable=True)
    iupac_name = Column(String(255), nullable=True)
    hazard_classification = Column(String(255), nullable=True)
    structure_image_url = Column(String(255), nullable=True)
    structure_image_svg_url = Column(String(255), nullable=True)
    compound_url = Column(String(255), nullable=True)