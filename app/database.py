import os
import psycopg
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
from contextlib import contextmanager

class PostgresDB:
    def __init__(self):
        load_dotenv()

        connection_string = f'''
            host={os.getenv('DB_HOST')}
            port={os.getenv('DB_PORT')}
            dbname={os.getenv('DB_NAME')} 
            user={os.getenv('DB_USERNAME')} 
            password={os.getenv('DB_PASSWORD')}
        '''

        self.pool = ConnectionPool(connection_string)

    @contextmanager
    def connection(self):
        with self.pool.connection() as conn:
            yield DBConnection(conn)

    def connect(self, func):
        def decorator(*args, **kwargs):
            with self.connection() as db:
                return func(db, *args, **kwargs)

        # To avoid errors with flask registering functions
        # with the pgdb.connect name instead of the name of
        # the decorated function, we have to set the name
        # of the decorator to the decorated function name.
        decorator.__name__ = func.__name__
        return decorator

class DBConnection:
    def __init__(self, conn):
        self.conn = conn
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
    
    def query_posts_by_user_id(self, user_id):
        self.dict_cursor.execute("SELECT * FROM Posts WHERE poster_id = %s ORDER BY post_date DESC;", (user_id, ))
        return self.dict_cursor.fetchall()

    def insert_user(self, user):
        query = """INSERT INTO 
        Users(display_name, handle, password_hash, state_code, city_id)
        VALUES (%s, %s, %s, %s, %s);"""
        self.cursor.execute(query, (user.display_name, user.handle, user.password_hash, user.state_code, user.city_id))
        self.conn.commit()
    
    def insert_post(self, post):
        query = """INSERT INTO
        Posts(poster_id, post_date, sighting_date, sighting_time, state_code, city_id, duration, summary, image_url, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
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
        
    def query_recent_posts_page(self, post_count, page_num=0):
        query = "SELECT * FROM Posts ORDER BY post_date DESC LIMIT %s OFFSET %s;"
        self.dict_cursor.execute(query, (post_count, page_num * post_count))
        return self.dict_cursor.fetchall()

    def query_rate_post(self, user_id, post_id, rating):
        query = "INSERT INTO rate_view VALUES (%s, %s, %s);"
        self.cursor.execute(query, (user_id, post_id, rating))
        self.conn.commit()

    def query_post_rating(self, user_id, post_id):
        query = "SELECT rating FROM Ratings WHERE user_id = %s AND post_id = %s;"
        self.cursor.execute(query, (user_id, post_id))
        if self.cursor.rowcount == 1:
            return self.cursor.fetchone()[0]
        else:
            return None

    def query_post_karma(self, post_id):
        query = """SELECT
            (SELECT COUNT(*) FROM Ratings WHERE post_id = %s AND rating=true)
          - (SELECT COUNT(*) FROM Ratings WHERE post_id = %s AND rating=false) AS Karma;"""

        self.cursor.execute(query, (post_id, post_id))
        if self.cursor.rowcount == 1:
            return self.cursor.fetchone()[0]
        else:
            return 0
