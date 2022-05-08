'''
This handles the forms
'''
from flask_wtf import FlaskForm
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

