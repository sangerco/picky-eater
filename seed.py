from models import db, Follows, User, User_profile, Child_profile, Favorite_recipe
from models import Diet, Intolerance
from app import app

db.drop_all()
db.create_all()

Diet.query.delete()

n = Diet(diet=None)
gf = Diet(diet='Gluten Free')
k = Diet(diet='Ketogenic')
v = Diet(diet='Vegetarian')
lv = Diet(diet='Lacto-Vegetarian')
ov = Diet(diet='Ovo-Vegetarian')
vegan = Diet(diet='Vegan')
p = Diet(diet='Pescetarian')
paleo = Diet(diet='Paleo')
primal = Diet(diet='Primal')
low = Diet(diet='Low FODMAP')
w = Diet(diet='Whole30')

db.session.add_all([n, gf,k,v,lv,ov,vegan,p,paleo,primal,low,w])
db.session.commit()

Intolerance.query.delete()

dairy = Intolerance(code='dry',intolerance='dairy')
egg = Intolerance(code='egg',intolerance='egg')
gluten = Intolerance(code='gtn',intolerance='gluten')
grain = Intolerance(code='grn',intolerance='grain')
peanut = Intolerance(code='pnt',intolerance='peanut')
seafood = Intolerance(code='sfd',intolerance='seafood')
sesame = Intolerance(code='ssm',intolerance='sesame')
shellfish = Intolerance(code='slf',intolerance='shellfish')
soy = Intolerance(code='soy',intolerance='soy')
sulfite = Intolerance(code='sul',intolerance='sulfite')
tree_nut = Intolerance(code='tnt',intolerance='tree_nut')
wheat = Intolerance(code='wht',intolerance='wheat')

db.session.add_all([dairy, egg, gluten, grain, peanut, seafood, sesame, shellfish, soy, sulfite, tree_nut, wheat])
db.session.commit()

User.query.delete()

d = User.register_user("Dan", "Sanger", "sangerco@yahoo.com", "dan", "password", None)
p = User.register_user("Philly", "Phil", 'philly@phil.com', 'philly_phil', 'password', None)
ca = User.register_user('Cassie', 'TheCat', 'cassiethecat@meowmeow.com', 'cassie_the_cat', 'password', None)
ch = User.register_user("Charlie", 'TheDog', 'charlie_the_dog@arfarf.org', 'charlie_the_dog', 'password', None)

db.session.add_all([d,p,ca,ch])
db.session.commit()

User_profile.query.delete()

d = User_profile(user_id=1, owner='dan', no_foods='zucchini, squash', yes_foods='pork, potatoes, brussels sprouts', diet_id=2, diet_name='Gluten Free', intolerances='gluten, wheat')
p = User_profile(user_id=2, owner='philly_phil', no_foods='beef, chicken, pork', yes_foods='tofu, broccoli', diet_id=7, diet_name='Vegan', intolerances='grain, wheat, gluten, dairy, eggs')
ca = User_profile(user_id=3, owner='cassie_the_cat', no_foods='lettuce, kale, chard, spinach, cabbage', yes_foods='fish, chicken', diet_id=10, diet_name='Primal')
ch = User_profile(user_id=4, owner='charlie_the_dog', no_foods='lettuce, kale, chard, spinach, cabbage', yes_foods='beef, chicken, pork, fish', diet_id=3, diet_name='Ketogenic', intolerances='grain, peanut, soy')

db.session.add_all([d,p,ca,ch])
db.session.commit()

Child_profile.query.delete()

c = Child_profile(name='Carl', user_profile_id=2, user_id=2, no_foods='beef, chicken, pork, squash, cheese', yes_foods='carrots, potatoes, tofu', diet_id=7, diet_name='Vegan', intolerances='grain, wheat, gluten, dairy, eggs')
b = Child_profile(name='Brutus', user_profile_id=3, user_id=3, no_foods='lettuce, kale, chard, spinach, cabbage', yes_foods='fish, chicken, beef, pork', diet_id=10, diet_name='Primal')
s = Child_profile(name='Socks', user_profile_id=4, user_id=4, no_foods='lettuce, kale, chard, spinach, cabbage', yes_foods='fish, chicken', diet_id=3, diet_name='Ketogenic', intolerances='grain, peanut, soy')
f = Child_profile(name='Finn', user_profile_id=1, user_id=1, no_foods='peas carrots tomatoes', yes_foods='noodles, pork, chicken, pizza, hamburgers', diet_id=1)

db.session.add_all([c,b,s,f])
db.session.commit()

Follows.query.delete()

a = Follows(user_being_followed_id=1, user_following_id=2)
b = Follows(user_being_followed_id=1, user_following_id=3)
c = Follows(user_being_followed_id=1, user_following_id=4)
d = Follows(user_being_followed_id=2, user_following_id=1)
e = Follows(user_being_followed_id=2, user_following_id=3)
f = Follows(user_being_followed_id=2, user_following_id=4)
g = Follows(user_being_followed_id=3, user_following_id=1)
h = Follows(user_being_followed_id=3, user_following_id=2)
i = Follows(user_being_followed_id=3, user_following_id=4)
j = Follows(user_being_followed_id=4, user_following_id=1)
k = Follows(user_being_followed_id=4, user_following_id=2)
l = Follows(user_being_followed_id=4, user_following_id=3)

db.session.add_all([a,b,c,d,e,f,g,h,i,j,k,l])
db.session.commit()

