from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, User_profile, Child_profile
from models import Favorite_recipe, Follows, Shopping_list
from forms import NewUserForm, LoginForm
from sqlalchemy.exc import IntegrityError

CURR_USER_KEY = 'curr_user'


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///picky_eater"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "finn_is_awesome"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.app_context().push()
connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.before_request
def add_user_to_g():
    """ add logged in user to Flask global """

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def do_login(user):
    """ Login user """

    session[CURR_USER_KEY] = user.id

def do_logout(user):
    """ Logout user """

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY] 

@app.route('/')
def landing_page():
    """ show welcome page for new users/logged out users, redirect logged in users """

    if g.user:
        return redirect(f'/users/{g.user.id}')

    else:
        return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup_user():
    """ display form to sign up user
        create new user and add to db
        redirect user to new page """

    form = NewUserForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        password = form.password.data
        email = form.email.data

        new_user = User.register_user(first_name, last_name, username, password, email)

        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken! Please choose another!')
            return render_template('signup.html', form=form)
        
        do_login(new_user)

        return redirect(f'/users/{new_user.id}')
    
    else:
        return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """ display form to login in user
        authenticate user and redirect to user page
        if invalid, flash message, show login form again 
        """
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate_user(username, password)
        if user:
            flash(f'Welcome back, {user.username}!', 'primary')
            session['user_id'] = user.id
            return redirect(f'/users/{user.id}')
        else:
            form.username.errors = ['Invalid username/password.']
    return render_template('login.html', form=form)

@app.route('/users')
def general_users_page():
    """ display other users with functionality to go to other user's pages """

    users = User.query.all()

    return render_template('users.html', users=users)