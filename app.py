# app.py
from flask import Flask, render_template
from flask_migrate import Migrate
from database import db
from controllers.events_controller import events_bp
from flask_cors import CORS 

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://minhnhat:minhnhat@localhost:5432/pcos"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)

    # Register blueprints
    app.register_blueprint(events_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
        
    @app.route("/")
    def index():
        return render_template("index.html")
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)