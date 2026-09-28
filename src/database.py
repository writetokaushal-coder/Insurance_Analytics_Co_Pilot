import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine


# Load .env file
load_dotenv()


# Get values from .env
SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")


# Create connection string
connection_string = quote_plus(
    f"DRIVER={{{SQL_DRIVER}}};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={SQL_DATABASE};"
    f"Trusted_Connection=yes;"
    f"TrustServerCertificate=yes;"
)


# Create database engine
engine = create_engine(
    f"mssql+pyodbc:///?odbc_connect={connection_string}",
    pool_pre_ping=True
)