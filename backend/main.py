import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import router
from core import settings
from database import create_tables


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_CREDENTIALS,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
    
    # Include API routes
    app.include_router(router)
    
    return app


# Initialize FastAPI app
app = create_app()


@app.on_event("startup")
def startup_db_client():
    """
    Initialize database tables on application startup.
    Provides helpful troubleshooting information in non-production environments.
    """
    try:
        create_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Warning: Could not create database tables: {str(e)}")
        print("The API will still work without database functionality")
        
        # When running locally, provide more helpful error messages
        if not os.environ.get('ENVIRONMENT') == 'production':
            if 'mysql' in str(e):
                print("\nTROUBLESHOOTING TIPS:")
                print("1. Make sure MySQL is running locally")
                print("2. Check that you can connect to MySQL with the credentials in your connection string")
                print("3. If you're using Docker, make sure the MySQL container is running")
                print("4. If you're running the app locally outside Docker but trying to connect to MySQL in Docker,")
                print("   update your connection string to use 'localhost' instead of 'mysql'")
                print("5. Try manually creating the database: CREATE DATABASE molar_mass_db;\n")