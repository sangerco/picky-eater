from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class Follows(db.Model):
    """ provide table for potential friends """

    __tablename__ = "follows"

    user_being_followed_id = db.Column(
                    db.Integer, 
                    db.ForeignKey('users.id', ondelete='cascade'),
                    primary_key=True)
    user_following_id = db.Column(
                    db.Integer, 
                    db.ForeignKey('users.id', ondelete='cascade'),
                    primary_key=True)

class User(db.Model):
    """ create general user profile """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, default="/static/images/picky_eater.jpg")
    followers = db.relationship("User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )
    following = db.relationship("User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )

    @classmethod
    def register_user(cls, first_name, last_name, email, username, password, image):
        """ register user with hashed password """

        hashed_password = bcrypt.generate_password_hash(password)
        # below method changes bytestring created by bcrypt into utf8 string
        hashed_utf8 = hashed_password.decode("utf8")

        return cls(first_name=first_name, last_name=last_name, email=email, 
                    username=username, password=hashed_utf8, image=image)

    @classmethod
    def authenticate_user(cls, username, password):
        """ check that user and password are valid 
        
            return user if valid, return False if not """

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

    def is_being_followed(self, other_user):
        """ are two users 'friends'? """

        followed_list = [user for user in self.followers if user == other_user ]
        return len(followed_list) == 1

    def is_following(self, other_user):
        """ are two users 'friends'? """

        following_list = [user for user in self.following if user == other_user ]
        return len(following_list) == 1

class Diet(db.Model):
    ''' simple table for diet select field on profiles pages '''

    __tablename__ = 'diets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    diet = db.Column(db.Text, unique=True)

class User_profile(db.Model):
    """ generate table for user likes and dislikes """

    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    owner = db.Column(db.Text, db.ForeignKey('users.username', ondelete='cascade'))
    no_foods = db.Column(db.Text, default=None)
    yes_foods = db.Column(db.Text, default=None)
    diet_id = db.Column(db.Integer, default=None)
    diet_name = db.Column(db.Text, db.ForeignKey('diets.diet'))


class Child_profile(db.Model):
    """ generate table for profiles that are children of user profile """

    __tablename__ = 'child_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    user_profile_id = db.Column(
                        db.Integer, 
                        db.ForeignKey('user_profiles.id', ondelete='cascade')
                        )
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    no_foods = db.Column(db.Text, default=None)
    yes_foods = db.Column(db.Text, default=None)
    diet_id = db.Column(db.Integer, default=None)
    diet_name = db.Column(db.Text, db.ForeignKey('diets.diet', ondelete='cascade'))


class Favorite_recipe(db.Model):
    """ provide table for user's favorite recipes """

    __tablename__ = 'favorite_recipes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_profile_id = db.Column(
                        db.Integer, 
                        db.ForeignKey('user_profiles.id', ondelete='cascade')
                        )
    user_id = db.Column(
                    db.Integer,
                    db.ForeignKey('users.id', ondelete='cascade')
                    )
    name = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text)
    api_recipe_id = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text)
    rating = db.Column(db.Integer, default=None)


class Shopping_list(db.Model):
    """ provide table for shopping list """

    __tablename__ = 'shopping_lists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_profile_id = db.Column(
                        db.Integer, 
                        db.ForeignKey('user_profiles.id', ondelete='cascade')
                        )
    api_shopping_list_id = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

class Message(db.Model):
    """ provide functionality for sending recipes to following user """

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_name = db.Column(db.Text, nullable=False)
    api_recipe_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(
                        db.Integer,
                        db.ForeignKey('users.id', ondelete='cascade')
                        )
    follower = db.Column(
                        db.Integer,
                        db.ForeignKey('users.id', ondelete='cascade')
                        )
    message = db.Column(db.Text)