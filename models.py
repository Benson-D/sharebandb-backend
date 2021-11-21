"""SQL models for sharebnb"""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE = "https://sharebnb-dnd.s3.us-east-2.amazonaws.com/defaultImage.png"

class User(db.Model):
    """User Model"""

    __tablename__ = 'users'

    username = db.Column(
        db.String(length=50),
        primary_key=True,
        unique=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    first_name = db.Column(
        db.Text,
        nullable=False,
    )

    last_name = db.Column(
        db.Text,
        nullable=False
    )

    bio = db.Column(
        db.Text,
        default=""
    )

    location = db.Column(
        db.Text,
        nullable=False
    )

    is_admin = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    listings_created = db.relationship(
        "Listing",
        foreign_keys="Listing.created",
        backref="creator"
    )

    listings_rented = db.relationship(
        "Listing",
        foreign_keys="Listing.rented",
        backref="renter"
    )

    def __repr__(self):
        return f"<User #{self.username}, {self.first_name} {self.last_name}>"

    @classmethod
    def signup(cls, username, password, email, first_name, last_name, location):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            email=email,
            first_name=first_name,
            last_name=last_name,
            location=location,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    
    def serialize(self):
        """Serialize User object to dictionary"""

        return {
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "bio": self.bio,
            "location": self.location,
            "is_admin": self.is_admin
        }

    def update(self, form):
        """Update User fields"""

        self.email = form.email.data
        self.first_name = form.first_name.data
        self.last_name = form.last_name.data
        self.bio = form.bio.data
        self.location = form.location.data


class Listing(db.Model):
    """Listing Model"""

    __tablename__ = "listings"

    id = db.Column(
        db.Integer, 
        primary_key = True,
        autoincrement = True
    )

    name = db.Column(
        db.Text,
        nullable = False,
    )

    address = db.Column(
        db.Text,
        nullable = False,
    )

    image = db.Column(
        db.Text, 
        nullable = False,
        default = DEFAULT_IMAGE
    )

    price = db.Column(
        db.Numeric(10, 2),
        nullable = False, 
        default = 0
    )

    description = db.Column(
        db.Text, 
        nullable = False,
        default = ""
    )

    location = db.Column(
        db.Text,
        nullable = False
    )

    created = db.Column(
        db.String,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        nullable=False
    )

    rented = db.Column(
        db.String,
        db.ForeignKey('users.username', ondelete='CASCADE'),
    )

    @classmethod
    def findListings(cls, searchTerm=False):
        """Find all current listings"""
        
        if searchTerm:
            listings = cls.query.filter(cls.location.like(f'%{searchTerm}%')).all()
        else:    
            listings = cls.query.all() 
        return listings


    def serialize(self):
        """Serialize to dictionary."""

        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "image": self.image,
            "price": str(self.price),
            "description": self.description,
            "location": self.location
        }

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)