import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = f'''
    host={os.getenv('DB_HOST')}
    port={os.getenv('DB_PORT')}
    dbname={os.getenv('DB_NAME')} 
    user={os.getenv('DB_USERNAME')} 
    password={os.getenv('DB_PASSWORD')}
'''

with psycopg.connect(connection_string, options="-c datestyle=ISO,DMY") as conn:
    with conn.cursor() as cur:
        # Run sql script to create tables
        with open('init_tables.sql') as sql:
            cur.execute(sql.read())

        # Load the cities data
        with open('cities.csv', 'r') as f:
            with cur.copy('''COPY Cities(id, city_name) 
                            FROM STDIN DELIMITER ',' CSV HEADER;''') as copy:
                copy.write(f.read())

        # Load the states data
        with open('states.csv', 'r') as f:
            with cur.copy('''COPY States(id, state_name)
                            FROM STDIN DELIMITER ',' CSV HEADER;''') as copy:
                copy.write(f.read())

        # Load the users data
        with open('users.csv') as f:
            with cur.copy('''COPY Users(id, username, password_hash, country, state_id, city_id)
                            FROM STDIN DELIMITER ',' CSV HEADER;''') as copy:
                copy.write(f.read())
        
        # Load the posts data
        with open('posts.csv', 'r') as f:
            with cur.copy('''COPY Posts(poster_id, post_date, sighting_date, sighting_time, 
                                        country, state_id, city_id, 
                                        duration, summary, image_url, latitude, longitude)
                            FROM STDIN DELIMITER ',' CSV HEADER;''') as copy:
                copy.write(f.read())

        conn.commit()
