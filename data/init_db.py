import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

dir = os.path.dirname(os.path.abspath(__file__))

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
        with open(os.path.join(dir, 'scripts', 'init_tables.sql'), 'r') as sql:
            cur.execute(sql.read())

        # Run sql script to create the ratings trigger
        with open(os.path.join(dir, 'scripts', 'ratings_trigger.sql'), 'r') as sql:
            cur.execute(sql.read())

        # Load the cities data
        with open(os.path.join(dir, 'tables', 'cities.csv'), 'r') as f:
            with cur.copy('''COPY Cities(city_name) 
                            FROM STDIN DELIMITER ',' CSV HEADER;''') as copy:
                copy.write(f.read())

        # Load the states data
        with open(os.path.join(dir, 'tables', 'states.csv'), 'r') as f:
            with cur.copy('''COPY States(state_code, state_name)
                            FROM STDIN DELIMITER ',' CSV HEADER;''') as copy:
                copy.write(f.read())

        # Load the users data
        with open(os.path.join(dir, 'tables', 'users.csv'), 'r') as f:
            with cur.copy('''COPY Users(display_name, handle, password_hash, state_code, city_id)
                            FROM STDIN DELIMITER ',' CSV HEADER;''') as copy:
                copy.write(f.read())
        
        # Load the posts data
        with open(os.path.join(dir, 'tables', 'posts.csv'), 'r') as f:
            with cur.copy('''COPY Posts(poster_id, post_date, sighting_date, sighting_time, 
                                        state_code, city_id, duration, summary, image_url, 
                                        latitude, longitude)
                            FROM STDIN DELIMITER ',' CSV HEADER;''') as copy:
                copy.write(f.read())
        
        # Create a temporary staging table, copy the actual image urls into it,
        # update the actual Posts table and finally drop it. We have split image 
        # urls up from the posts.csv file like this to avoid having to scrape 
        # all urls every time we want to change the rest of the dataset.
        with open(os.path.join(dir, 'image_urls.csv'), 'r') as f:
            cur.execute('CREATE TEMP TABLE tmp_img (id SERIAL, image_url VARCHAR(512));')

            with cur.copy('''COPY tmp_img(image_url) FROM STDIN DELIMITER ',' CSV HEADER;''') as copy:
                copy.write(f.read())

            cur.execute('''UPDATE Posts 
                           SET image_url = tmp_img.image_url 
                           FROM tmp_img 
                           WHERE Posts.id = tmp_img.id;
                        
                           DROP TABLE tmp_img;''')

        # Load the follows relation table
        with open(os.path.join(dir, 'tables', 'follows.csv'), 'r') as f:
            with cur.copy('''COPY Follows(user_id, follows_id)
                          FROM STDIN DELIMITER ',' CSV HEADER;''') as copy:
                copy.write(f.read())

        # Load the ratings relation table
        with open(os.path.join(dir, 'tables', 'ratings.csv'), 'r') as f:
            with cur.copy('''COPY Ratings(user_id, post_id, rating)
                          FROM STDIN DELIMITER ',' CSV HEADER;''') as copy:
                copy.write(f.read())

        conn.commit()
