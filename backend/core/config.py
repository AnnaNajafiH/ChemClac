import json
import os
from typing import Dict


class Settings:
    """Application settings and configuration"""
    
    # API Configuration
    API_TITLE: str = "Molar Mass Calculator API"
    API_DESCRIPTION: str = "API for calculating molar mass of chemical compounds"
    
    # CORS Configuration
    CORS_ORIGINS: list = ["*"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # Database Configuration
    HISTORY_LIMIT_DEFAULT: int = 10
    
    def __init__(self):
        self.atomic_masses = self._load_atomic_masses()
    
    def _load_atomic_masses(self) -> Dict[str, float]:
        """Load atomic mass data from JSON file"""
        try:
            with open("./atomic_masses.json") as file:
                return json.load(file)
        except FileNotFoundError:
            # Fallback to direct path if running from different directory
            with open("atomic_masses.json") as file:
                return json.load(file)


# Global settings instance
settings = Settings()