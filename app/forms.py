from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, URLField, DateTimeLocalField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Optional, Length

from app import pgdb

class LoginForm(FlaskForm):
    handle = StringField('Handle', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# TODO:
# Should probably make city a stringfield
# If not present in database, insert the new city
# before inserting the user or post.

@pgdb.connect
def get_states(db):
    return db.query_states()

@pgdb.connect
def get_cities(db):
    return db.query_states()

class RegistrationForm(FlaskForm):
    handle = StringField('Handle', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_repeat = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    state   = SelectField('State', validators=[Optional()],
                          choices=([('', '---')] + get_states()))
    city    = SelectField('City', validators=[Optional()],
                          choices=([('', '---')] + get_cities()))
    
    def validate_handle(self, handle):
        userdata = pgdb.cursor.query_userdata_by_handle(handle.data)
        if userdata is not None:
            raise ValidationError('Handle already taken!')
        
    # TASK: add a validator for the password. 
    # * Use regex to require at least 1 uppercase letter, at least 1 number, 
    #   and minimum 5 characters - or make up some other rules.
    # * Once this is added, we have to regenerate the dataset, so the sample
    #   users have a password that satisfies these conditions. You can modify
    #   the default password in data/generate_dataset.py
    #   
    # the function should have the following signature:
    # def validate_password(self, password):
    # if validation is successful, return nothing. Otherwise, raise an validationerror

class CreatePostForm(FlaskForm):
    summary = TextAreaField('Summary of sighting', validators=[DataRequired(), Length(max=512, message="Maximum 512 characters allowed")])
    imageUrl = URLField('The image Url', validators=[Optional()])
    sightingDateTime = DateTimeLocalField("Sighting Date and time", validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    sightingDuration = StringField("The duration of the sighting", validators=[DataRequired()])

    state = SelectField('State', validators=[Optional()],
                        choices=([('', '---')] + get_states()))
    city = SelectField('City', validators=[Optional()],
                        choices=([('', '---')] + get_cities()))

    latField = FloatField('Sighting latitude', validators=[Optional()])
    lonField = FloatField('Sighting longitude', validators=[Optional()])

    post = SubmitField('Post sighting')


class CreateSearchForm(FlaskForm):
    search = StringField('Searchfield', validators=[DataRequired()], render_kw={"placeholder": "Search..."})
    submit = SubmitField('Search')