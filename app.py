import os
from flask import Flask, jsonify, request
from flask_debugtoolbar import DebugToolbarExtension
from flask_jwt_extended import create_access_token, JWTManager, jwt_required
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, Listing, User
from flask_cors import CORS
from handle_image import create_presigned_url

import boto3

import dotenv
dotenv.load_dotenv()

CURR_USER_KEY = "curr_user"

s3 = boto3.client('s3')

BUCKET = os.environ['BUCKET']

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

@app.post('/signup')
def signup():
    """Signup user, create new user and add to DB. 
    If username is unique (hasn't been taken) Return { token } 
    else Return { errors: ["Username is already taken"] }"""
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

@app.post('/login')
def login_user():
    """Authenticates user login
       if authenticated Return { token }
       else Return { error }"""

    username = request.json["username"]
    password = request.json["password"]

    is_user = User.authenticate(username, password)

    if is_user: 
        return do_login(is_user)

    return (jsonify(errors=["Invalid username or password"]), 401)

@app.get('/users/<username>')
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

@app.delete('/users/<username>/delete')
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
def show_listings():
    """Show all or specific locations of current listings"""
    
    searchTerm = request.args.get('location')
    
    listings = Listing.findListings(searchTerm)

    serialized = [listing.serialize() for listing in listings]

    return jsonify(listings=serialized)

@app.get("/listings/<int:listing_id>")
def get_listing(listing_id):
    """Get a specific listing
    Return { id, name, image, price, description, location }"""

    listing = Listing.query.get_or_404(listing_id)

    serialized = listing.serialize()

    return jsonify(listing=serialized)

@app.post('/listings')
@jwt_required()
def create_listing():
    """Add a new listing to the database
    Return {listing: {id, name, image, price, description, location}}"""

    data = request.form
    file = request.files['image']

    s3.upload_fileobj(
        file, BUCKET, file.filename, ExtraArgs={"ACL":"public-read"} )
    url_path = create_presigned_url( BUCKET, file.filename,)

    new_listing = Listing(
        name = data['name'],
        address = data['address'],
        image = url_path,
        price = data['price'],
        description = data['description'], 
        location = data['location'],
        created = data['created']
    )
    
    db.session.add(new_listing)
    db.session.commit()

    serialized = new_listing.serialize()
    return (jsonify(listing=serialized), 201)

@app.patch('/listings/<int:listing_id>')
def update_listing(listing_id):
    """Update an existing listing.
    Return {listing: {id, name, image, price, description, location}}"""

    listing = Listing.query.get_or_404(listing_id)

    listing.address = request.json["address"]
    listing.image = request.json["image"]
    listing.price = request.json["price"]
    listing.description = request.json["description"]

    db.session.commit()

    serialized = listing.serialize()

    return jsonify(listing=serialized)

@app.delete('/listings/<int:listing_id>')
def delete_listing(listing_id):
    """Delete a listing. Return {deleted: [listing-id]}"""

    listing = Listing.query.get_or_404(listing_id)

    db.session.delete(listing)
    db.session.commit()

    return jsonify(deleted=listing_id)