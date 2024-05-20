import os
import psycopg
from dotenv import load_dotenv

class Database:
    def __init__(self):
        load_dotenv()

        connection_string = f'''
            host={os.getenv('DB_HOST')}
            port={os.getenv('DB_PORT')}
            dbname={os.getenv('DB_NAME')} 
            user={os.getenv('DB_USERNAME')} 
            password={os.getenv('DB_PASSWORD')}
        '''

        self.conn = psycopg.connect(connection_string)
        self.cursor = self.conn.cursor()
        self.dict_cursor = self.conn.cursor(row_factory=psycopg.rows.dict_row)

    def query_userdata_by_username(self, username):
        self.dict_cursor.execute("SELECT * FROM Users WHERE username = %s;", (username, ))
        return self.dict_cursor.fetchone() if self.dict_cursor.rowcount == 1 else None

    def query_username(self, user_id):
        self.cursor.execute("SELECT username FROM Users WHERE id = %s", (user_id, ))
        if self.cursor.rowcount == 1:
            return self.cursor.fetchone()[0]
        else:
            return None

    def insert_user(self, user):
        query = """INSERT INTO 
        Users(username, password_hash, country, state_id, city_id)
        VALUES (%s, %s, %s, %s, %s);"""
        self.cursor.execute(query, (user.username, user.password_hash, user.country, user.state_id, user.city_id))
        self.conn.commit()

    def query_countries(self):
        self.cursor.execute("SELECT country_name FROM Countries;")
        return [country[0] for country in self.cursor.fetchall()]
    
    def query_states(self):
        self.cursor.execute("SELECT id, state_name FROM States;")
        return self.cursor.fetchall()

    def query_cities(self):
        self.cursor.execute("SELECT id, city_name FROM Cities;")
        return self.cursor.fetchall()
    
    def query_state_name(self, state_id):
        query = "SELECT state_name FROM States WHERE id = %s;"
        self.cursor.execute(query, (state_id, ))
        if self.cursor.rowcount == 1:
            return self.cursor.fetchone()[0]
        else:
            return 'Unknown'
        
    def query_city_name(self, city_id):
        query = "SELECT city_name FROM Cities WHERE id = %s;"
        self.cursor.execute(query, (city_id, ))
        if self.cursor.rowcount == 1:
            return self.cursor.fetchone()[0]
        else:
            return 'Unknown'
        
    def query_recent_posts(self, count):
        query = "SELECT * FROM Posts ORDER BY post_date LIMIT %s;"
        self.dict_cursor.execute(query, (count, ))
        return self.dict_cursor.fetchall()