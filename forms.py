'''
This handles the forms
'''
from tokenize import String
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

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

