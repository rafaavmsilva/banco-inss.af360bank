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
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
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

    @app.route('/api/simular-inss', methods=['POST'])
    def simular_inss():
        try:
            data = request.json
            required_fields = ['cpf', 'salary', 'loan_amount', 'installments']
            if not all(field in data for field in required_fields):
                return jsonify({
                    "error": "Missing required fields",
                    "required_fields": required_fields
                }), 400

            cpf = data.get('cpf', '').replace('.', '').replace('-', '')
            salary = float(data.get('salary', 0))
            loan_amount = float(data.get('loan_amount', 0))
            installments = int(data.get('installments', 0))

            if not validate_cpf(cpf):
                return jsonify({"error": "CPF inválido"}), 400

            if salary <= 0 or loan_amount <= 0 or installments <= 0:
                return jsonify({"error": "Valores inválidos para salário, valor do empréstimo ou parcelas"}), 400

            credit_score = calculate_credit_score(cpf)
            loan_limit = calculate_loan_limit(salary, credit_score)

            if loan_amount > loan_limit:
                return jsonify({
                    "error": "Valor do empréstimo excede o limite disponível",
                    "available_limit": loan_limit
                }), 400

            base_rate = get_bcb_interest_rate()
            monthly_rate = (base_rate + 2) / 12 / 100
            monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate)**installments) / ((1 + monthly_rate)**installments - 1)

            simulation_response = {
                "success": True,
                "data": {
                    "proposal_id": f"PROP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "monthly_payment": round(monthly_payment, 2),
                    "annual_interest_rate": round(base_rate + 2, 2),
                    "total_amount": round(monthly_payment * installments, 2),
                    "installments": installments,
                    "loan_amount": loan_amount
                }
            }

            return jsonify(simulation_response), 200

        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    @app.route('/api/simular-portabilidade', methods=['POST'])
    def simular_portabilidade():
        try:
            data = request.json
            simulation_response = {
                "success": True,
                "data": {
                    "proposal_id": f"PORT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "monthly_payment": round(float(data.get('current_installment', 0)) * 0.8, 2),
                    "annual_interest_rate": 12.75,
                    "total_amount": round(float(data.get('current_installment', 0)) * 0.8 * int(data.get('remaining_installments', 0)), 2),
                    "installments": data.get('remaining_installments', 0)
                }
            }
            return jsonify(simulation_response), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/solicitar-portabilidade-out', methods=['POST'])
    def solicitar_portabilidade_out():
        try:
            data = request.json
            response = {
                "success": True,
                "data": {
                    "protocol": f"POUT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "status": "Em análise"
                }
            }
            return jsonify(response), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route('/api/simular-refinanciamento', methods=['POST'])
    def simular_refinanciamento():
        try:
            data = request.json
            simulation_response = {
                "success": True,
                "data": {
                    "proposal_id": f"REF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "monthly_payment": round(float(data.get('current_installment', 0)) * 0.9, 2),
                    "annual_interest_rate": 14.75,
                    "total_amount": round(float(data.get('current_installment', 0)) * 0.9 * int(data.get('new_installments', 0)), 2),
                    "installments": data.get('new_installments', 0)
                }
            }
            return jsonify(simulation_response), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)