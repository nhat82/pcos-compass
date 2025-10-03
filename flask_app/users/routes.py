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


# @users.route('/profile', methods=['GET', 'POST'])
# @login_required
# def profile():
#     global SYMPTOMS
#     problem_form = ProblemForm()

#     if request.method == 'POST' and problem_form.validate_on_submit():
#         # Assume `symptoms` is a SelectMultipleField in ProblemForm
#         selected_symptoms = problem_form.symptoms.data  
#         added_any = False

#         for symptom in selected_symptoms:
#             # Validate against predefined list (or allow custom if you want)
#             if symptom not in SYMPTOMS:
#                 flash(f"'{symptom}' is not a valid symptom.", 'danger')
#                 continue

#             existing_problem = Problem.objects(
#                 name=symptom,
#                 user=current_user._get_current_object()
#             ).first()

#             if existing_problem:
#                 flash(f"'{symptom}' has already been logged.", 'warning')
#             else:
#                 new_problem = Problem(
#                     name=symptom,
#                     user=current_user._get_current_object(),
#                     solved = False
#                 )
#                 new_problem.save()
#                 current_user.problems.append(new_problem)
#                 current_user.save()
#                 added_any = True

#         if added_any:
#             flash('Symptoms logged successfully!', 'success')
        
#         custom_symptom = problem_form.custom_symptom.data
#         if custom_symptom:
#             existing_problem = Problem.objects(
#                 name=custom_symptom,
#                 user=current_user._get_current_object()
#             ).first()
#             if existing_problem:
#                 flash(f"'{custom_symptom}' has already been logged.", 'warning')
#             else:
#                 new_problem = Problem(
#                     name=custom_symptom,
#                     user=current_user._get_current_object(),
#                     solved=False
#                 )
#                 new_problem.save()
#                 current_user.problems.append(new_problem)
#                 current_user.save()
#                 flash('Custom symptom logged successfully!', 'success')
        
#         return redirect(url_for('users.profile'))

#     # Pass available symptoms + user’s existing logged symptoms
#     user_symptoms = Problem.objects(user=current_user._get_current_object())
#     return render_template('profile.html',
#                            form=problem_form,
#                            symptoms=SYMPTOMS,
#                            user_symptoms=user_symptoms,
#                            user=current_user)
    
    



def log_problem(user, form):
    """Logs a symptom/problem if not already logged."""
    existing_problem = Problem.objects(name=form.name.data, user=user).first()
    if existing_problem:
        return False, f"'{form.name.data}' has already been logged."
    
    new_problem = Problem(
        name=form.name.data,
        user=user,
        details = form.details.data, 
        solved=False
    )
    new_problem.save()
    user.problems.append(new_problem)
    user.save()
    return True, f"'{form.name.data}' logged successfully."


def log_treatment(user, form):
    """Logs a treatment from a TreatmentForm."""
    ongoing = form.ongoing.data == "true"
    new_treatment = Treatment(
        name=form.name.data,
        user=user,
        start_date=form.start_date.data,
        end_date=form.end_date.data,
        details=form.details.data
    )
    new_treatment.save()
    user.treatments.append(new_treatment)
    user.save()
    
    return f"Treatment '{form.name.data}' logged successfully!"



@users.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = current_user._get_current_object()

    problem_form = ProblemForm(prefix="problem")
    treatment_form = TreatmentForm(prefix="treatment")

    # Inject choices dynamically
    problem_form.symptoms.choices = [(s, s) for s in SYMPTOMS]
    treatment_form.name.choices = [(t, t) for t in TREATMENTS]

    if problem_form.submit.data and problem_form.validate_on_submit():
        messages = []
        for symptom in problem_form.symptoms.data:
            if symptom in SYMPTOMS:
                success, msg = log_problem(user, symptom)
                messages.append((success, msg))
            else:
                messages.append((False, f"'{symptom}' is not a valid symptom."))
        custom_symptom = problem_form.custom_symptom.data
        if custom_symptom:
            success, msg = log_problem(user, custom_symptom)
            messages.append((success, msg))
        for success, msg in messages:
            flash(msg, "success" if success else "warning")
        return redirect(url_for('users.profile'))

    elif treatment_form.submit.data and treatment_form.validate_on_submit():
        msg = log_treatment(user, treatment_form)
        flash(msg, "success")
        return redirect(url_for('users.profile'))

    # Render page
    user_symptoms = Problem.objects(user=user)
    user_treatments = Treatment.objects(user=user)
    return render_template(
        "profile.html",
        problem_form=problem_form,
        treatment_form=treatment_form,
        user_symptoms=user_symptoms,
        user_treatments=user_treatments,
        user=user
    )
