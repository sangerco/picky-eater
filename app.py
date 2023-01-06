import os
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, User_profile, Child_profile
from models import Favorite_recipe, Follows, Diet, Message, Reply
from forms import NewUserForm, LoginForm, UserProfileForm, ChildProfileForm
from forms import FavoriteRecipeForm, ShareRecipeForm, ReplyForm
from sqlalchemy import desc
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

    user = User.query.get_or_404(user_id)
    user_profile = User_profile.query.filter_by(user_id = user_id).first()
    child_profiles = Child_profile.query.filter(Child_profile.user_id == user_id).all()
    favorite_recipes = Favorite_recipe.query.filter(Favorite_recipe.user_id == user_id).all()
    msgs = Message.query.filter(Message.follower == user_id).order_by(desc(Message.timestamp)).all()
    replies = Reply.query.filter(Reply.recipient_id == user_id).order_by(desc(Reply.timestamp)).all()

    return render_template('user-info.html', user=user, user_profile=user_profile, 
                child_profiles=child_profiles, following=user.following, 
                followers=user.followers, favorite_recipes=favorite_recipes, msgs=msgs,
                replies=replies)

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
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

@app.route('/users/delete/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    """ delete account """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/")

@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def follow_user(follow_id):
    """ find user in db, append to logged-in user's following list """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")    

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f'/users')

@app.route('/users/unfollow/<int:follow_id>', methods=['POST'])
def unfollow_user(follow_id):
    """ find user in db, remove from logged-in user's following list """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")    

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f'/users/{g.user.id}')

@app.route('/users/profile/<int:user_id>', methods=['GET', 'POST'])
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

        if profile.intolerances:
            intolerances_list = profile.intolerances.split()
        else:
            intolerances_list = []

        return render_template('user-profile.html', user=user, profile=profile,
                    child_profiles=child_profiles, no_foods=no_food_list, 
                    yes_foods=yes_food_list, diet=profile.diet_id, 
                    intolerances=intolerances_list)

    else:
        form = UserProfileForm()
        form.diet.choices = [(diet.id, diet.diet) for diet in Diet.query.all()]
        user = User.query.get_or_404(user_id)
        if form.validate_on_submit():
            no_foods = form.no_foods.data
            yes_foods = form.yes_foods.data
            diet = form.diet.data
            diet_name = Diet.query.get(diet).diet
            intolerances = form.intolerances.data


            new_profile = User_profile(user_id=user_id, owner=user.username, 
                    no_foods=no_foods, yes_foods=yes_foods, diet_id=diet, 
                    diet_name=diet_name, intolerances=intolerances)
            db.session.add(new_profile)
            db.session.commit()
            flash('Hooray! New profile added!', 'success')
            return redirect(f'/users/{user_id}')
        
    return render_template('user-profile.html', user=user, form=form)

@app.route('/users/profile/edit/<int:user_id>', methods=['GET','POST'])
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
        profile.intolerances = form.intolerances.data
        db.session.commit()
        flash(f"{user.username}'s profile edited", 'success')
        return redirect(f"/users/profile/{user.id}")

    return render_template('edit-profile.html', user=user, form=form)

@app.route('/users/child-profile/<int:user_id>/new', methods=['GET', 'POST'])
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
    profile = User_profile.query.filter_by(user_id = user.id).first()
    print(profile)
    user_profile_id = profile.id
    form = ChildProfileForm()
    form.diet.choices = [(diet.id, diet.diet) for diet in Diet.query.all()]
    if form.validate_on_submit():
        name = form.name.data
        no_foods = form.no_foods.data
        yes_foods = form.yes_foods.data
        diet = form.diet.data
        diet_name = Diet.query.get(diet).diet
        intolerances = form.intolerances.data

        new_profile = Child_profile(name=name, user_profile_id=user_profile_id, 
                user_id=user_id, no_foods=no_foods, yes_foods=yes_foods, diet_id=diet, 
                diet_name=diet_name, intolerances=intolerances)
        db.session.add(new_profile)
        db.session.commit()
        flash('Hooray! New profile added!', 'success')
        return redirect(f'/users/{user_id}')

    return render_template('add-child-profile.html', user=user, form=form)

@app.route('/profiles/child/<int:child_profile_id>')
def view_child_profile(child_profile_id):
    """ child profile page """

    profile = Child_profile.query.get_or_404(child_profile_id)
    id = Child_profile.query.get_or_404(child_profile_id).user_id
    user = User.query.get_or_404(id)

    if profile.no_foods:
        no_food_list = profile.no_foods.split()
    else:
        no_food_list = [] 

    if profile.yes_foods:
        yes_food_list = profile.yes_foods.split()
    else:
        yes_food_list = []

    if profile.intolerances:
        intolerances_list = profile.intolerances.split()
    else:
        intolerances_list = []

    

    return render_template('child-profile.html', profile=profile, user=user, no_foods=no_food_list, 
                    yes_foods=yes_food_list, intolerances=intolerances_list)

