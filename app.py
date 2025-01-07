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
import logging

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        app_name="banco-af360bank"
    )
    auth_client.init_app(app)

    # Use auth_client's login_required instead of local one
    login_required = auth_client.login_required

    @app.route('/login')
    def login():
        """Redirect to auth server login"""
        return redirect(os.getenv('AUTH_SERVER_URL', 'https://af360bank.onrender.com') + '/login')

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
            cpf = data['cpf']
            
            # Chamada à API da Receita Federal
            api_url = f"https://apigateway.conectagov.estaleiro.serpro.gov.br/api-beneficios-previdenciarios/v3/beneficios?cpf={cpf}"
            headers = {
                "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
                "Content-Type": "application/json"
            }
            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                # Processar a resposta da API e criar a proposta
                proposal = INSSProposal(
                    cpf=cpf,
                    proposal_type='new',
                    proposal_id=result.get('id', 'N/A'),
                    status='pending'
                )
                db.session.add(proposal)
                db.session.commit()
                flash('Proposta criada com sucesso!', 'success')
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao criar proposta de novo empréstimo: {e}")
                flash('Erro ao criar proposta de novo empréstimo', 'danger')
            
            return redirect(url_for('dashboard'))
        return render_template('inss/novo.html')

    @app.route('/inss/portabilidade', methods=['GET', 'POST'])
    @login_required
    def inss_portabilidade():
        if request.method == 'POST':
            data = request.form
            cpf = data['cpf']
            
            # Chamada à API da Receita Federal
            api_url = f"https://apigateway.conectagov.estaleiro.serpro.gov.br/api-beneficios-previdenciarios/v3/beneficios/pertence-especie?cpf={cpf}"
            headers = {
                "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
                "Content-Type": "application/json"
            }
            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                # Processar a resposta da API e criar a proposta
                proposal = INSSProposal(
                    cpf=cpf,
                    proposal_type='portability',
                    proposal_id=result.get('id', 'N/A'),
                    status='pending'
                )
                db.session.add(proposal)
                db.session.commit()
                flash('Proposta de portabilidade criada com sucesso!', 'success')
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao criar proposta de portabilidade: {e}")
                flash('Erro ao criar proposta de portabilidade', 'danger')
            
            return redirect(url_for('dashboard'))
        return render_template('inss/portabilidade.html')

    @app.route('/inss/portabilidade-out', methods=['GET', 'POST'])
    @login_required
    def inss_portabilidade_out():
        if request.method == 'POST':
            data = request.form
            cpf = data['cpf']
            
            # Chamada à API da Receita Federal
            api_url = f"https://apigateway.conectagov.estaleiro.serpro.gov.br/api-beneficios-previdenciarios/v3/beneficios/pertence-especie-87?cpf={cpf}"
            headers = {
                "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
                "Content-Type": "application/json"
            }
            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                # Processar a resposta da API e criar a proposta
                proposal = INSSProposal(
                    cpf=cpf,
                    proposal_type='portability_out',
                    proposal_id=result.get('id', 'N/A'),
                    status='pending'
                )
                db.session.add(proposal)
                db.session.commit()
                flash('Proposta de portabilidade out criada com sucesso!', 'success')
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao criar proposta de portabilidade out: {e}")
                flash('Erro ao criar proposta de portabilidade out', 'danger')
            
            return redirect(url_for('dashboard'))
        return render_template('inss/portabilidade_out.html')

    @app.route('/inss/refinanciamento', methods=['GET', 'POST'])
    @login_required
    def inss_refinanciamento():
        if request.method == 'POST':
            data = request.form
            cpf = data['cpf']
            
            # Chamada à API da Receita Federal
            api_url = f"https://apigateway.conectagov.estaleiro.serpro.gov.br/api-beneficios-previdenciarios/v3/beneficios?cpf={cpf}"
            headers = {
                "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
                "Content-Type": "application/json"
            }
            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()
                result = response.json()
                
                # Processar a resposta da API e criar a proposta
                proposal = INSSProposal(
                    cpf=cpf,
                    proposal_type='refinancing',
                    proposal_id=result.get('id', 'N/A'),
                    status='pending'
                )
                db.session.add(proposal)
                db.session.commit()
                flash('Proposta de refinanciamento criada com sucesso!', 'success')
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao criar proposta de refinanciamento: {e}")
                flash('Erro ao criar proposta de refinanciamento', 'danger')
            
            return redirect(url_for('dashboard'))
        return render_template('inss/refinanciamento.html')

    @app.route('/simulate_inss', methods=['POST'])
    def simulate_inss():
        try:
            # Código que realiza a simulação de INSS
            data = request.json
            cpf = data.get('cpf')
            
            # Chamada à API da Receita Federal
            api_url = f"https://apigateway.conectagov.estaleiro.serpro.gov.br/api-beneficios-previdenciarios/v3/beneficios?cpf={cpf}"
            headers = {
                "Authorization": f"Bearer {os.getenv('API_TOKEN')}",
                "Content-Type": "application/json"
            }
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return jsonify(result)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao realizar simulação de INSS: {e}")
            return jsonify({"error": "Erro ao realizar simulação"}), 500

    @app.route('/auth/login')
    def auth_login():
        """Initiate the authentication process"""
        redirect_uri = url_for('auth_callback', _external=True)
        return redirect(auth_client.get_authorization_url(redirect_uri))

    @app.route('/auth/logout')
    def auth_logout():
        """Handle user logout"""
        session.clear()
        return redirect(url_for('dashboard'))

    @app.route('/social_security/benefits_request', methods=['POST'])
    def benefits_request():
        data = request.json
        cpf = data.get('cpf')
        legal_representative_document_number = data.get('legal_representative_document_number')
        signer = data.get('signer')
        authorization_term = data.get('authorization_term')

        # Simulação de resposta com base no primeiro dígito do CPF
        first_digit = cpf[0]
        if first_digit == '1':
            # Sucesso
            return jsonify({
                "status": "Success",
                "benefit_status": "Elegible"
            }), 200
        else:
            # Falha
            return jsonify({
                "status": "Failure",
                "enumerator": "inexistent_beneficiary",
                "description": "no beneficiary found"
            }), 400

    @app.route('/social_security/balance_request', methods=['POST'])
    def balance_request():
        data = request.json
        cpf = data.get('cpf')
        legal_representative_document_number = data.get('legal_representative_document_number')
        signer = data.get('signer')
        authorization_term = data.get('authorization_term')

        # Simulação de resposta com base no primeiro dígito do CPF
        first_digit = cpf[0]
        if first_digit == '1':
            # Sucesso
            return jsonify({
                "status": "Success",
                "assistance_type": "retirement_by_age",
                "benefit_status": "active",
                "has_entity_representation": False,
                "alimony_code": "not_payer",
                "has_judicial_concession": False,
                "has_power_of_attorney": False,
                "credit_type": "checking_account",
                "benefit_situation": "active",
                "used_total_balance": 1000.00,
                "max_total_balance": 5000.00,
                "available_total_balance": 4000.00,
                "benefit_quota_expiration_date": None,
                "block_type": "0",
                "politically_exposed": {
                    "type": "0",
                    "is_politically_exposed": False
                }
            }), 200
        else:
            # Falha
            return jsonify({
                "status": "Failure",
                "enumerator": "inexistent_beneficiary",
                "description": "no beneficiary found"
            }), 400

    @app.route('/debt_simulation', methods=['POST'])
    def debt_simulation():
        data = request.json
        borrower = data.get('borrower')
        financial = data.get('financial')
        collaterals = data.get('collaterals')
        refinanced_credit_operations = data.get('refinanced_credit_operations', [])

        # Simulação de resposta
        return jsonify({
            "status": "Success",
            "installment_value": financial['installment_face_value'],
            "disbursed_amount": financial['installment_face_value'] * financial['number_of_installments']
        }), 200

    @app.route('/debt', methods=['POST'])
    def create_debt():
        data = request.json
        borrower = data.get('borrower')
        financial = data.get('financial')
        collaterals = data.get('collaterals')
        related_parties = data.get('related_parties', [])
        additional_data = data.get('additional_data', {})
        disbursement_bank_accounts = data.get('disbursement_bank_accounts', [])

        # Simulação de resposta
        return jsonify({
            "status": "Success",
            "debt_key": "DEBT-KEY-12345"
        }), 200

    @app.route('/upload', methods=['POST'])
    def upload_document():
        # Simulação de upload de documento
        return jsonify({
            "document_key": "DOCUMENT-KEY-12345"
        }), 200

    @app.route('/debt/<debt_key>/signed', methods=['POST'])
    def sign_debt(debt_key):
        data = request.json
        ip_address = data.get('ip_address')
        signature_datetime = data.get('signature_datetime')

        # Simulação de resposta
        return jsonify({
            "status": "Success"
        }), 200

    @app.route('/debt/<debt_key>/cancel_permanently', methods=['POST'])
    def cancel_debt_permanently(debt_key):
        # Simulação de cancelamento permanente
        return jsonify({
            "status": "canceled_permanently"
        }), 200

    @app.route('/debt/<debt_key>/change_disbursement_date', methods=['POST'])
    def change_disbursement_date(debt_key):
        data = request.json
        new_disbursement_date = data.get('new_disbursement_date')

        # Simulação de resposta
        return jsonify({
            "status": "Success",
            "new_disbursement_date": new_disbursement_date
        }), 200

    @app.route('/debt/<debt_key>/collateral', methods=['GET'])
    def get_last_response(debt_key):
        # Simulação de resposta
        return jsonify({
            "status": "Success",
            "enumerator": "successfully_included",
            "reservation_method": "new_credit"
        }), 200

    @app.route('/webhook', methods=['POST'])
    def webhook():
        data = request.json
        webhook_type = data.get('webhook_type')
        status = data.get('status')

        # Simulação de resposta
        return jsonify({
            "status": "Received"
        }), 200

    return app

# Create the application instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)