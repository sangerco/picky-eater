from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email, Length

class NewUserForm(FlaskForm):
    """ form for signing up new users """

    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('First Name', validators=[InputRequired()])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    email = StringField('Email', validators=[InputRequired(), 
                            Email(message='Please enter a valid email address')])
    image = StringField('Profile Picture URL (Optional)')

class LoginForm(FlaskForm):
    """ form for logging in/validating existing users """

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    