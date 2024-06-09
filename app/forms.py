from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, URLField, DateTimeLocalField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Optional, Length

from app import pgdb

class LoginForm(FlaskForm):
    handle = StringField('Handle', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

@pgdb.connect
def get_states(db):
    return db.query_states()

class RegistrationForm(FlaskForm):
    handle          = StringField('Handle', validators=[DataRequired(), Length(min=4, max=32)])
    password        = PasswordField('Password', validators=[DataRequired()])
    password_repeat = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    state           = SelectField('State', validators=[Optional()], choices=([('', '---')] + get_states()))
    city            = StringField('City', validators=[Optional(), Length(min=2, max=64)])
    submit          = SubmitField('Register')
    
    city_id         = None
    
    def validate_handle(self, handle):
        with pgdb.connection() as db:
            userdata = db.query_userdata_by_handle(handle.data)
            if userdata is not None:
                raise ValidationError('Handle already taken!')

    # Set form data to city id. If city name not in database, it is inserted.
    def validate_city(self, city):
        with pgdb.connection() as db:
            self.city_id = db.query_or_insert_city_get_id(city.data)

class CreatePostForm(FlaskForm):
    summary = TextAreaField('Summary of sighting', validators=[DataRequired(), Length(max=512, message="Maximum 512 characters allowed")])
    imageUrl = URLField('URL of image', validators=[Optional(), Length(max=512)])
    sightingDateTime = DateTimeLocalField("Sighting Date and time", validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    sightingDuration = StringField("The duration of the sighting", validators=[DataRequired(), Length(max=128)])

    state = SelectField('State', validators=[Optional()], choices=([('', '---')] + get_states()))
    city  = StringField('City', validators=[Optional(), Length(min=2, max=64)])

    latField = FloatField('Sighting latitude', validators=[DataRequired()])
    lonField = FloatField('Sighting longitude', validators=[DataRequired()])

    post = SubmitField('Post sighting')

    def validate_imageUrl(self, imageUrl):
        valid_extensions = ['png', 'jpg', 'jpeg']
        extension = imageUrl[-5:].split('.')[-1]
        if extension not in valid_extensions:
            raise ValidationError('Image url must be a .png, .jpg or .jpeg')

    # Set form data to city id. If city name not in database, it is inserted.
    def validate_city(self, city):
        with pgdb.connection() as db:
            self.city_id = db.query_or_insert_city_get_id(city.data)

class CreateSearchForm(FlaskForm):
    search = StringField('Searchfield', validators=[DataRequired()], render_kw={"placeholder": "Search...", "autocomplete": "off"})
    submit = SubmitField('Search')
