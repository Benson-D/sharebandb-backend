from datetime import datetime
from models import User, Listing, Message
from app import db

db.drop_all()
db.create_all()

user_one = User(
    username="test-user",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    email="test@gmail.com",
    first_name="Test",
    last_name="User",
    bio="This is the test bio of a user",
    location="Chicago, IL",
    is_admin=True
)

user_two = User(
    username="test-user-2",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    email="testNew@gmail.com",
    first_name="Test",
    last_name="User",
    bio="This is the test 2 bio of a user",
    location="Boston, MA",
    is_admin=False
)

l1 = Listing(
    name="Designer studio on Michigan Ave",
    address="test123 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/apartment1.jpg",
    price=100,
    description="Cozy apartment that features 2 bedrooms, living room, and 1 bathroom",
    location="Chicago IL",
    created=user_one.username
)

l2 = Listing(
    name="Designer studio on Michigan Ave",
    address="test123 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/apartment2.jpg",
    price=200,
    description="Cozy apartment that features 1 bedroom, living room, and 1 bathroom",
    location="Chicago IL",
    created=user_one.username
)

l3 = Listing(
    name="CHICAGO O’HARE HARLEM BLUE LINE",
    address="test123 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/house1.jpg",
    price=200,
    description="Cozy house that features 3 bedrooms, living room, and 3 bathrooms",
    location="Chicago IL",
    created=user_one.username
)

l4 = Listing(
    name="Fenway location",
    address="test234 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/house3.jpg",
    price=200,
    description="Cozy house that features 3 bedrooms, living room, and 3 bathrooms",
    location="Boston MA",
    created=user_one.username
)

l5 = Listing(
    name="Chicago Southside location",
    address="test123 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/house4.jpg",
    price=200,
    description="Cozy house that features 3 bedrooms, living room, and 3 bathrooms",
    location="Chicago IL",
    created=user_one.username
)

l6 = Listing(
    name="Chicago Northside location",
    address="test123 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/house5.jpg",
    price=200,
    description="Cozy house that features 2 bedrooms, living room, and 1 bathroom",
    location="Chicago IL",
    created=user_one.username
)

l7 = Listing(
    name="Bay Area location",
    address="test123 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/house6.jpg",
    price=200,
    description="Cozy house that features 2 bedrooms, living room, and 2 bathrooms",
    location="San Francisco CA",
    created=user_one.username
)

l8 = Listing(
    id=8,
    name="Bay Area location",
    address="test123 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/house2.jpg",
    price=200,
    description="Cozy house that features 3 bedrooms, living room, and 3 bathrooms",
    location="San Francisco CA",
    created=user_two.username
)

message = Message(
    text="Hello new user!",
    time_sent=datetime.now(),
    to_user=user_two.username,
    from_user=user_one.username,
    listing_id=l8.id
)


db.session.add_all([user_one, user_two, l1,l2,l3,l4,l5,l6,l7,l8,message])
db.session.commit()
