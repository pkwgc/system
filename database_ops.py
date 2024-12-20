import os
import subprocess
from datetime import datetime
from flask import current_app
from models import db

def create_backup(tables):
    """Create a backup of specified tables"""
    if not tables:
        return False, "No tables selected for backup"

    backup_dir = current_app.config['BACKUP_DIR']
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{backup_dir}/backup_{timestamp}.sql"

    try:
        tables_str = ' '.join(tables)
        cmd = [
            'mysqldump',
            '-h', current_app.config['DB_HOST'],
            '-u', current_app.config['DB_USER'],
            f"-p{current_app.config['DB_PASS']}",
            current_app.config['DB_NAME'],
            *tables
        ]

        with open(backup_file, 'w') as f:
            subprocess.run(cmd, stdout=f, check=True)

        return True, f"Backup created successfully: {backup_file}"
    except Exception as e:
        return False, f"Backup failed: {str(e)}"

def delete_table(table_name):
    """Safely delete a table after creating a backup"""
    # Create backup first
    success, message = create_backup([table_name])
    if not success:
        return False, f"Failed to create backup before deletion: {message}"

    try:
        # Drop the table
        db.session.execute(f'DROP TABLE IF EXISTS {table_name}')
        db.session.commit()
        return True, f"Table {table_name} deleted successfully"
    except Exception as e:
        db.session.rollback()
        return False, f"Failed to delete table: {str(e)}"

def get_all_tables():
    """Get list of all tables in database"""
    try:
        result = db.session.execute('SHOW TABLES')
        return [row[0] for row in result]
    except Exception as e:
        return []
