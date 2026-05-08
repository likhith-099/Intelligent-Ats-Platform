#!/usr/bin/env python3
"""
Script to add missing column 'original_filename' to resumes table.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine
from sqlalchemy import text

def add_column():
    """Add original_filename column to resumes table if it doesn't exist."""
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'resumes' AND column_name = 'original_filename'
        """))
        if result.fetchone():
            print("Column 'original_filename' already exists.")
            return
        
        # Add column
        conn.execute(text("""
            ALTER TABLE resumes 
            ADD COLUMN original_filename VARCHAR NOT NULL DEFAULT ''
        """))
        conn.commit()
        print("Column 'original_filename' added successfully.")
        
        # Update existing rows: set original_filename = filename (best guess)
        conn.execute(text("""
            UPDATE resumes 
            SET original_filename = filename 
            WHERE original_filename = ''
        """))
        conn.commit()
        print("Updated existing rows with filename as original_filename.")

if __name__ == "__main__":
    add_column()