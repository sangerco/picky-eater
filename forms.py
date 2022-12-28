from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField
from wtforms import SelectMultipleField
from wtforms.validators import InputRequired, Email, Length, NumberRange

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
    intolerances = StringField('Intolerances')

class ChildProfileForm(FlaskForm):
    ''' form for creating/editing child profiles '''

    name = StringField('Profile Name', validators=[InputRequired()])
    no_foods = StringField('No Thank You! Foods')
    yes_foods = StringField('Yes Please! Foods')
    diet = SelectField('Diet', coerce=int, choices=[])
    intolerances = StringField('Intolerances')

class FavoriteRecipeForm(FlaskForm):
    ''' form for favoriting, rating, and reviewing recipes '''

    review = TextAreaField('Review this recipe:')
    rating = IntegerField('Rate this recipe from 1 to 5!', 
                    validators=[NumberRange(min=1,max=5,
                    message='Must be a number between 1 and 5!')])

class ShareRecipeForm(FlaskForm):
    ''' form for sharing recipes with other users with message functionality '''

    def pre_validate(self, form):
        pass

    follower = SelectField('Who are you sharing this with?', coerce=int, choices=[])
    message = TextAreaField('Type message here.')

class ReplyForm(FlaskForm):
    ''' form for replying to shared messages '''

    def pre_validate(self, form):
        pass

    message = TextAreaField('Type message here.')