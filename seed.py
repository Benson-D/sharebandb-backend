from models import User, db, Listing
# from app import app

db.drop_all()
db.create_all()

user_one = User(
    username="test_user",
    password="$2b$12$AZH7virni5jlTTiGgEg4zu3lSvAw68qVEfSIOjJ3RqtbJbdW/Oi5q",
    email="test@gmail.com",
    first_name="Test",
    last_name="User",
    bio="This is the test bio of a user",
    location="Chicago IL",
    is_admin=True
)

l1 = Listing(
    name="Designer studio on Michigan Ave",
    address="test123 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/apartment1.jpg",
    price=100,
    description="Cozy apartment that features 2 bedrooms, living room, and 1 bathroom",
    location="Chicago IL",
    created="test_user"
)

l2 = Listing(
    name="Designer studio on Michigan Ave",
    address="test123 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/apartment2.jpg",
    description="Cozy apartment that features 1 bedroom, living room, and 1 bathroom",
    location="Chicago IL",
    created="test_user"
)
l3 = Listing(
    name="CHICAGO O’HARE HARLEM BLUE LINE",
    address="test123 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/house1.jpg",
    description="Cozy house that features 3 bedrooms, living room, and 3 bathrooms",
    location="San Francisco CA",
    created="test_user"
)

l4 = Listing(
    name="Chicago Southside location",
    address="test123 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/house2.jpg",
    description="Cozy house that features 3 bedrooms, living room, and 3 bathrooms",
    location="San Francisco CA",
    created="test_user"
)

l5 = Listing(
    name="Chicago Southside location",
    address="test123 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/house3.jpg",
    description="Cozy house that features 3 bedrooms, living room, and 3 bathrooms",
    location="Chicago IL",
    created="test_user"
)

l6 = Listing(
    name="Chicago Southside location",
    address="test123 st",
    image="https://sharebnb-dnd.s3.us-east-2.amazonaws.com/house4.jpg",
    description="Cozy house that features 3 bedrooms, living room, and 3 bathrooms",
    location="Chicago IL",
    created="test_user"
)


db.session.add_all([user_one, l1,l2,l3,l4,l5,l6])
db.session.commit()
