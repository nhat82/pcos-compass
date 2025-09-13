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

# class PeriodLogForm(FlaskForm):
#     start_date = DateTimeLocalField(
#         "Start Date and Time",
#         format="%Y-%m-%dT%H:%M",
#         default=datetime.datetime.now,
#         validators=[InputRequired()],
#     )
#     end_date = DateTimeLocalField(
#         "End Date and Time",
#         format="%Y-%m-%dT%H:%M",
#         default=datetime.datetime.now,
#         validators=[InputRequired()],
#     )
#     flow_intensity = StringField(
#         "Flow Intensity (light, medium, heavy)",
#         validators=[InputRequired(), Length(max=10)],
#     )
#     symptoms = SelectMultipleField(
#         "Symptoms (hold Ctrl or Cmd to select multiple)",
#         choices=[
#             ("cramps", "Cramps"),
#             ("bloating", "Bloating"),
#             ("headache", "Headache"),
#             ("fatigue", "Fatigue"),
#             ("nausea", "Nausea"),
#             ("back_pain", "Back Pain"),
#             ("breast_tenderness", "Breast Tenderness"),
#             ("mood_swings", "Mood Swings"),
#             ("acne", "Acne"),
#             ("other", "Other"),
#         ],
#     )
#     mood = StringField("Mood", validators=[Length(max=50)])
#     pain_level = StringField("Pain Level (0-10)", validators=[Length(max=2)])
#     medication_taken = SelectMultipleField(
#         "Medication Taken (hold Ctrl or Cmd to select multiple)",
#         choices=[
#             ("ibuprofen", "Ibuprofen"),
#             ("acetaminophen", "Acetaminophen"),
#             ("naproxen", "Naproxen"),
#             ("other", "Other"),
#         ],
#     )
#     notes = TextAreaField("Additional Notes", validators=[Length(max=500)])
#     submit = SubmitField("Submit Period Log")
    
# class OvulationLogForm(FlaskForm):
#     start_date = DateTimeLocalField(
#         "Start Date and Time",
#         format="%Y-%m-%dT%H:%M",
#         default=datetime.datetime.now,
#         validators=[InputRequired()],
#     )
#     end_date = DateTimeLocalField(
#         "End Date and Time",
#         format="%Y-%m-%dT%H:%M",
#         default=datetime.datetime.now,
#         validators=[InputRequired()],
#     )
#     ovulation_test_result = StringField(
#         "Ovulation Test Result (positive, negative, not_taken)",
#         validators=[Length(max=12)],
#     )
#     symptoms = SelectMultipleField(
#         "Symptoms (hold Ctrl or Cmd to select multiple)",
#         choices=[
#             ("mittelschmerz", "Mittelschmerz"),
#             ("increased_cervical_mucus", "Increased Cervical Mucus"),
#             ("breast_tenderness", "Breast Tenderness"),
#             ("heightened_senses", "Heightened Senses"),
#             ("fatigue", "Fatigue"),
#             ("mood_swings", "Mood Swings"),
#             ("acne", "Acne"),
#             ("other", "Other"),
#         ],
#     )
#     mood = StringField("Mood", validators=[Length(max=50)])
#     notes = TextAreaField("Additional Notes", validators=[Length(max=500)])
#     submit = SubmitField("Submit Ovulation Log")
    
# class LabLogForm(FlaskForm):
#     start_date = DateTimeLocalField(
#         "Date and Time",
#         format="%Y-%m-%dT%H:%M",
#         default=datetime.datetime.now,
#         validators=[InputRequired()],
#     )
#     test_name = StringField("Test Name", validators=[InputRequired(), Length(max=100)])
#     results_summary = TextAreaField("Results Summary", validators=[Length(max=1000)])
#     detailed_report = FileField(
#         "Upload Detailed Report (PDF, JPG, PNG)",
#         validators=[
#             FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], "Only PDF, JPG, JPEG, and PNG files are allowed"),
#         ],
#     )
#     notes = TextAreaField("Additional Notes", validators=[Length(max=500)])
#     submit = SubmitField("Submit Lab Log")
    
# class MedicationLogForm(FlaskForm):
#     start_date = DateTimeLocalField(
#         "Start Date and Time",
#         format="%Y-%m-%dT%H:%M",
#         default=datetime.datetime.now,
#         validators=[InputRequired()],
#     )
#     end_date = DateTimeLocalField(
#         "End Date and Time",
#         format="%Y-%m-%dT%H:%M",
#         default=datetime.datetime.now,
#         validators=[InputRequired()],
#     )
#     medication_name = StringField("Medication Name", validators=[InputRequired(), Length(max=100)])
#     dosage = StringField("Dosage", validators=[InputRequired(), Length(max=50)])
#     frequency = StringField("Frequency", validators=[InputRequired(), Length(max=50)])
#     notes = TextAreaField("Additional Notes", validators=[Length(max=500)])
#     submit = SubmitField("Submit Medication Log")
    
# class TemperatureLogForm(FlaskForm):
#     start_date = DateTimeLocalField(
#         "Date and Time",
#         format="%Y-%m-%dT%H:%M",
#         default=datetime.datetime.now,
#         validators=[InputRequired()],
#     )
#     temperature = StringField("Temperature (°F)", validators=[InputRequired(), Length(max=5)])
#     method = StringField("Method (oral, basal, ear, forehead, armpit)", validators=[Length(max=10)])
#     notes = TextAreaField("Additional Notes", validators=[Length(max=500)])
#     submit = SubmitField("Submit Temperature Log")
    
# def validate_temperature(form, field):
#     try:
#         temp = float(field.data)
#         if temp < 80.0 or temp > 110.0:
#             raise ValidationError("Temperature must be between 80.0°F and 110.0°F")
#     except ValueError:
#         raise ValidationError("Invalid temperature format. Please enter a numeric value.")

class DeleteAccountForm(FlaskForm):
    submit = SubmitField("Delete Account") 
    
    def validate_submit(self, field):
        if not current_user.is_authenticated:
            raise ValidationError("You must be logged in to delete your account.")
        user = User.objects(username=current_user.username).first()
        if not user:
            raise ValidationError("User not found.")
        return True
    