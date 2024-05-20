from app import db, conn
from app.models import User

def get_user_by_username(username):
    db.execute("SELECT * FROM Users WHERE username = %s;", (username, ))
    return User(db.fetchone()) if db.rowcount == 1 else None

def insert_user(user):
    query = """INSERT INTO 
    Users(username, password_hash, country, state_id, city_id)
    VALUES (%s, %s, %s, %s, %s);"""

    db.execute(query, (user.username, user.password_hash, user.country, user.state_id, user.city_id))
    conn.commit()

def get_countries():
    query = "SELECT * FROM Countries"
    db.execute(query)
    res = db.fetchall()
    return res

def get_states():
    query = "SELECT * FROM States"
    db.execute(query)
    res = db.fetchall()
    return res 

def get_cities():
    query = "SELECT * FROM Cities"
    db.execute(query)
    res = db.fetchall()
    return res 