from app import login, db
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    db.execute("SELECT * FROM Users WHERE id = %s;", (id,))
    return User(db.fetchone()) if db.rowcount == 1 else None

class User(UserMixin):
    @property
    def id(self):
        return self.user_id
    
    def __init__(self, user_data):
        self.user_id = user_data.get('id')
        self.username = user_data.get('username')
        self.password_hash = user_data.get('password_hash')
        self.country = user_data.get('country')
        self.state_id = user_data.get('state_id')
        self.city_id = user_data.get('city_id')
    
