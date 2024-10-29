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
from models import db, User, Planet, Character
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

@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    serialized_users = [user.serialize() for user in users]
    response_body = {
        "msg": "Here's our list of users", "users": serialized_users
    }

    return jsonify(response_body), 200 

@app.route('/user/favorites', methods=['GET'])
def get_all_user_favorites():
    user = User.query.get(1)
    favorites = {
        "favorite_characters": [favorite_character.serialize() for favorite_character in user.favorite_characters],
        "favorite_planets": [favorite_planet.serialize() for favorite_planet in user.favorite_planets]


    }
    response_body = {
        "msg": "Here are your favorite lists", "favorites": favorites
    }

    return jsonify(response_body), 200


@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()
    serialized_characters=[character.serialize()for character in characters]
    response_body = {
        "msg": "Here's our list of characters", "characters" : serialized_characters
    }

    return jsonify(response_body), 200

@app.route('/characters/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.filter_by(id=character_id).first()
    if character is None :
        return jsonify({"msg": "character not found" }), 404
    
    response_body = {
        "msg": "Here's the character", "character" : character.serialize()
    }

    return jsonify(response_body), 200

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    serialized_planets=[planet.serialize()for planet in planets]
    response_body = {
        "msg": "Here's our list of planets", "planets" : serialized_planets
    }

    return jsonify(response_body), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.filter_by(id=planet_id).first()
    if planet is None:
        return jsonify({"msg": "planet not found"}), 404
    
    response_body = {
        "msg": "Here's the planet", "planet": planet.serialize()
    }

    return jsonify(response_body), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    if user_id is None:
        return jsonify({"msg": "user id required"}), 400
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "user not found"}), 404
    planet = Planet.query.filter_by(id=planet_id).first()
    if planet is None:
        return jsonify({"msg": "planet not found"}), 404
    if planet in user.favorite_planets: 
        return jsonify({"msg": "Planet is already part of favorite planets list."}), 409
    if user.favorite_planets is None: 
        user.favorite_planets = []
    user.favorite_planets.append(planet)
    db.session.commit()
    response_body = {
        "msg": "Success! A new planet has been added to your favorite planets list.", "favorite_planets": [favorite_planet.serialize() for favorite_planet in user.favorite_planets]

    }

    return jsonify(response_body), 200

@app.route('/favorite/character/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    user_id = request.json.get('user_id')
    if user_id is None:
        return jsonify({"msg": "user id required"}), 400
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "user not found"}), 404
    character = Character.query.filter_by(id=character_id).first()
    if character is None:
        return jsonify({"msg": "character not found"}), 404
    if character in user.favorite_characters: 
        return jsonify({"msg": "Character is already part of favorite characters list."}), 409
    if user.favorite_characters is None: 
        user.favorite_characters = []
    user.favorite_characters.append(character)
    db.session.commit()
    response_body = {
        "msg": "Success! A new character has been added to your favorite characters list.", "favorite_characters": [favorite_character.serialize() for favorite_character in user.favorite_characters]
    }

    return jsonify(response_body), 200


@app.route('/favorite/character/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):
    user_id = request.json.get('user_id')
    if user_id is None:
        return jsonify({"msg": "user id required"}), 400
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "user not found"}), 404
    character = Character.query.filter_by(id=character_id).first()
    if character is None:
        return jsonify({"msg": "character not found"}), 404
    if character not in user.favorite_characters: 
        return jsonify({"msg": "Character is not part of favorite characters list."}), 409
    user.favorite_characters.remove(character)
    db.session.commit()
    response_body = {
        "msg": "Success! Character has been deleted from your favorite characters list.", "favorite_characters": [favorite_character.serialize() for favorite_character in user.favorite_characters]
    }

    return jsonify(response_body), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.json.get('user_id')
    if user_id is None:
        return jsonify({"msg": "user id required"}), 400
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"msg": "user not found"}), 404
    planet = Planet.query.filter_by(id=planet_id).first()
    if planet is None:
        return jsonify({"msg": "planet not found"}), 404
    if planet not in user.favorite_planets: 
        return jsonify({"msg": "Planet is not part of favorite planets list."}), 409
    user.favorite_planets.remove(planet)
    db.session.commit()
    response_body = {
        "msg": "Success! Planet has been deleted from your favorite planets list.", "favorite_planets": [favorite_planet.serialize() for favorite_planet in user.favorite_planets]
    }

    return jsonify(response_body), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
