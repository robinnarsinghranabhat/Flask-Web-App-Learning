import os
import secrets
from PIL import Image
from dataclasses import dataclass
import email
from fileinput import filename
from flask_blog import app, bcrypt, db
from flask import render_template, flash, redirect, url_for, request, abort
from flask_blog.forms import RegistrationForm, LoginForm, AccountUpdateForm, PostForm
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
    page_num = request.args.get('page_num', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page_num)
    return render_template("home.html", posts=posts)


@app.route("/user/<string:username>")
def user_posts(username):
    """
    Show Posts by a particular User
    """
    # If user is not found, return a 404 Page not found directly.
    # no extra if else bullshit.
    page_num = request.args.get('page_num', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(per_page=5, page=page_num)
    return render_template("user_post.html", posts=posts, user=user)


# @app.route("/user_posts/")
# def home():
#     page_num = request.args.get('page_num', 2, type=int)
#     # Post.query.order_by()
#     posts = Post.query.paginate(per_page=5, page=page_num)
#     return render_template("home.html", posts=posts)

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


# THIS VIEW IS USING A POST/REDIRECT/GET Pattern
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ix-pagination
# Notice : After handling post-reqest, we redirect to this view itself.
# Because, when we submit form,  
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

        # flash("Account Sucessfully Updated", "success")
        return redirect( url_for('account'))

    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static',  filename='profile_pics/' + current_user.image_file)
    # NOTE : Additional arguments are be used as variables in jinja
    return render_template("account.html", title='Account Page', image_file=image_file, form=form)



@app.route("/post/new", methods=["GET", "POST"])
@login_required # Only Logged-in user can access view to create a new-post
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data, 
            content=form.content.data,
            author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(f'New Post Created !', "success")
        return redirect( url_for('home') )
    return render_template("create_post.html", title='New Post', legend='Create a new Post', form=form)


@app.route("/post/<int:post_id>", methods=["GET"])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)

from datetime import datetime

@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required # Only Logged-in user can update their own-post.
def update_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    # A Form to update things
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        # post.last_updated = datetime.utcnow
        db.session.commit()
        flash(f'Post Updated !', "success")
        return redirect( url_for('post' , post_id=post.id) )
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template("create_post.html", title='Update Post', legend= 'Update Post', form=form)


@app.route("/post/<int:post_id>/delete", methods=["GET", "POST"])
@login_required # Only Logged-in user can update their own-post.
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author != current_user:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash(f'Post Deleted !', "success")
    return redirect(url_for('home'))