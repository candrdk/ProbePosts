from app.models import User

def get_user_by_username(username):
    # TODO:
    # query = "SELECT * FROM Users WHERE username = %s"
    # db.execute(query, (username,))
    # return User(db.fetchone()) if db.rowcount > 0 else None
    user = User({'username': 'candr'})
    user.set_password('candr')
    return user if username == 'candr' else None
