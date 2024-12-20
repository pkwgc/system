from main import app, db
from sqlalchemy import inspect

def inspect_database():
    with app.app_context():
        inspector = inspect(db.engine)
        print("Available tables:")
        for table_name in inspector.get_table_names():
            print(f"\nTable: {table_name}")
            print("Columns:")
            for column in inspector.get_columns(table_name):
                print(f"  - {column['name']}: {column['type']}")
            print("Primary Key:", inspector.get_pk_constraint(table_name))
            print("Foreign Keys:", inspector.get_foreign_keys(table_name))

if __name__ == "__main__":
    inspect_database()
