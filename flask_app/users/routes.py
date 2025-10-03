from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from io import BytesIO
from werkzeug.utils import secure_filename
from ..extensions import bcrypt 
from ..forms import RegistrationForm, LoginForm, ProblemForm, TreatmentForm
from ..models import * 
from ..config import GOOGLE_FORM_LINK
from flask_app.constants import SYMPTOMS, TREATMENTS
import datetime

users = Blueprint('users', __name__)

''' User Management Views '''

@users.route('/')
def home():
    return render_template('home.html', google_form_link=GOOGLE_FORM_LINK)


@users.route('/community')
def community():
    return render_template('community.html')

@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        new_user.save()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('logs.logs_page'))
    
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('logs.logs_page'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('users.home'))


def log_problem(user, problem_name, details=""):
    """Logs a symptom/problem if not already logged."""
    # Check if problem already exists for this user
    existing_problem = Problem.objects(name=problem_name, user=user).first()
    if existing_problem:
        return False, f"'{problem_name}' has already been logged."
    
    # Create new problem
    new_problem = Problem(
        name=problem_name,  # Use the problem_name parameter
        user=user,
        details=details
    )
    new_problem.save()
    user.problems.append(new_problem)
    user.save()
    return True, f"'{problem_name}' logged successfully."



@users.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user._get_current_object()
    problem_form = ProblemForm(prefix="problem")

    # Inject choices dynamically
    problem_form.symptoms.choices = [(s, s) for s in SYMPTOMS]

    if problem_form.submit.data and problem_form.validate_on_submit():
        messages = []
        # Log selected symptoms from the dropdown
        for symptom in problem_form.symptoms.data:
            if symptom in SYMPTOMS:
                success, msg = log_problem(user, symptom)  # Pass the symptom string
                messages.append((success, msg))
            else:
                messages.append((False, f"'{symptom}' is not a valid symptom."))
        
        # Log custom symptom
        custom_symptom = problem_form.custom_symptom.data
        if custom_symptom:
            success, msg = log_problem(user, custom_symptom)  # Pass the custom symptom string
            messages.append((success, msg))
        
        for success, msg in messages:
            flash(msg, "success" if success else "warning")
        return redirect(url_for('users.profile'))

    # Render page
    user_symptoms = Problem.objects(user=user)
    user_treatments = Log.objects(user=user, type="Treatment")
    return render_template(
        "profile.html",
        problem_form=problem_form,
        user_symptoms=user_symptoms,
        user_treatments=user_treatments,
        user=user
    )
