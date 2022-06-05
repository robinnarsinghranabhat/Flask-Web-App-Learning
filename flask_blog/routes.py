import os
import secrets
from PIL import Image
from dataclasses import dataclass
import email
from fileinput import filename
from flask_blog import app, bcrypt, db
from flask import render_template, flash, redirect, url_for, request
from flask_blog.forms import RegistrationForm, LoginForm, AccountUpdateForm
from flask_blog.models import User, Post

# current_user varaible invokes a function 
# that returns a user if someone is logged in. 
from flask_login import login_user, current_user, logout_user, login_required, user_accessed

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

    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username = form.username.data,
            email = form.email.data,
            password = hashed_password,
        )

        db.session.add(user)
        db.session.commit()

        flash(f'Account Created for {form.username.data} . Now you can log in !', "success")
        return redirect( url_for('login') )
    return render_template("register.html", title='Register', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    # import pdb; pdb.set_trace()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            # If we try to access views like : "settings", "account"; 
            # without being logged in, we are redirected to login-view.
            # As per below code in __init__.py.
            # login_manager.login_view = 'login'
            # login_manager.login_message_category = 'info'
            # But the query_string will be : http://127.0.0.1:5000/login?next=%2Faccount'
            # browser remembers that, after login though, we need to go to "account" view.

            # To implement that, we use code below.
            next_page = request.args.get('next') #.strip('/')
            if next_page:
                next_page = next_page.strip('/')
            # Without above line, we would normally not continue our visit to "account"
            # but go to home page.
            return redirect(url_for(next_page)) if next_page else redirect(url_for('home'))
        else:
            flash(f'Invalid Username or Password', "danger",)

    return render_template("login.html", title='Login', form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(nbytes=8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_save_path = os.path.join( app.root_path, 'static/profile_pics' , picture_fn )
    i = Image.open( form_picture )
    # resize here
    i.thumbnail = (125,125)
    i.save(picture_save_path)

    return picture_fn


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """
    This view updates the account information :
    - username
    - email
    - Profile Image of User
    """

    form = AccountUpdateForm()

    if form.validate_on_submit():

        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()

        flash("Account Sucessfully Updated", "success")
        return redirect( url_for('account'))

    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static',  filename='profile_pics/' + current_user.image_file)
    # NOTE : Additional arguments are be used as variables in jinja
    return render_template("account.html", title='Account Page', image_file=image_file, form=form)