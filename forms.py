from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, ValidationError
from models import User
from passlib.hash import pbkdf2_sha256

def invalid_credentials(form,field):
    username_entered = form.username.data
    password_entered = field.data

    user_object = User.query.filter_by(username=form.username.data).first()
    if user_object is None:
        raise ValidationError('username or password is incorrect')
    
    elif not pbkdf2_sha256.verify(password_entered, user_object.password):
        raise ValidationError('username or password is incorrect')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators= [InputRequired(message="Username required"),
                            Length(min=4, max=25, message="Username must be at least 4 characters and atmost 25 characters")
                            ])
    password = PasswordField('Password',validators= [InputRequired(message="Password required"),
                            Length(min=4, max=25, message="Password must be at least 4 characters and atmost 25 characters")
                            ])
    confirm_password = PasswordField('Confirm password', validators= [InputRequired(message="Password required"),
                            EqualTo('password', message="Password must match!")
                            ])
    submit_button = SubmitField('create')

    def validate_username(self,username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError('Username already exists')
        
class LoginForm(FlaskForm):
    username = StringField('Username', validators= [InputRequired(message="Username required")])
    password = PasswordField('Password', validators= [InputRequired(message="Password required"), invalid_credentials])
    submit_button = SubmitField('Login')

