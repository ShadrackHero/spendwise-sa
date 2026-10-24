
import sys
import pandas as pd
import pdfplumber
import sqlalchemy
import psycopg

print("SpendWise SA - Environment Test")
print("-" * 40)

print("Python:", sys.version.split()[0])
print("Pandas:", pd.__version__)
print("SQLAlchemy:", sqlalchemy.__version__)
print("Psycopg:", psycopg.__version__)

print("-" * 40)
print("All packages imported successfully!")
