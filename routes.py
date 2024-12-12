from flask import current_app as app
from flask import request, jsonify, render_template, flash
import requests
import os
from . import db
from .models import User

# BMP API Configuration
BMP_API_BASE_URL = "https://api.bmpbanco.com.br"
API_KEY = os.getenv("BMP_API_KEY")

@app.route("/", methods=["GET"])
def index():
    return render_template('dashboard.html')

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "BMP API Integration Service is running"})

@app.route("/usuarios", methods=["GET"])
def usuarios():
    try:
        users = User.query.all()
        return render_template('usuarios.html', users=users)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('usuarios.html', users=[])
