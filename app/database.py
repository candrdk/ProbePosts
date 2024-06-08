import os
import psycopg
import re
from psycopg_pool import ConnectionPool
from psycopg import Cursor, sql
from dotenv import load_dotenv
from contextlib import contextmanager
from datetime import datetime

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
        self.cursor:cursor.Cursor = self.conn.cursor()
        self.dict_cursor:Cursor = self.conn.cursor(row_factory=psycopg.rows.dict_row)

    def query_userdata_by_id(self, id):
        self.dict_cursor.execute("SELECT * FROM Users WHERE id = %s;", (id, ))
        return self.dict_cursor.fetchone() if self.dict_cursor.rowcount == 1 else None

    def query_userdata_by_handle(self, handle):
        self.dict_cursor.execute("SELECT * FROM Users WHERE handle = %s;", (handle, ))
        return self.dict_cursor.fetchone() if self.dict_cursor.rowcount == 1 else None

    def query_user_display_name(self, user_id):
        self.cursor.execute("SELECT display_name FROM Users WHERE id = %s;", (user_id, ))
        return self.cursor.fetchone()[0] if self.cursor.rowcount == 1 else None

    def query_user_handle(self, user_id):
        self.cursor.execute("SELECT handle FROM Users WHERE id = %s;", (user_id, ))
        return self.cursor.fetchone()[0] if self.cursor.rowcount == 1 else None
    
    def query_user_id(self, user_handle):
        self.cursor.execute("SELECT id FROM Users WHERE handle = %s;", (user_handle, ))
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
        self.cursor.execute("SELECT city_name FROM Cities;")
        return [city for (city,) in self.cursor.fetchall()]
    
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
        
    def query_city_id(self, city):
        self.cursor.execute("SELECT id FROM Cities WHERE city_name = %s;", (city, ))
        if self.cursor.rowcount == 1:
            return self.cursor.fetchone()[0]
        else:
            return None

    def insert_city(self, city):
        self.cursor.execute("INSERT INTO Cities(city_name) VALUES (%s);", (city, ))
        self.conn.commit()

    def query_or_insert_city_get_id(self, city_raw):
        if city_raw == '':
            return None

        city = city_raw.title()
        city_id = self.query_city_id(city)

        if city_id is None:
            self.insert_city(city)
            city_id = self.query_city_id(city)
        
        return city_id

    def query_recent_posts_page(self, post_count, page_num=0):
        query = "SELECT * FROM Posts ORDER BY post_date DESC LIMIT %s OFFSET %s;"
        self.dict_cursor.execute(query, (post_count, page_num * post_count))
        return self.dict_cursor.fetchall()

    def query_recent_posts_by_user_page(self, user_id, post_count, page_num=0):
        query = "SELECT * FROM Posts WHERE poster_id = %s ORDER BY post_date DESC LIMIT %s OFFSET %s;"
        self.dict_cursor.execute(query, (user_id, post_count, page_num * post_count))
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

    def query_user_liked_posts(self, poster_id:int):
        query = """
                select p.* from posts p join ratings r on p.id = r.post_id where r.user_id = %s;
                """
        self.dict_cursor.execute(query,(poster_id, ))
        return self.dict_cursor.fetchall()
        
    def query_user_liked_posts_page(self, user_id, post_count, page_num=0):
        print((user_id, post_count, page_num ), flush=True)
        query = "SELECT p.* FROM Posts p join ratings r on p.id = r.post_id WHERE r.user_id = %s ORDER BY p.post_date DESC LIMIT %s OFFSET %s;"
        self.dict_cursor.execute(query, (user_id, post_count, page_num * post_count))
        return self.dict_cursor.fetchall()
    
    def query_state_code(self, state):
        self.cursor.execute("SELECT state_code FROM States WHERE state_name = %s;", (state, ))
        if self.cursor.rowcount == 1:
            return self.cursor.fetchone()[0]
        else:
            return None

    def query_search_posts_page(self, q, post_count, page_num=0):

        # List of patterns that can be matched in a search query.
        # Kind of messy, since we have to be careful with to avoid SQL injection.
        pattern = [
            (r'state:(\w+)'               , lambda x: sql.SQL('{field} = {value}').format(field=sql.Identifier('statec_code'), value=sql.Literal(self.query_state_code(x.title())))),
            (r'city:(\w+)'                , lambda x: sql.SQL('{field} = {value}').format(field=sql.Identifier('city_id'),     value=sql.Literal(self.query_city_id(x.title())))),
            (r'before:(\d{4}-\d{2}-\d{2})', lambda x: sql.SQL('{field} < {value}').format(field=sql.Identifier('post_date'),   value=sql.Literal(datetime.strptime(x, '%Y-%m-%d')))),
            (r'after:(\d{4}-\d{2}-\d{2})' , lambda x: sql.SQL('{field} > {value}').format(field=sql.Identifier('post_date'),   value=sql.Literal(datetime.strptime(x, '%Y-%m-%d')))),
            (r'before:(\d{4})'            , lambda x: sql.SQL('{field} < {value}').format(field=sql.Identifier('post_date'),   value=sql.Literal(datetime.strptime(x, '%Y')))),
            (r'after:(\d{4})'             , lambda x: sql.SQL('{field} > {value}').format(field=sql.Identifier('post_date'),   value=sql.Literal(datetime.strptime(x, '%Y')))),
            (r'from:(\w+)'                , lambda x: sql.SQL('{field} = {value}').format(field=sql.Identifier('poster_id'),   value=sql.Literal(self.query_user_id(x))))
        ]

        d = [sql.SQL('summary ILIKE %(search)s')]
        for (regex, func) in pattern:           # Check if the query contains any
            match = re.search(regex, q)         # of the supported patterns. 
            if match:           
                d += [func(match.group(1))]     # Add the SQL condition to d
                q = re.sub(regex, '', q)        # and remove it from the query.


        # Retrieve a page of count posts matching the conditions of the search query
        query = sql.SQL('''SELECT * FROM Posts
                           WHERE {conditions}
                           ORDER BY post_date DESC
                           LIMIT %(count)s
                           OFFSET %(page)s;''').format(conditions=sql.SQL(' AND ').join(d))

        # Any part of the string that didn't match any patterns is
        # assumed to be a simple search of the summary text of posts.
        params = {'search': f'%{q.strip()}%',
                  'count': post_count,
                  'page': page_num * post_count}

        self.dict_cursor.execute(query, params)
        return self.dict_cursor.fetchall()
