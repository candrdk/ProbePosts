from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError

from app.queries import get_user_by_username

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# TASK: Add support for choosing country, state, city
# * Add a SelectField for choosing country.
#   - Should have a DataRequired() validator
#   - The field should be added to the templates/register.html file
# * Add an enumerate_countries query to queries.py
#   - Available choices should be queried from the database.
#   - use db.fetchall to get a list of dictionaries for each row in country table
#   - use list comprehension to tranfsorm this list into just a list of contry names
# * Add SelectFields for choosing state and city
#   - These should *not* be required!
#   - follow the same steps as the countries selectfield
# * Once these have been implemented, make sure that they are passed
#   actually saved in the user. See register function in routes.py 
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_repeat = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = get_user_by_username(username.data)
        if user is not None:
            raise ValidationError('Username already taken!')
        
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
