from flask import Flask, request, jsonify, render_template, flash, redirect, url_for, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from functools import wraps
from auth_client import AuthClient
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

# INSS Proposal Model
class INSSProposal(db.Model):
    __tablename__ = 'inss_proposals'
    
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), nullable=False)
    proposal_type = db.Column(db.String(20), nullable=False)  # 'new', 'portability', 'refinancing'
    proposal_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            # Store the requested URL for redirecting after authentication
            session['next_url'] = request.url
            return redirect(url_for('auth_login'))
        return f(*args, **kwargs)
    return decorated_function

def create_app():
    app = Flask(__name__)
    
    # Basic configuration
    app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Sessions last 24 hours
    app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie
    Session(app)
    
    # Database configuration - Using SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # Auth client initialization
    auth_client = AuthClient(
        auth_server_url=os.getenv('AUTH_SERVER_URL', 'https://af360bank.onrender.com'),
        app_name=os.getenv('APP_NAME', 'sistema-comissoes')
    )
    auth_client.init_app(app)

    @app.route('/')
    @login_required
    def dashboard():
        """Dashboard page"""
        proposals = INSSProposal.query.all()
        pending_count = sum(1 for p in proposals if p.status == 'pending')
        approved_count = sum(1 for p in proposals if p.status == 'approved')
        rejected_count = sum(1 for p in proposals if p.status == 'rejected')
        total_count = len(proposals)
        
        return render_template('dashboard.html',
                             pending_count=pending_count,
                             approved_count=approved_count,
                             rejected_count=rejected_count,
                             total_count=total_count)

    @app.route('/inss/novo', methods=['GET', 'POST'])
    @login_required
    def inss_novo():
        if request.method == 'POST':
            data = request.form
            proposal = INSSProposal(
                cpf=data['cpf'],
                proposal_type='new'
            )
            db.session.add(proposal)
            db.session.commit()
            flash('Proposta criada com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('inss/novo.html')

    @app.route('/inss/portabilidade', methods=['GET', 'POST'])
    @login_required
    def inss_portabilidade():
        if request.method == 'POST':
            data = request.form
            proposal = INSSProposal(
                cpf=data['cpf'],
                proposal_type='portability'
            )
            db.session.add(proposal)
            db.session.commit()
            flash('Proposta de portabilidade criada com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('inss/portabilidade.html')

    @app.route('/inss/portabilidade-out', methods=['GET', 'POST'])
    @login_required
    def inss_portabilidade_out():
        if request.method == 'POST':
            data = request.form
            proposal = INSSProposal(
                cpf=data['cpf'],
                proposal_type='portability_out'
            )
            db.session.add(proposal)
            db.session.commit()
            flash('Proposta de portabilidade out criada com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('inss/portabilidade_out.html')

    @app.route('/inss/refinanciamento', methods=['GET', 'POST'])
    @login_required
    def inss_refinanciamento():
        if request.method == 'POST':
            data = request.form
            proposal = INSSProposal(
                cpf=data['cpf'],
                proposal_type='refinancing'
            )
            db.session.add(proposal)
            db.session.commit()
            flash('Proposta de refinanciamento criada com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('inss/refinanciamento.html')

    @app.route('/auth/login')
    def auth_login():
        """Initiate the authentication process"""
        redirect_uri = url_for('auth_callback', _external=True)
        return redirect(auth_client.get_authorization_url(redirect_uri))

    @app.route('/auth/callback')
    def auth_callback():
        """Handle the authentication callback from AF360 Bank"""
        code = request.args.get('code')
        if not code:
            flash('Authentication failed. Please try again.', 'error')
            return redirect(url_for('dashboard'))

        try:
            # Exchange the code for an access token
            token_response = auth_client.get_token(code, url_for('auth_callback', _external=True))
            
            if token_response and token_response.get('access_token'):
                session['authenticated'] = True
                session['access_token'] = token_response['access_token']
                
                # Redirect to the originally requested URL if it exists
                next_url = session.pop('next_url', None)
                if next_url:
                    return redirect(next_url)
                return redirect(url_for('dashboard'))
            else:
                flash('Failed to obtain access token', 'error')
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            flash(f'Authentication error: {str(e)}', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/auth/logout')
    def auth_logout():
        """Handle user logout"""
        session.clear()
        return redirect(url_for('dashboard'))

    return app

# Create the application instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
