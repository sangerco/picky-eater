import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, Follows, User

os.environ['DATABASE_URI'] = "postgresql:///picky-eater-test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """ test users creation, register, and authentication functionalities """

    def setUp(self):
        """ create users """

        db.drop_all()
        db.create_all()

        self.client = app.test_client()


        u1 = User.register_user(first_name="test", last_name="tester", email="test@test.com", 
                                    username="test", password="password", image=None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.register_user(first_name="test2", last_name="tester2", email="test2@test.com", 
                                    username="test2", password="password", image=None)
        uid2 = 2222
        u2.id = uid2

        db.session.add_all([u1,u2])
        db.session.commit()

        u1 = User.query.get(uid1)
        self.u1 = u1
        self.uid1 = uid1

        u2 = User.query.get(uid2)
        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """ test user creation 
            user should exist but have no followers
            nor should they be following anyone """

        u = User(first_name="test",
                    last_name="user",
                    email="testuser@test.com",
                    username="testuser",
                    password="password",
                    image=None
                    )

        db.session.add(u)
        db.session.commit()

        self.assertIsNotNone(u)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)

    def test_register_user(self):
        """ does user register functionality work """

        u = User.register_user(first_name="test", last_name="user", email="test_user@test.com", 
                                username="test_user2", password="password", image=None)

        uid = 2323
        u.id = uid
        db.session.add(u)
        db.session.commit()

        u = User.query.get(uid)
        self.assertIsNotNone(u)
        self.assertEqual(u.username, "test_user2")
        self.assertEqual(u.email, "test_user@test.com")
        self.assertTrue(u.password.startswith("$2b$"))

    def test_register_no_username(self):
        """ can you register with no username """

        i = User.register_user("test", "user", "test_user@test.com", None, "password", None)
        i_id = 3434
        i.id = i_id
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.add(i)
            db.session.commit()

    def test_register_no_password(self):   
        """ can you register with no password """

        with self.assertRaises(ValueError) as context:
            User.register_user(first_name="test", last_name="user", email="test_user@test.com", 
                                username="tester_user", password=None, image=None)

    def test_register_invalid_password(self):   
        """ can you register with invalid password """

        with self.assertRaises(ValueError) as context:
            User.register_user(first_name="test", last_name="user", email="test_user@test.com", 
                                username="tester_user", password="", image=None)
                                
    def test_authenticate_user(self):
        """ test valid authentication """

        u = User.authenticate_user(username=self.u1.username, password="password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)

    def test_authenticate_bad_username(self):
        """ can you log in with bad username """

        self.assertFalse(User.authenticate_user(username="wrongname", password="password"))

    def test_authenticate_bad_password(self):
        """ can you log in with bad password """

        self.assertFalse(User.authenticate_user(username=self.u1.username, password="wrongpassword"))

    def test_is_following(self):
        """ test if user1 is following user 2 """

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 1)

        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)

    def test_follower(self):
        """ test if user2 is following user 1 """

        self.u2.following.append(self.u1)
        db.session.commit()

        self.assertTrue(self.u1.is_being_followed(self.u2))
        self.assertFalse(self.u2.is_being_followed(self.u1))
