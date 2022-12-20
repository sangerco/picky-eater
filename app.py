from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, User_profile, Child_profile
from models import Favorite_recipe, Follows, Shopping_list, Diet
from forms import NewUserForm, LoginForm, UserProfileForm, ChildProfileForm
from sqlalchemy.exc import IntegrityError
import requests

CURR_USER_KEY = 'curr_user'


app = Flask(__name__)

URL = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/"
API_HOST = "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
API_SECRET_KEY = "d5d3480381msh53bfc1010a93e4dp163156jsn7ec3fa2fb72f"
HEADERS = {
  'x-rapidapi-host': API_HOST,
  'x-rapidapi-key': API_SECRET_KEY,
  }

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
        email = form.email.data
        username = form.username.data
        password = form.password.data
        image = form.image.data

        new_user = User.register_user(first_name, last_name, email, username, password, image)

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
            do_login(user)
            flash(f'Welcome back, {user.username}!', 'primary')
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

    joke = str(requests.request('GET', URL + "food/jokes/random", headers=HEADERS).json()['text'])
    user = User.query.get_or_404(user_id)
    user_profile = User_profile.query.filter_by(user_id = user_id).first()
    child_profiles = Child_profile.query.filter(Child_profile.user_id == user_id).all()
    favorite_recipes = Favorite_recipe.query.filter(Favorite_recipe.user_id == user_id).all()

    return render_template('user-info.html', joke=joke,
                user=user, user_profile=user_profile, 
                child_profiles=child_profiles, favorite_recipes=favorite_recipes)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_account(user_id):
    """ render form to edit account """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    if CURR_USER_KEY not in session:
        flash('Please log in first!', 'danger')
        return redirect('/')

    user = User.query.get_or_404(session[CURR_USER_KEY])
    form = NewUserForm(obj=user)
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.username = form.username.data
        user.image = form.image.data
        db.session.commit()
        flash(f"Account for {user.username} edited.", 'success')
        return redirect(f"/users/{user.id}")

    return render_template('edit-account.html', user=user, form=form)

@app.route('/users/<int:user_id>/delete', methods=['GET', 'POST'])
def delete_user(user_id):
    """ delete account """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/")


@app.route('/users/<int:user_id>/profile', methods=['GET', 'POST'])
def user_profile_page(user_id):
    """ display user profile page
        if no profile yet, display form to create new profile """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    if CURR_USER_KEY not in session:
        flash('Please log in first!', 'danger')
        return redirect('/')

    user = User.query.get_or_404(user_id)
    profile = User_profile.query.filter_by(user_id = user_id).first()
    if profile:
        child_profiles = Child_profile.query.filter(Child_profile.user_id == user_id).all()

        if profile.no_foods:
            # no_food_list = [nf for nf in profile.no_foods]
            no_food_list = profile.no_foods.split()
        else:
            no_food_list = [] 

        if profile.yes_foods:
            # yes_food_list = [yf for yf in profile.yes_foods]
            yes_food_list = profile.yes_foods.split()
        else:
            yes_food_list = []

        return render_template('user-profile.html', user=user, profile=profile,
                    child_profiles=child_profiles, no_foods=no_food_list, 
                    yes_foods=yes_food_list, diet=profile.diet_id)

    else:
        form = UserProfileForm()
        form.diet.choices = [(diet.id, diet.diet) for diet in Diet.query.all()]
        user = User.query.get_or_404(user_id)
        if form.validate_on_submit():
            no_foods = form.no_foods.data
            yes_foods = form.yes_foods.data
            diet = form.diet.data
            diet_name = Diet.query.get(diet).diet


            new_profile = User_profile(user_id=user_id, owner=user.username, 
                    no_foods=no_foods, yes_foods=yes_foods, diet_id=diet, 
                    diet_name=diet_name)
            db.session.add(new_profile)
            db.session.commit()
            flash('Hooray! New profile added!', 'success')
            return redirect(f'/users/{user_id}')
        
    return render_template('user-profile.html', user=user, form=form)

