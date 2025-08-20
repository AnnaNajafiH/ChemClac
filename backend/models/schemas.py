from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FormulaRequest(BaseModel):
    """Request model for formula calculation."""
    formula: str


class FormulaResponse(BaseModel):
    """Response model for formula calculation with physical properties."""
    formula: str
    molar_mass: float
    unit: str
    boiling_point: Optional[str] = None  #none by default, when bp is not available
    melting_point: Optional[str] = None  #Optional[str] gives flexibility:"100°C", with float it would be "100"
    density: Optional[str] = None
    state_at_room_temp: Optional[str] = None
    iupac_name: Optional[str] = None
    hazard_classification: Optional[str] = None
    structure_image_url: Optional[str] = None
    structure_image_svg_url: Optional[str] = None
    compund_url: Optional[str] = None


class FormulaHistoryModel(BaseModel):
    """Model for formula history data"""
    id: int
    formula: str
    molar_mass: float
    timestamp: datetime
    boiling_point: Optional[str] = None
    melting_point: Optional[str] = None
    density: Optional[str] = None
    state_at_room_temp: Optional[str] = None
    iupac_name: Optional[str] = None
    hazard_classification: Optional[str] = None
    structure_image_url: Optional[str] = None
    structure_image_svg_url: Optional[str] = None
    compund_url: Optional[str] = None


    class Config:
        """Pydantic configuration to allow ORM mode."""
        orm_mode = True
