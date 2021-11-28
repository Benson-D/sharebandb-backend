import os

from flask import Flask, jsonify, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity

from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Listing, Message
from flask_cors import CORS

import dotenv
dotenv.load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ['DATABASE_URL']
    .replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

app.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']

jwt = JWTManager(app)

connect_db(app)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

##############################################################################
# JWT 

# Function takes in the object that we're creating a token for, adds 
# additional claims to the JWT.
# Returns { username: "test_user"}

@jwt.additional_claims_loader
def add_claims_to_access_token(user):
    return {
         "username": user.username
    }

# Function takes in a object when creating JWTs, 
# converts it to a JSON serializable format.
# Returns "test_user"

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username

##############################################################################
# User signup/login/logout

def do_login(user):
    """Create a token when a user has logged in and signed up successfully, 
       Return { token }"""

    access_token = create_access_token(identity=user)
    
    return (jsonify(token=access_token), 200)

@app.post("/signup")
def signup():
    """Signup user, create new user and add to DB. 
        If username is unique (hasn't been taken) 
            Return { token } 
        else 
            Return { errors: ["Username is already taken"] }"""

    data = request.json

    try:
        user = User.signup(
                username=data["username"],
                password=data["password"],
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                location=data["location"]
            )

        db.session.commit()

        return do_login(user)

    except IntegrityError:
        return (jsonify(errors=["Username is already taken"]), 400)

@app.post("/login")
def login_user():
    """Authenticates user login
        if authenticated 
            Return { token }
        else 
            Return { error: ["Invalid username or password"] }"""

    username = request.json["username"]
    password = request.json["password"]

    is_user = User.authenticate(username, password)

    if is_user: 
        return do_login(is_user)

    return (jsonify(errors=["Invalid username or password"]), 401)

@app.get("/users/<username>")
@jwt_required()
def get_user(username):
    """Show user details
        Return { username,
                 email,
                 first_name,
                 last_name,
                 bio,
                 location,
                 is_admin
                }"""

    user = User.query.get_or_404(username)
    serialize = User.serialize(user)
    
    return (jsonify(user=serialize), 200)

@app.delete("/users/<username>/delete")
@jwt_required()
def delete_user(username):
    """Delete user, if there is a username.
        Return { success }"""

    user = User.query.get_or_404(username)

    db.session.delete(user)
    db.session.commit()
    return (jsonify(deleted="success"), 201)

##############################################################################
# Listing Routes

@app.get("/listings")
@jwt_required()
def show_listings():
    """Show all or specific locations of current listings
    Return { listing, listing, listing... }"""
    
    searchTerm = request.args.get('location')
    
    listings = Listing.find_listings(searchTerm)

    serialized = [listing.serialize() for listing in listings]

    return jsonify(listings=serialized)

@app.get("/listings/<int:listing_id>")
@jwt_required()
def get_listing(listing_id):
    """Get a specific listing
    Return { id, 
             name, 
             address, 
             image, 
             price, 
             description, 
             location, 
             created, 
             rented
            }"""

    listing = Listing.query.get_or_404(listing_id)

    serialized = listing.serialize()

    return jsonify(listing=serialized)

@app.post("/listings")
@jwt_required()
def add_listing():
    """Add a new listing to the database
    Return { id, 
             name, 
             address, 
             image, 
             price, 
             description, 
             location, 
             created, 
             rented
            }"""

    data = request.form
    image = request.files['image']

    new_listing = Listing.create_listing(data, image)

    db.session.commit()

    serialized = new_listing.serialize()
    return (jsonify(listing=serialized), 201)

@app.patch("/listings/<int:listing_id>")
@jwt_required()
def update_listing(listing_id):
    """Update an existing listing.
    Return {id, name, address, image, price, description, location}"""

    listing = Listing.query.get_or_404(listing_id)

    listing.address = request.json["address"]
    listing.image = request.json["image"]
    listing.price = request.json["price"]
    listing.description = request.json["description"]

    db.session.commit()

    serialized = listing.serialize()

    return jsonify(listing=serialized)

@app.delete("/listings/<int:listing_id>")
@jwt_required()
def delete_listing(listing_id):
    """Delete a listing. Return {deleted: listing-id}"""

    listing = Listing.query.get_or_404(listing_id)

    db.session.delete(listing)
    db.session.commit()

    return (jsonify(deleted=listing_id), 201)

##############################################################################
# Message Routes

@app.post("/messages")
@jwt_required()
def send_message():
    """Create a message to send to user
        if not the same user: 
            Return { text, time_sent, to_user, from_user, listing_id} 
        else 
            Return { errors: ["Invalid Username"]}"""

    curr_user = get_jwt_identity()

    data = request.json

    new_message = Message.create_message(data, curr_user)

    if new_message:

        db.session.commit()
        serialize = new_message.serialize()

        return (jsonify(message=serialize), 201)

    return (jsonify(errors=["Invalid Username"]), 404)

@app.get("/messages")
@jwt_required()
def inbox_messages():
    """Show all or specific messages for to_user
    Return { message, message, message... }"""

    curr_user = get_jwt_identity()
    inbox = Message.retrieve_inbox(curr_user)

    serialize = [message.serialize() for message in inbox]

    return jsonify(message=serialize)
    
@app.delete("/messages/<int:message_id>")
@jwt_required()
def delete_message(message_id):
    """Delete a message. Return {deleted: message-id}"""

    message = Message.query.get_or_404(message_id)

    db.session.delete(message)
    db.session.commit()

    return (jsonify(deleted=message_id), 201)  