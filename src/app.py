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
from models import db, User, Character, Planet, FavoriteCharacter, FavoritePlanet

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

##Renderizado de Usuarios##

@app.route('/user', methods=['GET'])
def handle_hello():
    users= db.session.query(User).all()

    if not users:
        return jsonify({"error": "users not found"}), 404


    return jsonify([user.serialize() for user in users]), 200

##Renderizado de Usuarios por id##

@app.route('/user/<int:id>', methods=['GET'])
def getUserById(id):
    user= User.query.filter_by(id=id).first()
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
        return jsonify ({"msg": "All fields are required"}), 400
    exist = User.query.filter_by(email=email).first()
    if exist:
        return jsonify({"msg": "This email is already in use"}), 400
    new_user = User(email= email, password=password, is_active= True)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "Usuario creado"}), 201

##Renderizado Character##

##Renderizado Character:id##

##Renderizado Planet##

##Renderizado Planet:id##

##Agregar Character Favorito a Usuarios##
@app.route('/favorite_character/<int:user_id>', methods=['POST'])
def addFavoriteCharacter(user_id):
    request_body = request.get_json()
    character_id = request_body.get("character_id")

    if not user_id or not character_id:
        return ({"msg": "User and Character required"}), 400
    
    user = User.query.get(user_id)
    character = Character.query.get(character_id)

    if not user or not character:
        return jsonify ({"msg": "User and character not found"}), 404
    
    existing_favorite = FavoriteCharacter.query.filter_by(user_id=user_id, character_id=character_id).first()
    if existing_favorite:
        return jsonify ({"msg": "Favorite already exists"}), 409
    
    new_favorite_character = FavoriteCharacter(user_id=user_id, character_id=character_id)
    db.session.add(new_favorite_character)
    db.session.commit()

    return jsonify({"msg": "Favorite character added"}), 201
    
    

##Agregar Planet Favorito a Usuarios##

@app.route('/favorite_planet/<int:user_id>', methods=['POST'])
def addFavoritePlanet(user_id):
    request_body = request.get_json()
    planet_id = request_body.get("planet_id")

    if not user_id or not planet_id:
        return ({"msg": "User and planet required"}), 400
    
    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)

    if not user or not planet:
        return jsonify ({"msg": "User and planet not found"}), 404
    
    existing_favorite = FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if existing_favorite:
        return jsonify ({"msg": "Favorite already exists"}), 409
    
    new_favorite_planet = FavoritePlanet(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite_planet)
    db.session.commit()

    return jsonify({"msg": "Favorite planet added"}), 201

##Eliminar Character Favoritos de Usuarios##

@app.route('/favorite_character/<int:user_id>', methods=['DELETE'])
def deleteFavoriteCharacter(user_id):
    request_body = request.get_json()
    character_id = request_body.get("character_id")

    if not character_id:
        return jsonify({"msg": "Character ID is required"}), 400
    
    favorite_character_delete = FavoriteCharacter.query.filter_by(user_id=user_id, character_id=character_id).first()

    if not favorite_character_delete:
        return jsonify({"msg": "Favorite Character not found"}), 404
    
    db.session.delete(favorite_character_delete)
    db.session.commit()

    return jsonify({"msg": "deleted successfully"}),200

##Eliminar Planet Favoritos de Usuarios##

@app.route('/favorite_planet/<int:user_id>', methods=['DELETE'])
def deleteFavoritePlanet(user_id):
    request_body = request.get_json()
    planet_id = request_body.get("planet_id")

    if not planet_id:
        return jsonify({"msg": "Planet ID is required"}), 400
    
    favorite_planet_delete = FavoritePlanet.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    if not favorite_planet_delete:
        return jsonify({"msg": "Favorite planet not found"}), 404
    
    db.session.delete(favorite_planet_delete)
    db.session.commit()

    return jsonify({"msg": "deleted successfully"}),200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)