import os
from flask import Flask, jsonify, request
from flask_debugtoolbar import DebugToolbarExtension
# from sqlalchemy.exc import IntegrityError
# from werkzeug.exceptions import Unauthorized

from models import db, connect_db, Listing
from flask_cors import CORS
from handle_image import create_presigned_url

import boto3

import dotenv
dotenv.load_dotenv()

s3 = boto3.client('s3')


BUCKET = os.environ['BUCKET']

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sharebnb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

connect_db(app)

app.config['SECRET_KEY'] = "secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

db.create_all()

##############################################################################
# Listing Routes

@app.get("/listings")
def show_listings():
    """Show all current listings"""
    
    searchTerm = request.args.get('location')
    
    listings = Listing.findListings(searchTerm)

    serialized = [listing.serialize() for listing in listings]

    return jsonify(listings=serialized)

@app.get("/listings/<int:listing_id>")
def get_listing(listing_id):
    """Get a specific listing
    Return {id, name, image, price, description, location}
    """

    listing = Listing.query.get_or_404(listing_id)

    serialized = listing.serialize()

    return jsonify(listing=serialized)

@app.post('/listings')
def create_listing():
    """
    Adding a new listing to our database
    Return {listing: {id, name, image, price, description, location}}
    """

    data = request.form
    file = request.files['image']

    s3.upload_fileobj(file, BUCKET, file.filename, ExtraArgs={"ACL":"public-read"} )
    url_path = create_presigned_url( BUCKET, file.filename,)

    new_listing = Listing(
        name = data['name'],
        image = url_path,
        price = data['price'],
        description = data['description'], 
        location = data['location']
    )
    
    db.session.add(new_listing)
    db.session.commit()

    serialized = new_listing.serialize()
    # Return w/status code 201 --- return tuple (json, status)
    return (jsonify(listing=serialized), 201)

@app.patch('/listings/<int:listing_id>')
def update_listing(listing_id):
    """
    Update an existing listing.
    Return {listing: {id, name, image, price, description, location}}
    """

    listing = Listing.query.get_or_404(listing_id)

    listing.price = request.json["price"]
    listing.image = request.json["image"]
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

    # serialized = listing.serialize()

    return jsonify(deleted=listing_id)