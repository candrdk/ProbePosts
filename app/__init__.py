from flask import Flask
from flask_login import LoginManager

import os
import psycopg
from dotenv import load_dotenv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'LaLiLuLeLo'

login = LoginManager(app)
login.login_view = 'login'

load_dotenv()

connection_string = f'''
    host={os.getenv('DB_HOST')}
    port={os.getenv('DB_PORT')}
    dbname={os.getenv('DB_NAME')} 
    user={os.getenv('DB_USERNAME')} 
    password={os.getenv('DB_PASSWORD')}
'''

# TODO(caleb): how to close this connection?
conn = psycopg.connect(connection_string, row_factory=psycopg.rows.dict_row)
db = conn.cursor()

from app import routes
