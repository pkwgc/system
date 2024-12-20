import os
import subprocess
from datetime import datetime
from flask import current_app
from models import db
from sqlalchemy.sql import text

def create_backup(tables):
    """Create a backup of specified tables"""
    if not tables:
        return False, "No tables selected for backup"

    backup_dir = current_app.config['BACKUP_DIR']
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{backup_dir}/backup_{timestamp}.sql"

    try:
        # Get database connection info from SQLAlchemy
        db_uri = db.engine.url
        cmd = [
            'mysqldump',
            '-h', db_uri.host,
            '-u', db_uri.username,
            f"-p{db_uri.password}",
            db_uri.database,
            *tables
        ]

        with open(backup_file, 'w') as f:
            subprocess.run(cmd, stdout=f, check=True)

        return True, f"Backup created successfully: {backup_file}"
    except Exception as e:
        return False, f"Backup failed: {str(e)}"

def delete_table(table_name):
    """Safely delete a table after creating a backup"""
    # Get user confirmation first
    confirmation = input(f"Are you sure you want to delete table {table_name}? This action cannot be undone. (yes/no): ")
    if confirmation.lower() != 'yes':
        return False, "Table deletion cancelled by user"

    # Create backup first
    success, message = create_backup([table_name])
    if not success:
        return False, f"Failed to create backup before deletion: {message}"

    try:
        # Drop the table using SQLAlchemy
        with db.engine.begin() as conn:
            conn.execute(text(f'DROP TABLE IF EXISTS {table_name}'))
        return True, f"Table {table_name} deleted successfully"
    except Exception as e:
        return False, f"Failed to delete table: {str(e)}"

def get_all_tables():
    """Get list of all tables in database"""
    try:
        inspector = db.inspect(db.engine)
        return inspector.get_table_names()
    except Exception as e:
        return []
