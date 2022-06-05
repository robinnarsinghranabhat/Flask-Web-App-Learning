'''
This handles the forms
'''
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from flask_blog.models import User, Post


class RegistrationForm(FlaskForm):

    username = StringField( 
                "Username", 
                validators=[ 
                    DataRequired(), Length(min=4, max=24) 
                    ])
    email = StringField(
        'Email', 
        validators=[
            DataRequired(), Email()
        ]
    )

    password = PasswordField('Password',
        validators=[DataRequired()]    
    )
    confirm_password = PasswordField('Confirm Password',
        validators=[DataRequired(), EqualTo('password')]    
    )

    submit = SubmitField('Sign Up')

    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username is taken. Please try another name.")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError("Email is taken. Please try another name.")


class LoginForm(FlaskForm):

    username = StringField( 
                "Username", )
    email = StringField(
        'Email', 
        validators=[
            DataRequired(), Email()
        ]
    )

    password = PasswordField('Password',
        validators=[DataRequired()]    
    )

    remember = BooleanField('remember-me')
    submit = SubmitField('Login')



class AccountUpdateForm(FlaskForm):

    username = StringField( 
                "Username", 
                validators=[ 
                    DataRequired(), Length(min=4, max=24) 
                    ])
    email = StringField(
        'Email', 
        validators=[
            DataRequired(), Email()
        ]
    )
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png']) ])

    submit = SubmitField('Update')

    def validate_username(self, username):
        # if new name is same as old one, then ignore anything.
        # But a flash-message like : "Same Name. Ignoring Update"
        # could do as well 
        # otherwise, check if the new name we choose is already present
        # in the database. and raise error if the name exists. 
        # FlaskForm automatically Shows all Validation Error as neat-css.
        if username.data != current_user.username:

            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("Username is taken. Please try another name.")

    def validate_email(self, email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError("Email is taken. Please try another name.")