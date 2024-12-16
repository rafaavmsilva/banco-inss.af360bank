from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

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
    app.secret_key = 'dev-key-123'  # Change this in production
    
    # Database configuration - Using SQLite
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    @app.route('/')
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

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
