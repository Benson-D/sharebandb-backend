"""SQL models for sharebnb"""
import os

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from werkzeug.utils import secure_filename

import boto3

import dotenv
dotenv.load_dotenv()

s3 = boto3.client('s3')

BUCKET = os.environ['BUCKET']

bcrypt = Bcrypt()
db = SQLAlchemy()

DEFAULT_IMAGE = "https://sharebnb-dnd.s3.us-east-2.amazonaws.com/defaultImage.png"
IMAGE_URL = "https://sharebnb-dnd.s3.us-east-2.amazonaws.com"

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

    created_listing = db.relationship(
        "Listing",
        foreign_keys="Listing.created",
        backref="user_created"
    )

    rented_listing = db.relationship(
        "Listing",
        foreign_keys="Listing.rented",
        backref="user_rented"
    )

    sent_message = db.relationship(
        "Message",
        foreign_keys="Message.from_user",
        backref="user_sent"
    )

    received_message = db.relationship(
        "Message",
        foreign_keys="Message.to_user",
        backref="user_received"
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

    sent_message = db.relationship('Message',
                                    foreign_keys="Message.listing_id",
                                    backref="listing")

    @classmethod
    def find_listings(cls, searchTerm=False):
        """Find all current listings"""
        
        if searchTerm:
            listings = cls.query.filter(cls.location.like(f'%{searchTerm}%')).all()
        else:    
            listings = cls.query.all() 
        return listings

    @classmethod
    def create_listing(cls, data, image):
        """Create a new listing"""

        filename = secure_filename(image.filename)

        s3.upload_fileobj(
        image, BUCKET, image.filename, ExtraArgs={"ACL":"public-read"} )

        new_listing = Listing(
            name = data['name'],
            address = data['address'],
            image = f"{IMAGE_URL}/{filename}",
            price = data['price'],
            description = data['description'], 
            location = data['location'],
            created = data['created']
        )
    
        db.session.add(new_listing)

        return new_listing

    def serialize(self):
        """Serialize to dictionary."""

        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "image": self.image,
            "price": str(self.price),
            "description": self.description,
            "location": self.location,
            "created": self.created,
            "rented": self.rented
        }

class Message(db.Model):
    """Message Model"""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer, 
        primary_key = True,
        autoincrement = True
    )

    text = db.Column(
        db.Text,
        nullable=False
    )

    time_sent = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    to_user = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        primary_key = True,
        nullable=False
    )

    from_user = db.Column(
        db.Text,
        db.ForeignKey('users.username', ondelete='CASCADE'),
        primary_key = True,
        nullable=False
    )

    listing_id = db.Column(
        db.Integer,
        db.ForeignKey('listings.id', ondelete="CASCADE"),
        nullable=False,
    )

    def __repr__(self):
        return f"""<Message #{self.id}, {self.to_user}, {self.from_user}>"""

    @classmethod
    def create_message(cls, data, curr_user):
        """Create a new message"""

        listing = Listing.query.get_or_404(data['listing_id'])
        user = User.query.get_or_404(data['to_user'])

        if user.username != curr_user:

            new_message = Message(
                text=data['text'],
                time_sent=datetime.now(),
                to_user=user.username,
                from_user=curr_user,
                listing_id=listing.id
            )

            db.session.add(new_message)

            return new_message 
    
    @classmethod
    def retrieve_inbox(cls, curr_user):
        """Find all messages for to_user"""
        
        inbox = cls.query.filter(cls.to_user == curr_user).all()
    
        return inbox

    def serialize(self):
        """Serialize Message Object to dictionary"""

        return {
            "text": self.text,
            "time_sent": self.time_sent,
            "to_user": self.to_user,
            "from_user": self.from_user,
            "listing_id": self.listing_id,
        }

def connect_db(app):
    """Connect this database to provided Flask app."""

    db.app = app
    db.init_app(app)