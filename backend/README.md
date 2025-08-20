# ChemCalc Backend API

A FastAPI-based REST API for calculating molar masses of chemical compounds and fetching their physical/chemical properties from PubChem.

## 🚀 Features

- **Molar Mass Calculation**: Calculate molecular weight for chemical formulas
- **Chemical Properties**: Fetch physical and chemical properties from PubChem API
- **Formula History**: Store and manage calculation history with full CRUD operations
- **Error Handling**: Comprehensive validation and error handling
- **Database Support**: MySQL/MariaDB with SQLite fallback
- **CORS Support**: Configurable cross-origin resource sharing
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## 📋 Requirements

- Python 3.8+
- MySQL/MariaDB (recommended) or SQLite (fallback)
- Internet connection (for PubChem API)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd ChemCalc/backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the backend directory:
```env
# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/molar_mass_db
SQLALCHEMY_DATABASE_URL=mysql+pymysql://username:password@localhost:3306/molar_mass_db

# Environment
ENVIRONMENT=development

# Docker (if using Docker)
DOCKER_ENV=false
```

### 5. Database Setup
Make sure your MySQL server is running and create the database:
```sql
CREATE DATABASE molar_mass_db;
```

## 🚀 Running the Application

### Development Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Project Structure

```
backend/
├── api/                    # API endpoints
│   ├── __init__.py
│   └── endpoints.py        # Route definitions
├── core/                   # Core configuration
│   ├── __init__.py
│   └── config.py          # Application settings
├── data/                   # Data access layer
│   ├── __init__.py
│   └── pubchem_api.py     # PubChem API integration
├── models/                 # Data models
│   ├── __init__.py
│   └── schemas.py         # Pydantic schemas
├── services/              # Business logic
│   ├── __init__.py
│   ├── formula_service.py # Formula calculation logic
│   └── history_service.py # History management
├── utils/                 # Utilities
│   ├── __init__.py
│   └── validators.py      # Input validation
├── atomic_masses.json     # Atomic mass data
├── database.py           # Database models and setup
├── main.py              # FastAPI application
└── requirements.txt     # Python dependencies
```

## 🔌 API Endpoints

### Health Check
```http
GET /
```
Returns API status and health information.

### Calculate Molar Mass
```http
POST /molar-mass
Content-Type: application/json

{
    "formula": "H2O"
}
```

**Response:**
```json
{
    "formula": "H2O",
    "molar_mass": 18.015,
    "unit": "g/mol",
    "boiling_point": "100 °C",
    "melting_point": "0 °C",
    "density": "1.000 g/mL",
    "state_at_room_temp": "Liquid",
    "iupac_name": "water",
    "hazard_classification": "Non-hazardous",
    "structure_image_url": "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/962/PNG",
    "structure_image_svg_url": null,
    "compound_url": "https://pubchem.ncbi.nlm.nih.gov/compound/962"
}
```

### Get Calculation History
```http
GET /history?limit=10
```

### Update Formula in History
```http
PUT /history/{formula_id}
Content-Type: application/json

{
    "formula": "CO2"
}
```

### Delete Formula from History
```http
DELETE /history/{formula_id}
```

## 🧪 Supported Chemical Formulas

The API supports standard chemical notation:

- **Simple compounds**: `H2O`, `CO2`, `NaCl`
- **Complex compounds**: `C6H12O6`, `CaCl2`
- **Parentheses**: `Ca(OH)2`, `Al2(SO4)3`
- **Nested parentheses**: `Ca(NO3)2`, `[Cu(NH3)4]SO4`

### Formula Validation Rules
- Elements must start with uppercase letter
- Numbers indicate atom counts
- Parentheses must be balanced
- Only alphanumeric characters and parentheses allowed

## 🗄️ Database Schema

### FormulaHistory Table
```sql
CREATE TABLE formulas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    formula VARCHAR(100) NOT NULL,
    molar_mass FLOAT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_ip VARCHAR(45),
    boiling_point VARCHAR(100),
    melting_point VARCHAR(100),
    density VARCHAR(100),
    state_at_room_temp VARCHAR(50),
    iupac_name VARCHAR(255),
    hazard_classification VARCHAR(255),
    structure_image_url VARCHAR(255),
    structure_image_svg_url VARCHAR(255),
    compound_url VARCHAR(255)
);
```

