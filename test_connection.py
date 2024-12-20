import pymysql
import time
from config import Config

def test_mysql_connection():
    print(f"Attempting to connect to MySQL database at {Config.DB_HOST}...")
    start_time = time.time()

    try:
        connection = pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASS.replace('%40', '@'),  # Decode URL-encoded password
            database=Config.DB_NAME,
            port=int(Config.DB_PORT),
            connect_timeout=5  # Set a 5-second timeout
        )
        print("Successfully connected to the database!")
        connection.close()
        return True
    except pymysql.Error as e:
        print(f"Failed to connect to the database. Error: {e}")
        print(f"Time elapsed: {time.time() - start_time:.2f} seconds")
        return False

if __name__ == "__main__":
    test_mysql_connection()
