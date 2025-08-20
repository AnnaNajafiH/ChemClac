from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, func, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from datetime import datetime
from dotenv import load_dotenv
import os
import re
import time


# Load environment variables from .env file
load_dotenv()

# Database connection handling with support for Render
database_url = os.getenv("DATABASE_URL", "")

# If we're on Render, we need to modify the connection string
if database_url:
    # First, check if the string already contains the dialect+driver format
    if 'mysql+pymysql://' in database_url:
        # Already in the correct format, don't modify
        pass
    # Handle both mysql:// and postgres:// connection strings (Render might use either)
    elif 'mysql://' in database_url:
        # Convert mysql:// to mysql+pymysql:// for SQLAlchemy
        database_url = database_url.replace('mysql://', 'mysql+pymysql://')
    elif 'postgres://' in database_url:
        # Convert postgres:// to postgresql:// for SQLAlchemy
        database_url = database_url.replace('postgres://', 'postgresql://')

# Check if we're running in Docker development environment
# In Docker, we need to use the service name 'mysql' instead of 'localhost'
is_docker = os.environ.get('DOCKER_ENV') == 'true'
default_host = 'mysql' if is_docker else 'localhost'

# If we're running locally and DATABASE_URL is trying to connect to 'mysql',
# we should change it to 'localhost'
if database_url and 'mysql' in database_url and not is_docker:
    if '@mysql:' in database_url:
        database_url = database_url.replace('@mysql:', '@localhost:')

# Use the converted URL or fall back to default
SQLALCHEMY_DATABASE_URL = database_url or os.getenv(
    "SQLALCHEMY_DATABASE_URL",
    f"mysql+pymysql://root:root@{default_host}:3306/molar_mass_db"
)

# Debug: Print out connection details but mask the password
masked_url = SQLALCHEMY_DATABASE_URL
if '@' in masked_url:
    # Simple string manipulation to mask password
    parts = masked_url.split('@')
    prefix_parts = parts[0].split(':')
    if len(prefix_parts) > 2:
        # Has username and password
        masked_url = prefix_parts[0] + ':' + prefix_parts[1] + ':******@' + parts[1]

print(f"Connecting to database with: {masked_url}")

# Create SQLAlchemy engine with proper error handling
try:
    # First, validate the URL to make sure it's properly formatted
    if '+' in SQLALCHEMY_DATABASE_URL:
        # Count the number of '+' characters before the '://'
        prefix = SQLALCHEMY_DATABASE_URL.split('://')[0]
        if prefix.count('+') > 1:
            # Too many '+' characters, fix it by using just the correct driver format
            if 'mysql' in prefix:
                SQLALCHEMY_DATABASE_URL = re.sub(r'mysql(\+[^+]+)+://', 'mysql+pymysql://', SQLALCHEMY_DATABASE_URL)
            elif 'postgres' in prefix:
                SQLALCHEMY_DATABASE_URL = re.sub(r'postgres(\+[^+]+)+://', 'postgresql+psycopg2://', SQLALCHEMY_DATABASE_URL)
            
            # Mask password in connection string for logging
            masked_url = SQLALCHEMY_DATABASE_URL
            if '@' in masked_url:
                parts = masked_url.split('@')
                prefix_parts = parts[0].split(':')
                if len(prefix_parts) > 2:
                    # Has username and password
                    masked_url = prefix_parts[0] + ':' + prefix_parts[1] + ':******@' + parts[1]
            
            print(f"Fixed malformed connection string. New connection string: {masked_url}")
    
    # Add connection pooling and retry options for better reliability in cloud environments
    connect_args = {}
    if 'mysql' in SQLALCHEMY_DATABASE_URL:
        connect_args = {"connect_timeout": 15}  # MySQL specific timeout
        
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,  # Verify connection is active before using it
        pool_recycle=3600,   # Recycle connections after 1 hour
        connect_args=connect_args
    )
except Exception as e:
    print(f"Error creating database engine: {str(e)}")
    print(f"Attempting to create engine with basic configuration")
    # Fall back to a simpler configuration if the advanced one fails
    try:
        engine = create_engine(SQLALCHEMY_DATABASE_URL)
    except Exception as e2:
        print(f"Second attempt failed: {str(e2)}")
        # Last resort - try with a local SQLite database
        print("Falling back to SQLite database")
        engine = create_engine('sqlite:///./fallback.db')

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

# Formula history model
class FormulaHistory(Base):
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

# Function to create all tables
def create_tables():
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Extract database name for potential creation
            db_name = None
            if 'mysql+pymysql' in SQLALCHEMY_DATABASE_URL:
                # Use regex to extract the database name more reliably
                match = re.search(r'\/([^\/\?]+)(\?|$)', SQLALCHEMY_DATABASE_URL)
                if match:
                    db_name = match.group(1)
            
            # Try to create the database if we could extract a name
            if db_name:
                try:
                    # Create a base URL without the database name
                    base_url = re.sub(r'\/[^\/\?]+(\?|$)', '/', SQLALCHEMY_DATABASE_URL)
                    # Create temporary engine to connect to the server without a specific DB
                    temp_engine = create_engine(base_url, isolation_level="AUTOCOMMIT")
                    with temp_engine.connect() as conn:
                        # Use proper SQL execution with SQLAlchemy text()
                        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
                    temp_engine.dispose()
                except SQLAlchemyError as db_err:
                    print(f"Could not create database (this is often normal): {str(db_err)}")
            
            # Now create the tables
            Base.metadata.create_all(bind=engine)
            print(f"Database tables created successfully using connection: {SQLALCHEMY_DATABASE_URL}")
            return
            
        except OperationalError as oe:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Failed to create database tables after {max_retries} attempts: {str(oe)}")
                if os.getenv("ENVIRONMENT") != "production":
                    raise
                return
            
            # Wait with exponential backoff before retrying
            wait_time = 2 ** retry_count
            print(f"Database connection failed. Retrying in {wait_time} seconds... (Attempt {retry_count}/{max_retries})")
            time.sleep(wait_time)
            
        except Exception as e:
            print(f"Failed to create database tables: {str(e)}")
            print(f"Connection string used: {SQLALCHEMY_DATABASE_URL}")
            print("Please check your database connection settings and ensure the database is running")
            
            # Don't raise the exception in production to allow the API to start anyway
            if os.getenv("ENVIRONMENT") != "production":
                raise
            return

# Function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
