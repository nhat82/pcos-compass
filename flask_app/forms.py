from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, SelectMultipleField, DateTimeLocalField, SelectField
from wtforms.validators import (
    InputRequired,
    Length,
    Email,
    EqualTo,
    ValidationError,
)
from .models import User, Log
import datetime 

class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            InputRequired(),
            Length(min=4, max=20, message="Username must be between 4 and 20 characters"),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            InputRequired(),
            Email(message="Invalid email address"),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            Length(min=6, message="Password must be at least 6 characters long"),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user:
            raise ValidationError("Username already exists. Please choose a different one.")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError("Email already registered. Please choose a different one.")
        
class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min=4, max=20)],
    )
    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min=6)],
    )
    submit = SubmitField("Login")

class LogForm(FlaskForm):
    notes = TextAreaField("Notes", validators=[Length(max=500)])
    start_date = DateTimeLocalField(
        "Start Date and Time",
        format="%Y-%m-%dT%H:%M",
        default=datetime.datetime.now,
        validators=[InputRequired()],
    )
    end_date = DateTimeLocalField(
        "End Date and Time",
        format="%Y-%m-%dT%H:%M",
        default=datetime.datetime.now,
        validators=[InputRequired()],
    )
    submit = SubmitField("Submit Log")

class LogForm(FlaskForm):
    title = StringField("Log Title", validators=[InputRequired()])
    submit = SubmitField("Save")

class DeleteAccountForm(FlaskForm):
    submit = SubmitField("Delete Account") 
    
    def validate_submit(self, field):
        if not current_user.is_authenticated:
            raise ValidationError("You must be logged in to delete your account.")
        user = User.objects(username=current_user.username).first()
        if not user:
            raise ValidationError("User not found.")
        return True
    


class SearchPlaceForm(FlaskForm):
    search_query = StringField("Search Place", validators=[InputRequired(), Length(max=100)])
    submit = SubmitField("Search")

        
class ReviewForm(FlaskForm):
    rating = SelectField(
        "Rating",
        choices=[(str(i), i) for i in range(1, 6)],
        validators=[InputRequired()],
    )
    comment = TextAreaField("Comment", validators=[Length(max=1000)])
    submit = SubmitField("Submit Review")
    
    
    