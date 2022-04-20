from flask_blog import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True )
    username = db.Column(db.String(20), unique=True, nullable=False )
    email = db.Column(db.String(120), unique=True, nullable=False )
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg' )
    password = db.Column( db.String(60), nullable=False )
    ## We are referencing the `Post` Model.
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self) -> str:
        return f"User - {self.username} | Email - {self.email} | Password - {self.password}"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True )
    title = db.Column(db.String(100), nullable=False )
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow )
    content = db.Column( db.Text, nullable=False )
    ## For each Model, default name for table will be Lowercase Name of the class.
    ## That's why it's referencing table-name for User Class.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        return f"Title - {self.title} | Date - {self.date_posted} |  - {self.content[:20]}"
