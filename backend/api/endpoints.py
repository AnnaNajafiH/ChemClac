from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import FormulaHistory, get_db
from models.schemas import FormulaRequest, FormulaResponse, FormulaHistoryModel
from services.formula_service import calculate_molar_mass
from services.history_service import (
    save_to_database, 
    update_formula_in_history, 
    delete_formula_from_history
)
from backend.services.pubchem_service import get_chemical_properties
from core.config import settings

router = APIRouter()

#=========================================================================
#=========================================================================

@router.post("/molar-mass", response_model=FormulaResponse)
def get_molar_mass(request: FormulaRequest, db: Session = Depends(get_db), req: Request = None):
    """Calculate molar mass and fetch chemical properties for a given formula."""
    try:
        # Calculate molar mass
        molar_mass = calculate_molar_mass(request.formula)
        
        # Fetch physical/chemical properties from PubChem API
        properties = get_chemical_properties(request.formula)
        
        # Create result with properties (use values from API if available)
        result = {
            "formula": request.formula,
            "molar_mass": round(molar_mass, 4),
            "unit": "g/mol",
            "boiling_point": properties.get("boiling_point"),
            "melting_point": properties.get("melting_point"),
            "density": properties.get("density"),
            "state_at_room_temp": properties.get("state_at_room_temp"),
            "iupac_name": properties.get("iupac_name"),
            "hazard_classification": properties.get("hazard_classification"),
            "structure_image_url": properties.get("structure_image_url"),
            "structure_image_svg_url": properties.get("structure_image_svg_url"),
            "compound_url": properties.get("compound_url")
        }
        
        # Save to database (non-critical operation)
        save_to_database(db, request.formula, molar_mass, properties, req)
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

#=========================================================================
#=========================================================================

@router.get("/history", response_model=List[FormulaHistoryModel])
def get_history(limit: int = settings.HISTORY_LIMIT_DEFAULT, db: Session = Depends(get_db)):
    """Get formula calculation history."""
    formulas = db.query(FormulaHistory).order_by(FormulaHistory.timestamp.desc()).limit(limit).all()
    return formulas

#=========================================================================
#=========================================================================

@router.put("/history/{formula_id}", response_model=FormulaHistoryModel)
def update_formula(formula_id: int, request: FormulaRequest, db: Session = Depends(get_db)):
    """Update a formula in the history."""
    try:
        return update_formula_in_history(db, formula_id, request.formula)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating formula: {str(e)}")

#=========================================================================
#=========================================================================

@router.delete("/history/{formula_id}")
def delete_formula(formula_id: int, db: Session = Depends(get_db)):
    """Delete a formula from the history."""
    try:
        return delete_formula_from_history(db, formula_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting formula: {str(e)}")

#=========================================================================
#=========================================================================

@router.get("/")
def health_check():
    """Health check endpoint."""
    return {"status": "alive", "message": "Molar Mass Calculator API is running"}