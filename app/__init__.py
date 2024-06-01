from flask import Flask
from flask_login import LoginManager

from app.database import PostgresDB

app = Flask(__name__)
app.config['SECRET_KEY'] = 'LaLiLuLeLo'

login = LoginManager(app)
login.login_view = 'login'

pgdb = PostgresDB()

from app import routes
