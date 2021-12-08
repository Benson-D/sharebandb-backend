# ShareBnb-backend 
- ShareBnB is full stack web application based off an airbnb clone. The frontend consist of TypeScript, React and Bootstrap. The backend utilizes Python, Flask, PostgreSQL, SQLAlchemy, and AWS S3 cloud storage.
- For more details on the frontend documentation please click [here](https://github.com/Benson-D/sharebnb-frontend)

## Current Features 
- Contains a database for users, listings, and messages
- Uploads a file and connects with AWS S3 cloud storage
- Utilizes CRUD endpoints for users, listings, and messages
- Queries to a specific listing location 

## Installation
**Create Virtual Environment**
- Once in you're in your venv install the requirements needed for the application
```console
python3 -m venv venv
source venv/bin/activate
(venv) pip3 install -r requirements.txt
```
**Create Database**
```console
(venv) createdb sharebnb
(venv) python3 seed.py
```
**Start your local server** 
- Run the second command if Flask environment is not set to development
```console
(venv) flask run
(venv) FLASK_ENV=development flask run
```
