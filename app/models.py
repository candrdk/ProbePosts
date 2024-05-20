from app import login, db
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    db.dict_cursor.execute("SELECT * FROM Users WHERE id = %s;", (id,))
    if db.dict_cursor.rowcount == 1:
        return User(db.dict_cursor.fetchone()) 
    else:
        return None

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
    
class Post:
    def __init__(self, post_data):
        self.post_id         = post_data['id']

        self.poster_id       = post_data['poster_id']
        self.poster_username = db.query_username(self.poster_id)

        self.post_date       = post_data['post_date']
        self.sighting_date   = post_data['sighting_date']
        self.sighting_time   = post_data['sighting_time']
        self.country         = post_data['country']

        self.state_id        = post_data['state_id']
        self.city_id         = post_data['city_id']
        self.state           = db.query_state_name(self.state_id) if self.state_id is not None else None
        self.city            = db.query_city_name(self.city_id) if self.state_id is not None else None

        self.duration        = post_data['duration']
        self.content         = post_data['summary']
        self.image_url       = post_data['image_url']
        self.latitude        = post_data['latitude']
        self.longitude       = post_data['longitude']
