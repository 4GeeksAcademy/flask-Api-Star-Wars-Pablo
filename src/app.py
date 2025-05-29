"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():
    users= db.session.query(User).all()

    if users is None:
        return jsonify({"error": "users not found"}), 404


    return jsonify([user.serialize() for user in users]), 200

##Renderizado de Usuarios##

@app.route('/user/<int:id>', methods=['GET'])
def getUserById(id):
    user= User.query.filter_by(id=id).first() ##Primer ID es del "models" y el segundo es el de la consulta (la url)
    if not user:
        return jsonify({"error": "user not found"}), 400
    return jsonify({"user": user.serialize()}), 200

##Creación de usuarios##

@app.route('/user', methods=['POST'])
def newUser():
    request_body=request.get_json()
    email = request_body["email"]
    password = request_body["password"]
    if not email or not password:
        return jsonify ({"msg": "Todos los campos son requeridos"}), 400
    exist = User.query.filter_by(email=email).first()
    if exist:
        return jsonify({"msg": "Correo ya utilizado"}), 400
    new_user = User(email= email, password=password, is_active= True)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "Usuario creado"}), 201

##Agregar Character Favorito a Usuarios##

##Agregar Planet Favorito a Usuarios##

##Eliminar Character Favoritos de Usuarios##

##Eliminar Planet Favoritos de Usuarios##

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)