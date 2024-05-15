from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'LaLiLuLeLo'

from app import routes
