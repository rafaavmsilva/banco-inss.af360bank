from flask import Flask, request, redirect, url_for, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

db = SQLAlchemy()
migrate = Migrate()

class INSSProposal(db.Model):
    __tablename__ = 'inss_proposals'
    
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(11), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    valor_beneficio = db.Column(db.Float, nullable=False)
    valor_emprestimo = db.Column(db.Float, nullable=False)
    prazo = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pendente')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def create_app():
    app = Flask(__name__)
    
    # Load environment variables
    load_dotenv()
    
    # Flask configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    @app.route('/')
    def index():
        token = request.args.get('token')
        if not token:
            return jsonify({'error': 'Token não fornecido'}), 401
            
        # Validar token com o sistema principal
        validation_url = f"https://af360bank.com/validate-token/{token}"
        try:
            response = requests.get(validation_url)
            if response.status_code != 200:
                return jsonify({'error': 'Token inválido'}), 401
        except requests.exceptions.RequestException:
            return jsonify({'error': 'Erro ao validar token'}), 500
            
        return render_template('index.html')

    @app.route('/propostas', methods=['GET'])
    def listar_propostas():
        propostas = INSSProposal.query.order_by(INSSProposal.created_at.desc()).all()
        return render_template('propostas.html', propostas=propostas)

    @app.route('/proposta/nova', methods=['GET', 'POST'])
    def nova_proposta():
        if request.method == 'POST':
            try:
                data = request.form
                proposta = INSSProposal(
                    cpf=data['cpf'],
                    nome=data['nome'],
                    data_nascimento=datetime.strptime(data['data_nascimento'], '%Y-%m-%d'),
                    valor_beneficio=float(data['valor_beneficio']),
                    valor_emprestimo=float(data['valor_emprestimo']),
                    prazo=int(data['prazo'])
                )
                db.session.add(proposta)
                db.session.commit()
                return redirect(url_for('listar_propostas'))
            except Exception as e:
                return jsonify({'error': str(e)}), 400
                
        return render_template('nova_proposta.html')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