@app.route('/profiles/child/edit/<int:child_profile_id>', methods=['GET', 'POST'])
def edit_child_profile(child_profile_id):
    """ edit child profile page """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    if CURR_USER_KEY not in session:
        flash('Please log in first!', 'danger')
        return redirect('/')

    profile = Child_profile.query.get_or_404(child_profile_id)
    id = Child_profile.query.get_or_404(child_profile_id).user_id
    user = User.query.get_or_404(id)
    form = ChildProfileForm(obj=profile)
    form.diet.choices = [(diet.id, diet.diet) for diet in Diet.query.all()]
    if form.validate_on_submit():
        profile.name = form.name.data
        profile.no_foods = form.no_foods.data
        profile.yes_foods = form.yes_foods.data
        profile.diet_id = form.diet.data       
        profile.diet_name = Diet.query.get(profile.diet_id).diet
        profile.intolerances = form.intolerances.data
        db.session.commit()
        flash(f"Profile {profile.name} edited", 'success')
        return redirect(f"/profiles/child/{profile.id}")

    return render_template('edit-child-profile.html', profile=profile, user=user, form=form)

@app.route('/profiles/child/delete/<int:child_profile_id>', methods=['GET', 'POST'])
def delete_child_profile(child_profile_id):
    """ delete chile profile, redirect to user page """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    if CURR_USER_KEY not in session:
        flash('Please log in first!', 'danger')
        return redirect('/')

    profile = Child_profile.query.get_or_404(child_profile_id)
    id = Child_profile.query.get_or_404(child_profile_id).user_id
    user = User.query.get_or_404(id)

    db.session.delete(profile)
    db.session.commit()

    return redirect(f"/users/{user.id}")

@app.route('/users/profile/<int:user_id>/recipes', methods=['GET', 'POST'])
def show_user_recipe_results(user_id):
    """ parse from user profile
        run api call and parse returned data
        render returned template
        """

    user = User.query.get_or_404(user_id)
    profile = User_profile.query.filter_by(user_id = user_id).first()
    if profile.no_foods:
        no_food_list = profile.no_foods.split()
    else:
        no_food_list = []
    if profile.yes_foods:
        yes_food_list = profile.yes_foods.split()
    else:
        yes_food_list = []
    if profile.intolerances:
        intolerances_list = profile.intolerances.split()
    else:
        intolerances_list = []


    querystring = {'number':'25',
                    'includeIngredients':yes_food_list,
                    'excludeIngredients':no_food_list,
                    'diet':profile.diet_name,
                    'intolerances':intolerances_list,
                    'sort':'random'}

    res = requests.request('GET', URL + "recipes/complexSearch", headers=HEADERS, params=querystring).json()

    print(res)
    return render_template('recipe-results.html', user=user, recipes=res['results'])

@app.route('/profiles/child/<int:child_profile_id>/recipes', methods=['GET', 'POST'])
def show_child_recipe_results(child_profile_id):
    """ parse from user/child profile
        run api call and parse returned data
        render returned template
        """

    profile = Child_profile.query.get_or_404(child_profile_id)
    id = Child_profile.query.get_or_404(child_profile_id).user_id
    user = User.query.get_or_404(id)
    if profile.no_foods:
        no_food_list = profile.no_foods.split()
    else:
        no_food_list = []
    if profile.yes_foods:
        yes_food_list = profile.yes_foods.split()
    else:
        yes_food_list = []
    if profile.intolerances:
        intolerances_list = profile.intolerances.split()
    else:
        intolerances_list = []
    querystring = {'number':'25',
                    'includeIngredients':yes_food_list,
                    'excludeIngredients':no_food_list,
                    'diet':profile.diet_name,
                    'intolerances':intolerances_list,
                    'sort':'random'}

    res = requests.request('GET', URL + "recipes/complexSearch", headers=HEADERS, params=querystring).json()

    return render_template('recipe-results.html', user=user, recipes=res['results'])

@app.route('/recipes/<int:recipe_id>', methods=['GET', 'POST'])
def recipe_info_page(recipe_id):
    """ get recipe info from api
        display recipe info 
        """
    id = str(recipe_id)
    recipe_info_endpoint = "recipes/{0}/information".format(id)


    res = requests.request('GET', URL + recipe_info_endpoint, headers=HEADERS).json()

    return render_template('recipe.html', recipe=res)
    
