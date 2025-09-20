#!/usr/bin/env python3
"""Initialize the database with tables"""

from app.database.database import engine, Base
from app.database import models

def create_tables():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    create_tables()