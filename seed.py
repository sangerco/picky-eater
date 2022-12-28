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