@app.route('/recipes/<int:recipe_id>/favorite', methods=['GET', 'POST'])
def favorite_recipe(recipe_id):
    """ render form to review and rate recipe 
        send recipe info, review, and rating to db
        """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    if CURR_USER_KEY not in session:
        flash('Please log in first!', 'danger')
        return redirect('/')

    user = User.query.get_or_404(session[CURR_USER_KEY])
    profile = User_profile.query.filter_by(user_id = user.id).first()

    id = str(recipe_id)
    recipe_info_endpoint = "recipes/{0}/information".format(id)
    res = requests.request('GET', URL + recipe_info_endpoint, headers=HEADERS).json()

    form = FavoriteRecipeForm()
    if form.validate_on_submit():
        review = form.review.data
        rating = form.rating.data
        user_profile_id = profile.id
        user_id = user.id
        name = res['title']
        image = res['image']
        api_recipe_id = recipe_id

        fav_recipe = Favorite_recipe(user_profile_id=user_profile_id, user_id=user_id, 
                name=name, image=image, api_recipe_id=api_recipe_id, review=review, rating=rating)
        db.session.add(fav_recipe)
        db.session.commit()
        flash('Favorite recipe added.', 'success')
        return redirect(f'/recipes/{recipe_id}')

    return render_template('new-fav-recipe.html', recipe=res, form=form, 
                    user=user, profile=profile)

@app.route('/shares/<int:recipe_id>/share-recipe', methods=['GET', 'POST'])
def send_recipe(recipe_id):
    """ share recipe with following user """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    if CURR_USER_KEY not in session:
        flash('Please log in first!', 'danger')
        return redirect('/')

    user = User.query.get_or_404(session[CURR_USER_KEY])
    followers = User.query.get_or_404(session[CURR_USER_KEY]).followers
    for follower in followers:
        print(follower)

    id = str(recipe_id)
    recipe_info_endpoint = "recipes/{0}/information".format(id)
    res = requests.request('GET', URL + recipe_info_endpoint, headers=HEADERS).json()

    form = ShareRecipeForm()
    form.follower.choices = [(follower.id, follower.username) for follower in followers]
    print(form.follower.choices)
    if form.validate_on_submit():
        recipe_name = res['title']
        api_recipe_id = recipe_id   
        user_id = user.id
        username = user.username
        follower = form.follower.data
        message = form.message.data

        new_share = Message(recipe_name=recipe_name, api_recipe_id=api_recipe_id, 
                user_id=user_id, username=username, follower=follower, message=message)
        db.session.add(new_share)
        db.session.commit()
        flash('Recipe shared.', 'success')
        return redirect(f'/recipes/{recipe_id}')    

    return render_template('share.html', recipe=res, user=user, followers=followers, 
                            form=form)    

@app.route('/messages/delete/<int:message_id>', methods=['POST'])
def delete_message(message_id):
    """ delete individual message """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    if CURR_USER_KEY not in session:
        flash('Please log in first!', 'danger')
        return redirect('/')

    user = User.query.get_or_404(session[CURR_USER_KEY])
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()

    return redirect(f'/users/{user.id}')



@app.route('/messages/reply/<int:message_id>', methods=['GET', 'POST'])
def reply_to_message(message_id):
    """ reply to shared recipe message """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    if CURR_USER_KEY not in session:
        flash('Please log in first!', 'danger')
        return redirect('/')

    user = User.query.get_or_404(session[CURR_USER_KEY])
    message = Message.query.get_or_404(message_id)

    form = ReplyForm()
    if form.validate_on_submit():
        message_id = message.id
        sender_id = user.id
        sender_name = user.username
        recipient_id = message.user_id
        recipe_name = message.recipe_name
        message = form.message.data

        new_reply = Reply(message_id=message_id, sender_id=sender_id, sender_name=sender_name, 
                            recipient_id=recipient_id, recipe_name=recipe_name, message=message)
        db.session.add(new_reply)
        db.session.commit()       
        flash('Reply sent.', 'success')
        return redirect(f"/users/{user.id}")

    return render_template('reply.html', message=message, user=user, form=form)

@app.route('/replies/delete/<int:reply_id>', methods=['POST'])
def delete_reply(reply_id):
    """ functionality to delete individual reply """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect('/')

    if CURR_USER_KEY not in session:
        flash('Please log in first!', 'danger')
        return redirect('/')

    user = User.query.get_or_404(session[CURR_USER_KEY])
    reply = Reply.query.get_or_404(reply_id)   
    db.session.delete(reply)
    db.session.commit()

    return redirect(f'/users/{user.id}')      