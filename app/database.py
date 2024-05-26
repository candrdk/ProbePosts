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

    def query_userdata_by_handle(self, handle):
        self.dict_cursor.execute("SELECT * FROM Users WHERE handle = %s;", (handle, ))
        return self.dict_cursor.fetchone() if self.dict_cursor.rowcount == 1 else None

    def query_user_display_name(self, user_id):
        self.cursor.execute("SELECT display_name FROM Users WHERE id = %s;", (user_id, ))
        return self.cursor.fetchone()[0] if self.cursor.rowcount == 1 else None

    def query_user_handle(self, user_id):
        self.cursor.execute("SELECT handle FROM Users WHERE id = %s;", (user_id, ))
        return self.cursor.fetchone()[0] if self.cursor.rowcount == 1 else None

    def insert_user(self, user):
        query = """INSERT INTO 
        Users(display_name, handle, password_hash, state_code, city_id)
        VALUES (%s, %s, %s, %s, %s);"""
        self.cursor.execute(query, (user.display_name, user.handle, user.password_hash, user.state_code, user.city_id))
        self.conn.commit()
    
    def insert_post(self, post):
        query = """INSERT INTO
        Posts(poster_id, post_date, sighting_date, sighting_time, state_code, city_id, duration, summary, image_url, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
        """
        self.cursor.execute(query, (post.poster_id, post.post_date, post.sighting_date,
                                     post.sighting_time, post.state_code, post.city_id,
                                       post.duration, post.content, post.image_url, post.latitude, post.longitude))
        self.conn.commit()

    def query_states(self):
        self.cursor.execute("SELECT state_code, state_name FROM States;")
        return self.cursor.fetchall()

    def query_cities(self):
        self.cursor.execute("SELECT id, city_name FROM Cities;")
        return self.cursor.fetchall()
    
    def query_state_name(self, state_code):
        query = "SELECT state_name FROM States WHERE state_code = %s;"
        self.cursor.execute(query, (state_code, ))
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
        query = "SELECT * FROM Posts ORDER BY post_date DESC LIMIT %s;"
        self.dict_cursor.execute(query, (count, ))
        return self.dict_cursor.fetchall()