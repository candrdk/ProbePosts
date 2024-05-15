from app import login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login.user_loader
def load_user(id):
    # TODO:
    # query = "SELECT * FROM Users WHERE pk = %s"
    # db.execute(sql, (id,))
    # return User(db.fetchone()) if db.rowcount > 0 else None
    user = User({'username': 'candr', 'pk': id})
    user.set_password('candr')
    return user if id == user.id else None

class User(UserMixin):
    @property
    def id(self):
        return self.pk
    
    def __init__(self, user_data):
        self.pk = user_data.get('pk')
        self.username = user_data.get('username')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
