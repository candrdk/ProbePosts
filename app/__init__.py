from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'LaLiLuLeLo'

login = LoginManager(app)
login.login_view = 'login'

from app import routes
