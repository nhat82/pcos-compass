from flask import Flask 
from flask_migrate import Migrate
from database import db
from controllers.events_controller import events_bp 
from flask_sqlalchemy import SQLAlchemy

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://minhnhat:minhnhat@localhost:5432/pcos"
    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(events_bp)
    
    with app.app_context():
        db.create_all()
        
    return app