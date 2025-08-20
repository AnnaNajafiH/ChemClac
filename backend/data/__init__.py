"""
Data package for ChemCalc backend.
Contains database models, PubChem API integration, and data access layers.
"""
from .pubchem_api import get_chemical_properties

__all__ = [
    "get_chemical_properties"
]