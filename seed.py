from models import db, Follows, User, User_profile, Child_profile, Favorite_recipe
from models import Shopping_list, Diet
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
