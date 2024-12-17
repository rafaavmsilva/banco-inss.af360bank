from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import re

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Helper Functions
    def validate_cpf(cpf):
        cpf = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf) != 11:
            return False
            
        numbers = [int(digit) for digit in cpf]
        
        sum_of_products = sum(a*b for a, b in zip(numbers[0:9], range(10, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if numbers[9] != expected_digit:
            return False
            
        sum_of_products = sum(a*b for a, b in zip(numbers[0:10], range(11, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if numbers[10] != expected_digit:
            return False
            
        return True

    def get_bcb_interest_rate():
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/1?formato=json"
        try:
            response = requests.get(url)
            data = response.json()
            return float(data[0]['valor'])
        except:
            return 12.75

    def calculate_credit_score(cpf):
        cpf_sum = sum(int(digit) for digit in str(cpf) if digit.isdigit())
        base_score = (cpf_sum * 7) % 300 + 300
        return base_score

    def calculate_loan_limit(salary, score):
        base_limit = salary * 12
        score_multiplier = score / 600
        return min(base_limit * score_multiplier, salary * 20)

    # Routes
    @app.route('/api/simular-inss', methods=['POST', 'OPTIONS'])
    def simular_inss():
        if request.method == 'OPTIONS':
            return jsonify({}), 200
        # Rest of your code...

    @app.route('/api/simular-portabilidade', methods=['POST', 'OPTIONS'])
    def simular_portabilidade():
        if request.method == 'OPTIONS':
            return jsonify({}), 200
        # Rest of your code...

    @app.route('/api/solicitar-portabilidade-out', methods=['POST', 'OPTIONS'])
    def solicitar_portabilidade_out():
        if request.method == 'OPTIONS':
            return jsonify({}), 200
        # Rest of your code...

    @app.route('/api/simular-refinanciamento', methods=['POST', 'OPTIONS'])
    def simular_refinanciamento():
        if request.method == 'OPTIONS':
            return jsonify({}), 200
        # Rest of your code...

    return app  # Move return statement to end

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)