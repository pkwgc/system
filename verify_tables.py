from models import db
from main import app

def verify_tables():
    """Verify database tables are created with correct schema"""
    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print('\nCreated tables:', tables)

        for table in tables:
            print(f'\nColumns in {table}:')
            for column in inspector.get_columns(table):
                print(f'- {column["name"]}: {column["type"]}')

if __name__ == '__main__':
    verify_tables()
