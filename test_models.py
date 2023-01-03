import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, Follows, User, User_profile, Child_profile, Favorite_recipe
from models import Diet, Reply, Message

os.environ['DATABASE_URL'] = "postgresql:///picky-eater-test"

from app import app

db.create_all()

class OtherModelsTestCase(TestCase):
    """ test user profiles creation, edit, delete """

    def setUp(self):
        """ create users """
        db.drop_all()
        db.create_all()

        u1 = User.register_user("test", "tester", "test@test.com", "test", "password", None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.register_user("test2", "tester2", "test2@test.com", "test2", "password", None)
        uid2 = 2222
        u2.id = uid2

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

    
    def test_user_profile_model(self):
        """ test user profile creation """

        u1 = User.query.get(self.uid1)

        p = User_profile(user_id=u1.id,
                    owner=u1.username,
                    no_foods='carrots, apples',
                    yes_foods='hamburgers',
                    diet_id=1,
                    diet_name=None,
                    intolerances='dairy, eggs'
                    )

        db.session.add(p)
        db.session.commit()

        self.assertIsNotNone(p)
        self.assertEqual(p.owner, u1.username)
        self.assertEqual(p.no_foods, 'carrots, apples')
        self.assertNotEqual(p.yes_foods, 'pumpkins')
        self.assertEqual(p.diet_id, 1)
        self.assertNotEqual(p.diet_name, 'Gluten Free')
        self.assertEqual(p.intolerances, 'dairy, eggs')

    def test_child_profile_model(self):
        """ test chile profile creation """

        u1 = User.query.get(self.uid1)

        p = User_profile(user_id=u1.id, owner=u1.username,no_foods='carrots',yes_foods='hamburgers',
                                diet_id=1,diet_name=None,intolerances='eggs')
        p_id = 2222
        p.id = p_id
        db.session.add(p)
        db.session.commit()

        p1 = User_profile.query.get(p_id)

        cp = Child_profile(name='Test_child',
                            user_profile_id=p1.id,
                            user_id=u1.id,
                            no_foods='bananas, eggs',
                            yes_foods='beef, pork',
                            diet_id=9,
                            diet_name='Paleo',
                            intolerances='wheat')
        
        db.session.add(cp)
        db.session.commit()

        self.assertIsNotNone(cp)
        self.assertEqual(cp.name, 'Test_child')
        self.assertEqual(cp.user_profile_id, p1.id)
        self.assertEqual(cp.user_id, u1.id)
        self.assertEqual(p.no_foods, 'bananas, eggs')
        self.assertEqual(p.yes_foods, 'beef, pork')
        self.assertNotEqual(p.diet_id, 1)
        self.assertEqual(p.diet_name, 'Paleo')
        self.assertNotEqual(p.intolerances, 'dairy, eggs')     

    def test_fav_recipe_model(self):
        """ test creation of fav recipe """

        u1 = User.query.get(self.uid1)

        p = User_profile(user_id=u1.id, owner=u1.username,no_foods='carrots',yes_foods='hamburgers',
                                diet_id=1,diet_name=None,intolerances='eggs')
        p_id = 2222
        p.id = p_id
        db.session.add(p)
        db.session.commit()

        p1 = User_profile.query.get(p_id)  

        f = Favorite_recipe(user_profile_id=p1.id,
                            user_id=u1.id,
                            name='test fav',
                            image=None,
                            api_recipe_id=1234,
                            review="test review",
                            rating=3)

        db.session.add(f)
        db.session.commit()

        self.assertIsNotNone(f)
        self.assertEqual(f.user_profile_id, p1.id)
        self.assertEqual(f.user_id, u1.id)
        self.assertEqual(f.name, 'test fav')
        self.assertEqual(f.api_recipe_id, 1234)
        self.assertEqual(f.review, 'test review')
        self.assertNotEqual(f.rating, None)

    def test_message(self):
        """ test message model """

        u1 = User.query.get(self.uid1)
        u2 = User.query.get(self.uid2)

        self.u2.following.append(self.u1)
        db.session.commit()

        m = Message(recipe_name='test recipe',
                        api_recipe_id=2345,
                        user_id=u1.id,
                        username=u1.username,
                        follower=u2.id,
                        message='test message'
                        )
        db.session.add(m)
        db.session.commit()

        self.assertIsNotNone(m)
        self.assertEqual(m.recipe_name, 'test recipe')
        self.assertEqual(m.api_recipe_id, 2345)
        self.assertEqual(m.user_id, u1.id)
        self.assertEqual(m.username, u1.username)
        self.assertEqual(m.follower, u2.id)
        self.assertEqual(m.message, 'test message')
        self.assertIsNotNone(m.timestamp)

    def test_reply(self):
        """ test reply model """

        u1 = User.query.get(self.uid1)
        u2 = User.query.get(self.uid2)

        self.u2.following.append(self.u1)
        db.session.commit()

        m = Message(recipe_name='q',
                    api_recipe_id=22,
                    user_id=u1.id,
                    username=u1.username,
                    follower=u2.id,
                    message='w')

        m_id = 2222
        m.id = m_id
        db.session.add(m)
        db.session.commit()        

        m1 = Message.query.get(m.id)

        r = Reply(message_id=m1.id,
                    sender_id=u2.id,
                    sender_name=u2.username,
                    recipient_id=u1.id,
                    recipe_name='test recipe',
                    message='test message')

        db.session.add(r)
        db.session.commit()

        self.assertIsNotNone(r)
        self.assertEqual(r.message_id, m1.id)
        self.assertEqual(r.sender_id, u2.id)
        self.assertEqual(r.sender_name, u2.username)
        self.assertEqual(r.recipient_id, u1.id)
        self.assertEqual(r.recipe_name, 'test recipe')
        self.assertEqual(r.message, 'test message')
        self.assertIsNotNone(r.timestamp)
