from datetime import datetime
from typing import Dict, Optional
from fastapi import Request
from sqlalchemy.orm import Session

from database import FormulaHistory
from .formula_service import calculate_molar_mass
from utils import validate_formula


def save_to_database(
    db: Session, 
    formula: str, 
    molar_mass: float, 
    properties: Dict, 
    req: Optional[Request] = None
) -> None:
    try:
        client_ip = req.client.host if req else None
        db_formula = FormulaHistory(
            formula=formula,
            molar_mass=round(molar_mass, 4),
            user_ip=client_ip,
            boiling_point=properties.get("boiling_point"),
            melting_point=properties.get("melting_point"),
            density=properties.get("density"),
            state_at_room_temp=properties.get("state_at_room_temp"),
            iupac_name=properties.get("iupac_name"),
            hazard_classification=properties.get("hazard_classification"),
            structure_image_url=properties.get("structure_image_url"),
            structure_image_svg_url=properties.get("structure_image_svg_url"),
            compound_url=properties.get("compound_url")
        )
        db.add(db_formula)
        db.commit()
    except Exception as db_error:
        print(f"Database error (non-critical): {str(db_error)}")


def update_formula_in_history(db: Session, formula_id: int, new_formula: str) -> FormulaHistory:
    # Find the formula by ID
    db_formula = db.query(FormulaHistory).filter(FormulaHistory.id == formula_id).first()
    if not db_formula:
        raise Exception(f"Formula with ID {formula_id} not found")
    
    # Validate and calculate new molar mass
    validate_formula(new_formula)
    molar_mass = calculate_molar_mass(new_formula)
    
    # Update the formula
    db_formula.formula = new_formula
    db_formula.molar_mass = round(molar_mass, 4)
    db_formula.timestamp = datetime.now()  # Update timestamp to current time
    
    db.commit()
    db.refresh(db_formula)
    
    return db_formula


def delete_formula_from_history(db: Session, formula_id: int) -> Dict[str, str]:
    # Find the formula by ID
    db_formula = db.query(FormulaHistory).filter(FormulaHistory.id == formula_id).first()
    if not db_formula:
        raise Exception(f"Formula with ID {formula_id} not found")
    
    # Delete the formula
    db.delete(db_formula)
    db.commit()
    
    return {"message": f"Formula with ID {formula_id} deleted successfully"}