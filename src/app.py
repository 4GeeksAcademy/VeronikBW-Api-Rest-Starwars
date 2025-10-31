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
from models import db, User, Planet, Character, Favorite
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
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


@app.route('/people', methods=['GET'])
def get_people():
    people = Character.query.all()
    results = [character.serialize() for character in people]
    return jsonify(results), 200


@app.route('/people/<int:person_id>', methods=['GET'])
def get_person_by_id(person_id):
    people = Character.query.filter_by(id=person_id).first()
    if people is None:
        return jsonify({"message": "Character not found"}), 404
    return jsonify(people.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    results = [planet.serialize() for planet in planets]
    return jsonify(results), 200


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"message": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    results = [user.serialize() for user in users]
    return jsonify(results), 200


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    user_id = request.args.get('user_id')
    if user_id is None:
        return jsonify({"message": "user_id is required"}), 400

    user = User.query.get(user_id)
    if user is None:
        return jsonify({"message": "User not found"}), 404

    favorites = Favorite.query.filter_by(user_id=user.id).all()
    results = []
    for fav in favorites:
        if fav.planet:
            results.append(fav.planet.serialize())
        if fav.character:
            results.append(fav.character.serialize())
    return jsonify(results), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def handle_favorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if user_id is None:
        return jsonify({"message": "user_id is required"}), 400

    user = User.query.get(user_id)
    planet = Planet.query.get(planet_id)

    if user is None:
        return jsonify({"message": "User not found"}), 404
    if planet is None:
        return jsonify({"message": "Planet not found"}), 404

    fav = Favorite(user_id=user.id, planet_id=planet.id)
    db.session.add(fav)
    db.session.commit()

    return jsonify({"message": f"Planet {planet.name} added to favorites for user {user.user_name}"}), 201


@app.route('/favorite/people/<int:person_id>', methods=['POST'])
def handle_favorite_person(person_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if user_id is None:
        return jsonify({"message": "user_id is required"}), 400

    user = User.query.get(user_id)
    character = Character.query.get(person_id)

    if user is None:
        return jsonify({"message": "User not found"}), 404
    if character is None:
        return jsonify({"message": "Character not found"}), 404

    fav = Favorite(user_id=user.id, character_id=character.id)
    db.session.add(fav)
    db.session.commit()

    return jsonify({"message": f"Character {character.name} added to favorites for user {user.user_name}"}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def handle_unfavorite_planet(planet_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if user_id is None:
        return jsonify({"message": "user_id is required"}), 400

    favorite = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()

    if favorite is None:
        return jsonify({"message": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Planet removed from favorites"}), 200


@app.route('/favorite/people/<int:person_id>', methods=['DELETE'])
def handle_unfavorite_person(person_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if user_id is None:
        return jsonify({"message": "user_id is required"}), 400

    favorite = Favorite.query.filter_by(
        user_id=user_id, character_id=person_id).first()

    if favorite is None:
        return jsonify({"message": "Favorite not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "Character removed from favorites"}), 200


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
