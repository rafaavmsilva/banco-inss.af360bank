from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)

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
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    
    # Configure login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
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
