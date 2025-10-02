from config import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from flask_bcrypt import Bcrypt

# We'll use bcrypt for password hashing
bcrypt = Bcrypt()

class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    # Serialization rules to avoid recursion
    serialize_rules = ('-recipes', '-_password_hash')

    id = db.Column(db.Integer, primary_key=True)   # ✅ Must have PK
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=True)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship("Recipe", back_populates="user")

    # Password hash property
    @property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password) if self._password_hash else False


class Recipe(db.Model, SerializerMixin):
    __tablename__ = "recipes"

    # Serialization rules to avoid recursion
    serialize_rules = ('-user',)

    id = db.Column(db.Integer, primary_key=True)   # ✅ Must have PK
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = db.relationship("User", back_populates="recipes")

    # Add validation for instructions (must be at least 50 characters)
    @validates('instructions')
    def validate_instructions(self, key, instructions):
        if len(instructions) < 50:
            raise ValueError("Instructions must be at least 50 characters long")
        return instructions