@app.route('/users/<int:user_id>/profile/edit', methods=['GET','POST'])
def edit_user_profile(user_id):
    """ render form to edit user profile
        redirect to user page """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    if CURR_USER_KEY not in session:
        flash('Please log in first!', 'danger')
        return redirect('/')

    user = User.query.get_or_404(session[CURR_USER_KEY])
    profile = User_profile.query.filter_by(user_id = user.id).first()
    form = UserProfileForm(obj=profile)
    form.diet.choices = [(diet.id, diet.diet) for diet in Diet.query.all()]
    if form.validate_on_submit():
        profile.no_foods = form.no_foods.data
        profile.yes_foods = form.yes_foods.data
        profile.diet_id = form.diet.data       
        profile.diet_name = Diet.query.get(profile.diet_id).diet
        db.session.commit()
        flash(f"{user.username}'s profile edited", 'success')
        return redirect(f"/users/{user.id}/profile")

    return render_template('edit-profile.html', user=user, form=form)

@app.route('/users/<int:user_id>/child-profile/new', methods=['GET', 'POST'])
def create_child_profile(user_id):
    ''' render form to create child profile, 
        redirect to user profile page '''

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    if CURR_USER_KEY not in session:
        flash('Please log in first!', 'danger')
        return redirect('/')

    user = User.query.get_or_404(user_id)
    user_profile_id = User_profile.query.filter_by(user_id = user_id).first().id
    form = ChildProfileForm()
    form.diet.choices = [(diet.id, diet.diet) for diet in Diet.query.all()]
    if form.validate_on_submit():
        name = form.name.data
        no_foods = form.no_foods.data
        yes_foods = form.yes_foods.data
        diet = form.diet.data
        diet_name = Diet.query.get(diet).diet

        new_profile = Child_profile(name=name, user_profile_id=user_profile_id, 
                user_id=user_id, no_foods=no_foods, yes_foods=yes_foods, diet_id=diet, 
                diet_name=diet_name)
        db.session.add(new_profile)
        db.session.commit()
        flash('Hooray! New profile added!', 'success')
        return redirect(f'/users/{user_id}')

    return render_template('add-child-profile.html', user=user, form=form)

@app.route('/profiles/child/<int:child_profile_id>')
def view_child_profile(child_profile_id):
    """ child profile page """

    profile = Child_profile.query.get_or_404(child_profile_id)
    id = Child_profile.query.get_or_404(child_profile_id).users.id
    user = User.query.get_or_404(id)

    if profile.no_foods:
        no_food_list = profile.no_foods.split()
    else:
        no_food_list = [] 

    if profile.yes_foods:
        yes_food_list = profile.yes_foods.split()
    else:
        yes_food_list = []

    

    return render_template('child-profile.html', profile=profile, user=user, no_foods=no_food_list, 
                    yes_foods=yes_food_list)

@app.route('/profiles/child/<int:child_profile_id>/edit', methods=['GET', 'POST'])
def edit_child_profile(child_profile_id):
    """ edit child profile page """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    if CURR_USER_KEY not in session:
        flash('Please log in first!', 'danger')
        return redirect('/')

    profile = Child_profile.query.get_or_404(child_profile_id)
    id = Child_profile.query.get_or_404(child_profile_id).users.id
    user = User.query.get_or_404(id)
    form = ChildProfileForm(obj=profile)
    form.diet.choices = [(diet.id, diet.diet) for diet in Diet.query.all()]
    if form.validate_on_submit():
        profile.name = form.name.data
        profile.no_foods = form.no_foods.data
        profile.yes_foods = form.yes_foods.data
        profile.diet_id = form.diet.data       
        profile.diet_name = Diet.query.get(profile.diet_id).diet
        db.session.commit()
        flash(f"Profile {profile.name} edited", 'success')
        return redirect(f"/profiles/child/{profile.id}")

    return render_template('edit-child-profile.html', profile=profile, user=user, form=form)

@app.route('/profiles/child/<int:child_profile_id>/delete', methods=['GET', 'POST'])
def delete_child_profile(child_profile_id):
    """ delete chile profile, redirect to user page """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    if CURR_USER_KEY not in session:
        flash('Please log in first!', 'danger')
        return redirect('/')

    profile = Child_profile.query.get_or_404(child_profile_id)
    id = Child_profile.query.get_or_404(child_profile_id).users.id
    user = User.query.get_or_404(id)

    db.session.delete(profile)
    db.session.commit()

    return redirect(f"/users/{user.id}")