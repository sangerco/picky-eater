from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, User_profile, Child_profile
from models import Favorite_recipe, Follows, Shopping_list, Diet
from forms import NewUserForm, LoginForm, UserProfileForm
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

def do_logout():
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
        image = form.image.data

        new_user = User.register_user(first_name, last_name, username, password, email, image)

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

@app.route('/logout')
def logout_user():
    """ log out user and redirect to start page """

    do_logout()
    return redirect('/')

@app.route('/users')
def general_users_page():
    """ display other users with functionality to go to other user's pages """

    users = User.query.all()

    return render_template('users.html', users=users)

@app.route('/users/<int:user_id>')
def user_page(user_id):
    """ display individual users page """

    user = User.query.get_or_404(user_id)
    user_profile = User_profile.query.filter_by(user_id = user_id).first()
    child_profiles = Child_profile.query.filter(Child_profile.user_id == user_id).all()
    favorite_recipes = Favorite_recipe.query.filter(Favorite_recipe.user_id == user_id).all()

    return render_template('user-info.html', 
                user=user, user_profile=user_profile, 
                child_profiles=child_profiles, favorite_recipes=favorite_recipes)


@app.route('/users/<int:user_id>/profile', methods=['GET', 'POST'])
def user_profile_page(user_id):
    """ display user profile page """

    user = User.query.get_or_404(user_id)
    profile = User_profile.query.filter_by(user_id = user_id).first()
    if profile:
        child_profiles = Child_profile.query.filter(Child_profile.user_id == user_id).all()

        if profile.no_foods:
            no_food_list = [nf for nf in profile.no_foods]
        else:
            no_food_list = [] 

        if profile.yes_foods:
            yes_food_list = [yf for yf in profile.yes_foods]
        else:
            yes_food_list = []

        return render_template('user-profile.html', user=user, profile=profile,
                    child_profiles=child_profiles, no_foods=no_food_list, 
                    yes_foods=yes_food_list, diet=profile.diet)

    else:
        form = UserProfileForm()
        form.diet.choices = [(diet.id, diet.diet) for diet in Diet.query.all()]
        print(form.diet.choices)
        user = User.query.get_or_404(user_id)
        if form.validate_on_submit():
            no_foods = form.no_foods.data
            yes_foods = form.yes_foods.data
            diet = form.diet.data

            new_profile = User_profile(no_foods=no_foods, yes_foods=yes_foods, diet=diet)
            db.session.add(new_profile)
            db.session.commit()
            flash('Hooray! New profile added!', 'success')
            return redirect(f'/users/{user_id}/profile')
        
    return render_template('user-profile.html', user=user, form=form)

@app.route('/users/<int:user_id>/profile/add')
def create_user_profile(user_id):
    ''' render form to create user profile, redirect to user profile page '''
