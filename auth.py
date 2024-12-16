from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, AuditLog
from . import db
import functools

auth = Blueprint('auth', __name__)

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Você não tem permissão para acessar esta página.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Por favor, verifique seus dados de login e tente novamente.', 'error')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        
        # Log the login
        log = AuditLog(
            user_id=user.id,
            action='login',
            entity_type='user',
            entity_id=user.id,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()

        return redirect(url_for('main.dashboard'))

    return render_template('auth/login.html')

@auth.route('/signup', methods=['GET', 'POST'])
@admin_required
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        role = request.form.get('role', 'user')

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email já cadastrado.', 'error')
            return redirect(url_for('auth.signup'))

        new_user = User(
            email=email,
            name=name,
            password_hash=generate_password_hash(password, method='sha256'),
            role=role
        )

        db.session.add(new_user)
        
        # Log the user creation
        log = AuditLog(
            user_id=current_user.id,
            action='create_user',
            entity_type='user',
            entity_id=new_user.id,
            details={'role': role},
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()

        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/signup.html')

@auth.route('/logout')
@login_required
def logout():
    # Log the logout
    log = AuditLog(
        user_id=current_user.id,
        action='logout',
        entity_type='user',
        entity_id=current_user.id,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
    
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')
