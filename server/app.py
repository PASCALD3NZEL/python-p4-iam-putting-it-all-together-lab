from flask import Flask, request, session, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError
from config import Config, db
from models import User, Recipe

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Init extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        bio = data.get('bio')
        image_url = data.get('image_url')

        if not username:
            return {'error': 'Username is required'}, 422

        try:
            user = User(username=username, bio=bio, image_url=image_url)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(), 201
        except IntegrityError:
            return {'error': 'Username already exists'}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Unauthorized'}, 401
        return user.to_dict()

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict()
        return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    def delete(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        session.pop('user_id', None)
        return {}, 204

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        recipes = Recipe.query.filter_by(user_id=user_id).all()
        return [recipe.to_dict() for recipe in recipes]

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')

        if not title or not instructions or not minutes_to_complete:
            return {'error': 'Missing required fields'}, 422

        try:
            recipe = Recipe(title=title, instructions=instructions, minutes_to_complete=minutes_to_complete, user_id=user_id)
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except ValueError:
            return {'error': 'Instructions must be at least 50 characters long'}, 422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
