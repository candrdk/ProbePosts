from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Optional

from app import db

class LoginForm(FlaskForm):
    handle = StringField('Handle', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    handle = StringField('Handle', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_repeat = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    state   = SelectField('State', validators=[Optional()],
                          choices=([('', '---')] + db.query_states()))
    city    = SelectField('City', validators=[Optional()],
                          choices=([('', '---')] + db.query_cities()))
    
    def validate_handle(self, handle):
        userdata = db.query_userdata_by_handle(handle.data)
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
