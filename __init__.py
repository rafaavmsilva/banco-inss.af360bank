from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    # Load environment variables
    load_dotenv()
    
    app = Flask(__name__)
    CORS(app)
    
    # Flask configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://af360bank_db_user:jAO3e85X5e7cuDzIYpCpuGyo5VeVcRPy@dpg-ctcr4taj1k6c73flmt1g-a/af360bank_db').replace('postgres://', 'postgresql://')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Import routes
        from . import routes
        
        # Initialize database
        try:
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
    
    return app
