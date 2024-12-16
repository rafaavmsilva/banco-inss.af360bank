from flask import Flask, request, redirect, url_for, render_template, jsonify
from datetime import datetime
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Flask configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/propostas')
def listar_propostas():
    # For now, return an empty list of proposals
    return jsonify([])

@app.route('/nova-proposta', methods=['GET', 'POST'])
def nova_proposta():
    if request.method == 'POST':
        # Just return success for now
        return jsonify({"status": "success", "message": "Proposta recebida"})
    return render_template('nova_proposta.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
