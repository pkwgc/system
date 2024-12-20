import pymysql
import urllib.parse
import time

def test_mysql_connection():
    # Connection parameters
    host = 'rm-m5e0666vtv5234qi39o.mysql.rds.aliyuncs.com'
    user = 'pkwgc'
    password = 'Wghfd@584521@fd'
    database = 'stsmen'
    port = 3306

    print(f"Attempting to connect to MySQL database at {host}...")
    start_time = time.time()

    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
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
