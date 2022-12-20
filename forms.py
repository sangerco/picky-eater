from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Email, Length

class NewUserForm(FlaskForm):
    """ form for signing up new users """

    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), 
                            Email(message='Please enter a valid email address')])
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    image = StringField('Profile Picture URL (Optional)', default='/static/images/picky_eater.jpg')

class LoginForm(FlaskForm):
    """ form for logging in/validating existing users """

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    
class UserProfileForm(FlaskForm):
    """ form for creating/editing user profile """

    no_foods = StringField('No Thank You! Foods')
    yes_foods = StringField('Yes Please! Foods')
    diet = SelectField('Diet', coerce=int, choices=[])

class ChildProfileForm(FlaskForm):
    ''' form for creating/editing child profiles '''

    name = StringField('Profile Name', validators=[InputRequired()])
    no_foods = StringField('No Thank You! Foods')
    yes_foods = StringField('Yes Please! Foods')
    diet = SelectField('Diet', coerce=int, choices=[])
