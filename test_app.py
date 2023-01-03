import os
from unittest import TestCase
from sqlalchemy import exc
import requests

from models import db, Follows, User, User_profile, Child_profile, Favorite_recipe
from models import Diet, Reply, Message


os.environ['DATABASE_URL'] = "postgresql:///picky-eater-test"

from app import app, CURR_USER_KEY, URL, API_HOST, API_SECRET_KEY, HEADERS

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class TestUserFunctionsTestCase(TestCase):
    """ test for user funcionalities """

    def setUp(self):
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.register_user(first_name="test",
                                            last_name="user",
                                            email="test@test.com",
                                            username="testuser",
                                            password="password",
                                            image=None)
        self.testuser_id = 1234
        self.testuser.id = self.testuser_id
        self.u1 = User.register_user(first_name="test1",
                                            last_name="user1",
                                            email="test1@test.com",
                                            username="testuser1",
                                            password="password",
                                            image=None)
        self.u1_id = 2345
        self.u1.id = self.u1_id
        self.u2 = User.register_user(first_name="test2",
                                            last_name="user2",
                                            email="test2@test.com",
                                            username="testuser2",
                                            password="password",
                                            image=None)
        self.u2_id = 3456
        self.u2.id = self.u2_id
        self.u3 = User.register_user(first_name="test3",
                                            last_name="user3",
                                            email="test3@test.com",
                                            username="testuser3",
                                            password="password",
                                            image=None)
        self.u3_id = 4567
        self.u3.id = self.u3_id
        self.u4 = User.register_user(first_name="test4",
                                            last_name="user4",
                                            email="test4@test.com",
                                            username="testuser4",
                                            password="password",
                                            image=None)
        self.u4_id = 4567
        self.u4.id = self.u4_id
        db.session.commit()

        follow_u1 = User.query.get(self.u1.id)
        self.testuser.following.append(follow_u1)  
        follow_u2 = User.query.get(self.u2.id)
        self.testuser.following.append(follow_u2)
        db.session.commit()


    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_view_all_users(self):
        """ view all users page should show all 5 users """

        with self.client as c:
            res = c.get('/users')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('@testuser', html)
            self.assertIn('@testuser1', html)
            self.assertIn('@testuser2', html)
            self.assertIn('@testuser3', html)
            self.assertIn('@testuser4', html)

    def test_user_view(self):
        """ test individual user page """

        with self.client as c:
            res = c.get(f'/users/{self.testuser.id}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('testuser', html)
            self.assertIn('@testuser1', html)
            self.assertIn('@testuser2', html)
            self.assertIn("testuser's Profile", html)

    def test_edit_user(self):
        """ test to edit user """

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            user = {"first_name": "edited_test", "last_name": "user", "email": "testuser@testuser.com", 'username': "testuser", "image":None}
            res = c.post(f'/users/edit/{self.testuser.id}', data = user, follow_redirects=True)
            
            testuser = User.query.get(self.testuser.id)

            self.assertEqual(res.status_code, 200)
            self.assertEqual(testuser.first_name, 'edited_test')
            self.assertEqual(testuser.email, 'testuser@testuser.com')
            self.assertEqual(testuser.username, 'testuser')

    def test_edit_user_not_logged_in(self):
        ''' try to edit user when not logged in '''

        with self.client as c:
            user = {"first_name": "edited_test", "last_name": "user", "email": "testuser@testuser.com", 'username': "testuser", "image":None}
            res = c.post(f'/users/edit/{self.testuser.id}', data = user, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Please log in first!', html)

    def test_edit_wrong_user(self):
        ''' try to edit other user's account '''

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = 999999
            
            user = {"first_name": "edited_test", "last_name": "user", "email": "testuser@testuser.com", 'username': "testuser", "image":None}
            res = c.post(f'/users/edit/{self.testuser.id}', data = user, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized', html)

    def test_delete_user(self):
        """ test to delete user """

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = self.testuser_id


            res = c.get(f'/users/delete/{self.u4_id}', follow_redirects=True)
            
            u4 = User.query.get(self.u4_id)

            self.assertEqual(res.status_code, 200)
            self.assertIsNone(u4)
            
            resp = c.get('/users')
            html = resp.get_data(as_text=True)

            self.assertNotIn('testuser4', html)

    def test_delete_user_not_logged_in(self):
        ''' try to delete user when not logged in '''

        with self.client as c:
            res = c.get(f'/users/delete/{self.u4_id}', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Please log in first!', html)

    def test_delete_wrong_user(self):
        ''' try to delete other user '''

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = 999999

            res = c.get(f'/users/delete/{self.u4_id}', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', html)                        

    def setup_followers(self):
        ''' setup follower connections to test follow functionality '''

        f1 = Follows(user_being_followed_id=self.u1.id, user_following_id=self.testuser.id)
        f2 = Follows(user_being_followed_id=self.u2.id, user_following_id=self.testuser.id)

        db.session.add_all([f1,f2])
        db.session.commit()

    def test_show_followers(self):
        ''' test if followers show on user page '''

        self.setup_followers()

        with self.client as c:
            res = c.get(f'/users/{self.testuser.id}')
            html = res.get_data(as_text=True)

            self.assertIn('@testuser1', html)
            self.assertIn('@testuser2', html)

    def test_unfollow(self):
        ''' test unfollow functionality '''

        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            res = c.post(f"/users/unfollow/{self.u1.id}", follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 302)
            self.assertNotIn('@testuser1', html)
    
    def setup_user_profile(self):
        ''' set up profile to test user profile page '''

        self.p = User_profile(user_id=self.testuser.id, owner=self.testuser.username, no_foods='no, foods', 
                            yes_foods='yes_foods', diet_id=2, diet_name='Gluten Free', intolerances='intolerances')

        self.p_id = 1234
        self.p.id = self.p_id
        
        db.session.add(self.p)
        db.session.commit()

    def test_user_profile(self):
        ''' test user profile view '''

        self.setup_user_profile()

        with self.client as c:
            res = c.get(f"/users/profile/{self.testuser.id}")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("testuser's Profile", html)
            self.assertIn("no", html)
            self.assertIn("foods", html)
            self.assertIn("yes", html)
            self.assertIn("Gluten Free", html)
            self.assertIn("intolerances", html)

    def test_create_user_profile(self):
        ''' test create user profile ''' 

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u2_id

            profile = {'user_id':3456, 'owner': 'testuser2', 'no_foods': 'apple', 'yes_foods': 'rice', 'diet_id':3,
                    'diet_name':'Ketogenic', 'intolerances':'soy'}
            res = c.post(f"/users/profile/3456", data = profile)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("testuser2's Profile", html)
            self.assertIn("apple", html)
            self.assertIn("rice", html)
            self.assertIn("Ketogenic", html)
            self.assertIn("soy", html)

    def test_create_user_profile_not_logged_in(self):
        ''' try to create user profile when not logged in '''

        with self.client as c:
            profile = {'user_id':3456, 'owner': 'testuser2', 'no_foods': 'apple', 'yes_foods': 'rice', 'diet_id':3,
                    'diet_name':'Ketogenic', 'intolerances':'soy'}
            res = c.post(f"/users/profile/3456", data = profile)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Please log in first!', html)

    def test_create_user_profile_wrong_user(self):
        ''' try to create a user profile for not logged in user '''

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = 999999

            profile = {'user_id':3456, 'owner': 'testuser2', 'no_foods': 'apple', 'yes_foods': 'rice', 'diet_id':3,
                    'diet_name':'Ketogenic', 'intolerances':'soy'}
            res = c.post(f"/users/profile/3456", data = profile)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized', html)                        

    def test_edit_user_profile(self):
        ''' test edit user profile functionality '''

        self.setup_user_profile()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            new_profile = {"user_id":1234, "owner":"testuser", "no_foods":'tacos', 
                            "yes_foods":'pizza', "diet_id":2, "diet_name":'Gluten Free', "intolerances":'wheat'}
            res = c.post(f"/users/profile/edit/{self.testuser.id}", data = new_profile, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertIn('tacos', html)
            self.assertIn('pizza', html)
            self.assertIn('wheat', html)

    def test_edit_user_profile_not_logged_in(self):
        ''' test to edit user profile when not logged in '''

        self.setup_user_profile()

        with self.client as c:

            new_profile = {"user_id":1234, "owner":"testuser", "no_foods":'tacos', 
                            "yes_foods":'pizza', "diet_id":2, "diet_name":'Gluten Free', "intolerances":'wheat'}
            res = c.post(f"/users/profile/edit/{self.testuser.id}", data = new_profile, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Please log in first!', html)

    def test_edit_wrong_user_profile(self):
        ''' test to edit user profile of other user '''

        self.setup_user_profile()

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = 999999

            new_profile = {"user_id":1234, "owner":"testuser", "no_foods":'tacos', 
                            "yes_foods":'pizza', "diet_id":2, "diet_name":'Gluten Free', "intolerances":'wheat'}
            res = c.post(f"/users/profile/edit/{self.testuser.id}", data = new_profile, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized', html)

    def setup_child_profile(self):
        ''' setup chile profile to test functionality '''

        self.setup_user_profile()

        self.cp = Child_profile(name='testchild', user_profile_id=self.p.id, user_id=self.testuser.id, no_foods='no, foods', 
                            yes_foods='yes_foods', diet_id=2, diet_name='Gluten Free', intolerances='intolerances')
        
        self.cp_id = 1234
        self.cp.id = self.cp_id

        db.session.add(self.cp)
        db.session.commit()

    def test_child_profile(self):
        ''' test child profile view '''

        self.setup_child_profile()

        with self.client as c:
            res = c.get(f'/profile/child/{self.cp.id}')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("testchild", html)
            self.assertIn("no", html)
            self.assertIn("foods", html)
            self.assertIn("yes", html)
            self.assertIn("Gluten Free", html)
            self.assertIn("intolerances", html)

    def test_create_child_profile(self):
        ''' test to create new child profile '''

        self.setup_user_profile()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            child = {'id':123, 'name':'testchild2','user_profile_id':1234, 'owner':1234, 'no_foods':'apple', 'yes_foods':'rice', 'diet_id':3,
                    'diet_name':'Ketogenic', 'intolerances':'soy'}

            res = c.post(f'/users/child-profile/{self.testuser_id}/new', data=child, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 302)
            self.assertIn("testchild2", html)
            self.assertIn("apple", html)
            self.assertIn('rice', html)
            self.assertIn('Ketogenic', html)
            self.assertIn('soy', html)

    def test_create_child_profile_not_logged_in(self):
        ''' try to create child profile while not logged in '''

        self.setup_user_profile()

        with self.client as c:
            child = {'id':123, 'name':'testchild2','user_profile_id':1234, 'owner':1234, 'no_foods':'apple', 'yes_foods':'rice', 'diet_id':3,
                    'diet_name':'Ketogenic', 'intolerances':'soy'}

            res = c.post(f'/users/child-profile/{self.testuser_id}/new', data=child, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Please log in first!', html)            

    def test_create_child_profile_wrong_user(self):
        ''' try to create chile profile for wrong user '''

        self.setup_user_profile()

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = 999999
            child = {'id':123, 'name':'testchild2','user_profile_id':1234, 'owner':1234, 'no_foods':'apple', 'yes_foods':'rice', 'diet_id':3,
                    'diet_name':'Ketogenic', 'intolerances':'soy'}

            res = c.post(f'/users/child-profile/{self.testuser_id}/new', data=child, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', html)               

    def test_edit_child_profile(self):
        """ test edit child profile functionality """

        self.setup_child_profile()

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            new_child = {'name':'testchild','user_profile_id':1234, 'owner':1234, 'no_foods':'noodles', 'yes_foods':'potatoes', 'diet_id':3,
                        'diet_name':'Ketogenic', 'intolerances':'soy'}

            res = c.post(f'/profiles/child/edit/{self.cp_id}', data=new_child, follow_redirects=True)
            html = res.get_data(as_text=True)
        
            self.assertEqual(res.status_code, 302)
            self.assertIn("noodles", html)
            self.assertIn('potatoes', html)

    def test_edit_child_profile_not_logged_in(self):
        ''' try to edit child profile while not logged in '''

        self.setup_child_profile()

        with self.client as c:
            new_child = {'name':'testchild','user_profile_id':1234, 'owner':1234, 'no_foods':'noodles', 'yes_foods':'potatoes', 'diet_id':3,
                        'diet_name':'Ketogenic', 'intolerances':'soy'}

            res = c.post(f'/profiles/child/edit/{self.cp_id}', data=new_child, follow_redirects=True)
            html = res.get_data(as_text=True)       

            self.assertEqual(res.status_code, 200)
            self.assertIn('Please log in first!', html)     

    def test_edit_child_profile_wrong_user(self):
        ''' try to edit other user's child profile '''

        self.setup_child_profile()

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = 999999

            new_child = {'name':'testchild','user_profile_id':1234, 'owner':1234, 'no_foods':'noodles', 'yes_foods':'potatoes', 'diet_id':3,
                        'diet_name':'Ketogenic', 'intolerances':'soy'}

            res = c.post(f'/profiles/child/edit/{self.cp_id}', data=new_child, follow_redirects=True)
            html = res.get_data(as_text=True)       

            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', html)
         
    def test_delete_child_profile(self):
        """ test delete child profile functionality """

        self.setup_child_profile()
        cp = Child_profile.get_or_404(self.cp_id)

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = c.get(f'/profiles/child/delete/{self.cp_id}', follow_redirects=True)
            
            self.assertEqual(res.status_code, 302)
            self.assertIsNone(cp)

    def test_delete_child_profile_not_logged_in(self):
        ''' try to delete child profile while not logged in '''

        self.setup_child_profile()
        cp = Child_profile.get_or_404(self.cd_id)

        with self.client as c:
            res = c.get(f'/profiles/child/delete/{self.cp_id}', follow_redirects=True)
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn('Please log in first!', html)

    def test_delete_child_profile_wrong_user(self):
        ''' try to delete other user's child profile '''

        self.setup_child_profile()
        cp = Child_profile.get_or_404(self.cd_id)

        with self.client as c:
            res = c.get(f'/profiles/child/delete/{self.cp_id}', follow_redirects=True)
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', html)

    def test_get_recipes(self):
        ''' test get recipes functionality '''

        self.setup_user_profile()

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = c.get(f'/users/profile/{self.testuser_id}/recipes')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('http://spoonacular.com', html)

    def setup_fav_recipe(self):
        ''' set up favorite recipe for testing '''

        self.fr = Favorite_recipe(user_profile_id=self.p_id, user_id=self.testuser_id, name='test', api_recipe_id=1,
                                    review='review', rating=1)
        self.fr_id=123
        self.fr.id=self.fr_id
        db.session.add(self.fr)
        db.session.commit()

    def test_view_recipe(self):
        ''' test to view recipe '''

        with self.client as c:

            res = c.get(f'/recipes/1')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Fried Anchovies with Sage', html)
            self.assertIn('Favorite', html)
            self.assertIn('Share', html)

    def test_favorite_recipe_view(self):
        ''' test favorite recipe page '''

        self.setup_fav_recipe()

        with self.client as c:

            res = c.get(f"/recipes/{self.fr.api_recipe_id}/favorite")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Did you like Fried Anchovies with Sage?', html)
            self.assertIn('<label for="review">Review this recipe:</label>', html)

    def test_favorite_recipe(self):
        ''' test favorite recipe functionality '''

        self.setup_fav_recipe()

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = c.get(f'/users/{self.testuser_id}')
            html = res.get_data(as_text=True)

            self.assertIn('Fried Anchovies with Sage', html)
            self.assertIn('review', html)
            self.assertIn('I rated this a 1!', html)

    def test_share_recipe(self):
        ''' test share functionality '''

        self.setup_fav_recipe()

        share = {"recipe_name":"test", "api_recipe_id":self.fr.api_recipe_id, "user_id":self.testuser_id, 'name':self.testuser.username,
                    'follower':self.u1_id, 'message':'test', 'timestamp':'2022-12-28 23:59:17.141553'}

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = c.post(f'/shares/{self.fr.api_recipe_id}/share-recipe', data=share)

            self.assertEqual(res.status_code, 302)

            share = Message.query.one()
            self.assertEqual(share.message, "test")

    def test_share_recipe_not_logged_in(self):
        ''' try to share recipe while not logged in '''

        self.setup_fav_recipe

        share = {"recipe_name":"test", "api_recipe_id":self.fr.api_recipe_id, "user_id":self.testuser_id, 'name':self.testuser.username,
                    'follower':self.u1_id, 'message':'test', 'timestamp':'2022-12-28 23:59:17.141553'}

        with self.client as c:
            res = c.post(f'/shares/{self.fr.api_recipe_id}/share-recipe', data=share)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Please log in first!', html)

    def test_share_recipe_wrong_user(self):
        ''' try to share recipe from other user's account '''

        self.setup_fav_recipe

        share = {"recipe_name":"test", "api_recipe_id":self.fr.api_recipe_id, "user_id":self.testuser_id, 'name':self.testuser.username,
                    'follower':self.u1_id, 'message':'test', 'timestamp':'2022-12-28 23:59:17.141553'}

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = 999999

            res = c.post(f'/shares/{self.fr.api_recipe_id}/share-recipe', data=share)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Access unauthorized.', html)

    def setup_messages_and_reply(self):
        ''' create message to test reply
            create reply '''

        self.m1 = Message(recipe_name='test', api_recipe_id=1, user_id=self.u1_id, username=self.u1.username, 
                            follower=self.testuser_id, message='test message', timestamp='2023-01-02 17:20:46.045113')
        self.m1_id = 111
        self.m1.id = self.m1_id

        self.m2 - Message(recipe_name='test recipe', api_recipe_id=2, user_id=self.testuser_id, username=self.testuser.username,
                            follower=self.u1_id, message='test message', timestamp='2023-01-02 17:22:46.045113')
        self.m2_id = 222
        self.m2.id = self.m2_id

        db.session.add_all([self.m1, self.m2_id])
        db.session.commit()

        self.r = Reply(message_id=self.m1_id, sender_id=self.testuser_id, sender_name=self.testuser.username, recipient_id=self.u1_id,
                        recipe_name="test", message='test message', timestamp='2023-01-02 17:21:46.045113')
        self.r_id = 123
        self.r.id = self.r_id
        db.session.add(self.r)
        db.session.commit()

    def test_reply(self):
        ''' test reply view '''

        self.setup_messages_and_reply()

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = self.u1_id

            res = c.get(f"/users/{self.u1_id}")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(f'{self.testuser.username} replied to your share of this recipe:', html)
            self.assertIn(f'{self.r.recipe_name}', html)
            self.assertIn(f'{self.r.message}', html)

    def test_user_view_not_logged_in(self):
        ''' try to view user's messages and replies not logged in  '''

        self.setup_messages_and_reply()

        with self.client as c:

            res = c.get(f'/users/{self.u1_id}')
            html = res.get_data(as_text=True)

            self.assertNotIn(f'{self.testuser.username} replied to your share of this recipe:', html)
            self.assertNotIn(f'{self.testuser.username} has shared a recipe with you.', html)
            

    

        



            
            

