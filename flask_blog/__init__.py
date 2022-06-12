from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

## Internally it just uses some configs from app. 
bcrypt = Bcrypt(app)

## for handling logins
# SOMETHING INTERESTING IS HAPPENING HERE
# inside LoginManager.init_app method, we are attaching login_manager object 
# to our `app` object itself as : app.login_manager = self
# This is interesting grounds through where I am walking.  
login_manager = LoginManager(app)

## MORE INTERESTING IS :
# Since app.login_manager and login_manager are pointing to same address 
# in Memory.
# Changes to login_manager below, will reflect changes in 
# app.login_manager as well.
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Here is where the magic happes. 
# We add view-functions to the above initialized "app" object 
# through cunning use of decorators.
from flask_blog import routes