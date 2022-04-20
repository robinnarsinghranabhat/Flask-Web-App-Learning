from email.policy import default
from enum import unique
import re
from flask import Flask, render_template, flash, redirect, url_for, request
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from models import User, Post

app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' 
db = SQLAlchemy(app)

posts = [
    {
        'author' : 'Robin',
        'title' : 'First blog post',
        'content' : "You can try to read my lyrics off my myan. But you won't get to stop me from causing mayhem",
        'date_posted' : '2021-01-21',
    },
    {
        'author' : 'In nin',
        'title' : 'Second blog post',
        'content' : "If the mocking bird doesn't like you, I will break that birdy's neck",
        'date_posted' : '2021-01-21',
    }
]

## First things first
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=posts)

@app.route("/about")
def about_page():
    return render_template("about.html", title='Da gay')


## Adding the form registration part
@app.route("/register", methods=["GET", "POST"])
def register():

    ## Something interesting is happening here ##
    # Internally, during `form` object initializing, 
    # it will get initialized with values from request.form
    # In a get request, request.form will be none. 
    # NOTE : `request` is a global object in flask, like `session` anmd
    # `current` app. 
    # But in a post-request,  `form` object will have data.
    # Even though it may look like a new `form` object is being initialized.  

    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account Created for {form.username.data}', "success")
        return redirect( url_for('home') )
    return render_template("register.html", title='Register', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    # import pdb; pdb.set_trace()
    if form.validate_on_submit():
        if form.email.data == 'robin@gmail.com' and form.password.data == 'password':
            flash(f'{form.username.data} Logged In !', "success")
            return redirect( url_for('home') )
        else:
            flash(f'Invalid Username or Password', "danger",)

    return render_template("login.html", title='Login', form=form)


if __name__ == "__main__":

    ## Internally, 
    # app.run --> werkzeug.serving.run_simple -> 
    # werkzueg.serving.make_server().run_forever() || this is just a  While LOOP
    # Listening to Request !!!! 
    app.run(debug=True)