## 🔧 Configuration

### Core Settings (core/config.py)
- **API_TITLE**: API title for documentation
- **API_DESCRIPTION**: API description
- **CORS_ORIGINS**: Allowed origins for CORS
- **HISTORY_LIMIT_DEFAULT**: Default limit for history queries

### Database Configuration
The application supports multiple database configurations:
- **Production**: Uses DATABASE_URL environment variable
- **Development**: MySQL/MariaDB with connection pooling
- **Fallback**: SQLite for development/testing

### Atomic Mass Data
Atomic masses are loaded from `atomic_masses.json` containing all elements from the periodic table.

## 🚨 Error Handling

### Formula Validation Errors (400)
```json
{
    "detail": "Invalid formula format: XYZ123"
}
```

### Unknown Element Errors (400)
```json
{
    "detail": "Unknown element: Xx"
}
```

### Database Connection Errors (500)
```json
{
    "detail": "An error occurred: Database connection failed"
}
```

### PubChem API Errors
- Non-critical: API continues without properties
- Timeout handling: 10-15 second timeouts
- Fallback: Returns empty properties on failure

## 🐳 Docker Support

### Environment Variables for Docker
```env
DOCKER_ENV=true
DATABASE_URL=mysql+pymysql://root:password@mysql:3306/molar_mass_db
```

### Docker Compose Integration
The application is designed to work with Docker Compose setups where:
- Database service is named `mysql`
- Application connects via service name
- Environment variables control connection strings

## 🔍 Monitoring and Logging

### Database Connection Monitoring
- Connection pool pre-ping validation
- Automatic connection recycling (1 hour)
- Retry logic with exponential backoff
- Detailed error logging for troubleshooting

### PubChem API Monitoring
- Request timeout handling
- Error logging for failed requests
- Graceful degradation when API unavailable

## 🧪 Testing

### Manual Testing
Use the interactive API documentation at `/docs` to test endpoints.

### Example Test Commands
```bash
# Health check
curl http://localhost:8000/

# Calculate molar mass
curl -X POST "http://localhost:8000/molar-mass" \
     -H "Content-Type: application/json" \
     -d '{"formula": "H2O"}'

# Get history
curl http://localhost:8000/history?limit=5
```

## 🚀 Deployment

### Production Deployment
1. Set `ENVIRONMENT=production` in environment variables
2. Use production database with proper credentials
3. Configure proper CORS origins
4. Use production WSGI server like Gunicorn:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Environment-Specific Configuration
- **Development**: Full error details, database auto-creation
- **Production**: Minimal error exposure, robust error handling

## 📝 API Documentation

The API provides comprehensive documentation:
- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`
- **OpenAPI JSON**: Available at `/openapi.json`

## 🤝 Contributing

1. Follow the existing code structure
2. Add proper type hints
3. Include docstrings for new functions
4. Test with various chemical formulas
5. Ensure database operations are non-critical for main functionality

## 📄 License

This project is part of the ChemCalc application suite.

## 🆘 Troubleshooting

### Common Issues

#### Database Connection Failed
```
Error: Could not create database tables: (pymysql.err.OperationalError)
```
**Solutions:**
1. Ensure MySQL server is running
2. Check database credentials
3. Create database manually: `CREATE DATABASE molar_mass_db;`
4. For Docker: Ensure containers can communicate

#### Import Errors
```
ImportError: No module named 'core'
```
**Solutions:**
1. Ensure you're in the backend directory
2. Check that `__init__.py` files exist in all packages
3. Activate virtual environment

#### PubChem API Timeout
```
Warning: Could not fetch properties from PubChem
```
**Solutions:**
1. Check internet connection
2. Verify PubChem service status
3. API will continue without properties (non-critical)

#### Formula Parsing Errors
```
ValueError: Invalid formula format
```
**Solutions:**
1. Check formula syntax (proper capitalization)
2. Ensure balanced parentheses
3. Use standard chemical notation

For additional support, check the application logs and error messages for specific troubleshooting guidance.
