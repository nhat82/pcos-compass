from flask import Flask, render_template
from .extensions import db, login_manager, bcrypt

from flask_login import (
    LoginManager, 
    current_user, 
    login_user, 
    logout_user, 
    login_required
)

from werkzeug.utils import secure_filename
from .users.routes import users
from .logs.routes import logs
from .places.routes import places


def custom_404(e):
    return render_template("404.html"), 404

def create_app(test_config=None):
    app = Flask(__name__)
    
    app.config.from_pyfile("config.py", silent=False)
    if test_config:
        app.config.update(test_config)
        
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    app.register_blueprint(users)
    app.register_blueprint(logs)
    app.register_blueprint(places)
    
    app.register_error_handler(404, custom_404)
    
    login_manager.login_view = "users.login"
    
    return app
        