from flask import Flask, request, session, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from config import Config, db
from models import User, Recipe

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Init extensions
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

# Example route (you can add resources later)
@app.route("/")
def index():
    return {"message": "Flask app is running!"}

class Signup(Resource):
    def post(self):
        data = request.get_json()
        
        # Check if username is provided
        if not data.get('username'):
            return {'error': 'Username is required'}, 422
            
        # Check if user already exists
        if User.query.filter(User.username == data['username']).first():
            return {'error': 'Username already exists'}, 422
            
        # Create new user
        new_user = User(
            username=data['username'],
            image_url=data.get('image_url', ''),
            bio=data.get('bio', '')
        )
        
        # Set password hash
        new_user.password_hash = data['password']
        
        db.session.add(new_user)
        db.session.commit()
        
        # Set session
        session['user_id'] = new_user.id
        
        return new_user.to_dict(), 201

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter(User.username == data['username']).first()
        
        if user and user.authenticate(data['password']):
            session['user_id'] = user.id
            return user.to_dict(), 200
        else:
            return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id', None)
            return {}, 204
        else:
            return {'error': 'Unauthorized'}, 401

class CheckSession(Resource):
    def get(self):
        if session.get('user_id'):
            user = User.query.filter(User.id == session['user_id']).first()
            return user.to_dict(), 200
        else:
            return {'error': 'Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            recipes = Recipe.query.filter(Recipe.user_id == session['user_id']).all()
            return [recipe.to_dict() for recipe in recipes], 200
        else:
            return {'error': 'Unauthorized'}, 401
    
    def post(self):
        if session.get('user_id'):
            data = request.get_json()
            
            # Validate instructions length
            if len(data.get('instructions', '')) < 50:
                return {'error': 'Instructions must be at least 50 characters long'}, 422
            
            new_recipe = Recipe(
                title=data['title'],
                instructions=data['instructions'],
                minutes_to_complete=data['minutes_to_complete'],
                user_id=session['user_id']
            )
            
            db.session.add(new_recipe)
            db.session.commit()
            
            return new_recipe.to_dict(), 201
        else:
            return {'error': 'Unauthorized'}, 401

# Add resources to API
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(RecipeIndex, '/recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
