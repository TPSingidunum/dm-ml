import pymysql
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

class Database:

    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'dm-2'),
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor
        }

    def get_connection(self):
        try:
            return pymysql.connect(**self.connection_params)
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            raise

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        connection = None
        try:
            connection = self.get_connection()
            with connection.cursor() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")
        finally:
            if connection:
                connection.close()

db = Database()