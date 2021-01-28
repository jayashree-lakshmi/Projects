from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow #required for serialization it means conveting object to text
from flask_jwt_extended import JWTManager, jwt_required, create_access_token


app = Flask(__name__)  #constructor, this app will take its name form the name of the script
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'planets.db')
app.config['JWT_SECRET_KEY']='SUPER_SCERET'#CHANGE IT IN REAL TIME for login


db = SQLAlchemy(app)
ma = Marshmallow(app) #constructor, establishing the instance of marshmallow
jwt = JWTManager(app) #login


@app.cli.command('db_create')
def db_create():
	db.create_all()
	print('Database created')

@app.cli.command('db_drop')
def db_drop():
	db.drop_all()
	print('Database dropped')

@app.cli.command('db_seed')
def db_seed():

	mercury = Planet(
	planet_name= 'Mercury',
	planet_type= 'Class D',
	home_star= 'Sol',
	mass= 3.258e23,
	radius= 1516,
	distance= 35.98e6
	)
	venus = Planet(
	planet_name= 'Venus',
	planet_type= 'Class K',
	home_star= 'Sol',
	mass= 4.867e24,
	radius= 3764,
	distance= 67.24e6
	)
	earth = Planet(
	planet_name= 'Earth',
	planet_type= 'Class M',
	home_star= 'Sol',
	mass= 5.972e24,
	radius= 3959,
	distance= 92.96e6
	)

	db.session.add(mercury)
	db.session.add(venus)
	db.session.add(earth)

	test_user = User(first_name='William',
					last_name='Herschel',
					email='xcvb@gmail.com',
					password='password')
	db.session.add(test_user)
	db.session.commit()
	print('database seeded')

@app.route('/') #decoratior gives the special capability to the functions, it defines the route for an end points.
def hello_world():
	return "Hello world" #returns text

@app.route('/super_simple')
def supe_simple():
	return jsonify(message="Hello from the planetary API")  #return json

@app.route('/not_found')
def not_found():
	return jsonify(message='the resource not found'),404

@app.route('/parameters')
def parameters():
	#http://127.0.0.1:5000/parameters?name=jay&age=14
	name = request.args.get('name')
	age = int(request.args.get('age'))
	if age<18:
		return jsonify(message='Sorry {} ,you are not elligible'.format(name)), 401
	else:
		return jsonify(message="Hey {}!!, you are elligible".format(name))


@app.route('/url_variables/<string:name>/<int:age>')
def url_variables(name:str,age:int):
	#http://127.0.0.1:5000/url_variables/jay/14
	if age<18:
		return jsonify(message='Sorry {} ,you are not elligible'.format(name)), 401
	else:
		return jsonify(message="Hey {}!!, you are elligible".format(name))	


#sqlalchemy
@app.route('/planets',methods=['GET'])
def planets():
	
	planets_list = Planet.query.all()
	result = planets_schema.dump(planets_list) #serializing with marshmallow
	print(result)
	return jsonify(message=result)

#JWT Java Web Token
@app.route('/register',methods=['POST'])
def register():
	#check whether email exists or not ,if not exists then create the user
	email = request.form['email']
	test = User.query.filter_by(email=email).first()
	if test:
		return jsonify(messgae='That email already exist'),401
	else:
		first_name = request.form['first_name']
		last_name = request.form['last_name']
		password = request.form['password']
		user = User(first_name=first_name, last_name=last_name, email=email, password=password)
		db.session.add(user)
		db.session.commit()
		return jsonify(message='User created successfuly'),201

#JWT is used
@app.route('/login', methods=['POST'])
def login():
	if request.is_json:
		email = request.json['email']
		password = request.json['password']
	else:
		email = request.form['email']
		password = request.form['password']
	test = User.query.filter_by(email=email,password=password).first()
	if test:
		access_token = create_access_token(identity=email) #this function comes from the jwt JWTManager
		return jsonify(message='Login succeeded', access_token=access_token)
	else:
		return jsonify(message='Bad email or password'), 401
	
@app.route('/retrieve_password/<string:email>',methods=['GET'])
def retrieve_password(email:str):
	user = User.query.all.filter_by(email=email).first()
	if user:
		msg=Message('your planetary api password is' + user.password, sender='admin@planetary-api.com', recipients=[email])
		mail.send(msg)
		return jsonify(message='password sent to'+email)
	else:
		return jsonify(message="that email doesn't exist")

@app.route('/planet_details/<int:planet_id>', methods=['GET'])
def planet_details(planet_id:int):
	planet = Planet.query.filter_by(planet_id=planet_id).first()
	if planet:
		result = planet_schema.dump(planet)
		return result
	else:
		return jsonify(message='The planet does not exists'), 404

@app.route('/add_planet',methods=['POST'])
@jwt_required   #protect the endpoing, when we use this end point it asks to login using login endpoint by providing email and passwrod , then return access token, use that token in the add_planet endpoint in the place of authorization of type bearer token 
def add_planet():
	planet_name = request.form['planet_name']
	test = Planet.query.filter_by(planet_name=planet_name).first()
	if test:
		return jsonify(message='Planet already exists'),409
	else:
		planet_type = request.form['planet_type']
		home_star = request.form['home_star']
		mass = float(request.form['mass'])
		radius = float(request.form['radius'])
		distance = float(request.form['distance'])
		new_planet = Planet(planet_name=planet_name,planet_type=planet_type,home_star=home_star,mass=mass,radius=radius,distance=distance)
		db.session.add(new_planet)
		db.session.commit()
		return jsonify(message='New planet added')

@app.route('/update_planet',methods=['PUT'])
@jwt_required
def update_planet():
	planet_id = int(request.form['planet_id'])
	planet = Planet.query.filter_by(planet_id=planet_id).first()
	if planet:
		planet.planet_name = request.form['planet_name']
		planet.planet_type = request.form['planet_type']
		planet.home_star = request.form['home_star']
		planet.mass = request.form['mass']
		planet.radius = float(request.form['radius'])
		planet.distance = float(request.form['distance'])
		db.session.commit()
		return jsonify(message='You updated the planet'),202
	else:
		return jsonify(message='The planet does not exist'),404
@app.route('/delete_planet/<int:planet_id>',methods=['DELETE'])
@jwt_required
def delete_planet(planet_id:int):
	planet = Planet.query.filter_by(planet_id=planet_id).first()
	if planet:
		db.session.delete(planet)
		db.session.commit()
		return jsonify(message='You deleted the planet'),202
	else:
		return jsonify(message='Planet id does not exists'),404

#database models
class User(db.Model):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	first_name = Column(String)
	last_name = Column(String)
	email = Column(String, unique=True)
	password = Column(String)

class Planet(db.Model):
	__tablename__ = 'planets'
	planet_id = Column(Integer,primary_key=True)
	planet_name = Column(String)
	planet_type = Column(String)
	home_star = Column(String)
	mass = Column(Float)
	radius = Column(Float)
	distance = Column(Float)

class UserSchema(ma.Schema):
	class Meta:
		fields = ('id', 'first_name', 'last_name', 'email', 'password')
class PlanetSchema(ma.Schema):
	class Meta:
		fields = ('planet_id', 'planet_name', 'planet_type', 'home_star','mass', 'radius', 'distance')


user_schema = UserSchema()
users_schema = UserSchema(many=True) #defining the ability to de-serialize the single obj as in when u give one planet back lateron when we make the route for that, getting one record will use user_schema, for multiple records will use users_schema

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

if __name__ == '__main__':
	app.run(debug=True)