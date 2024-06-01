from app import login, pgdb
from flask_login import UserMixin

@login.user_loader
@pgdb.connect
def load_user(db, id):
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
        self.display_name = user_data.get('display_name')
        self.handle = user_data.get('handle')
        self.password_hash = user_data.get('password_hash')
        self.state_code = user_data.get('state_code')
        self.city_id = user_data.get('city_id')
    
class Post:
    def __init__(self, db, post_data, user_id=None):
        self.id = post_data['id']

        self.poster_id           = post_data['poster_id']
        self.poster_display_name = db.query_user_display_name(self.poster_id)
        self.poster_handle       = db.query_user_handle(self.poster_id)
        
        self.user_rating         = None if user_id is None else db.query_post_rating(user_id, self.id)
        self.karma               = db.query_post_karma(self.id)

        self.post_date       = post_data['post_date']
        self.sighting_date   = post_data['sighting_date']
        self.sighting_time   = post_data['sighting_time']

        self.state_code      = post_data['state_code']
        self.city_id         = post_data['city_id']
        self.state_name      = db.query_state_name(self.state_code) if self.state_code is not None else None
        self.city            = db.query_city_name(self.city_id)   if self.city_id  is not None else None

        self.duration        = post_data['duration']
        self.content         = post_data['summary']
        self.image_url       = post_data['image_url']
        self.latitude        = post_data['latitude']
        self.longitude       = post_data['longitude']
