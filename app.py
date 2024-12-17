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

    # Helper Functions
    def validate_cpf(cpf):
        cpf = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf) != 11:
            return False
            
        # CPF validation algorithm
        numbers = [int(digit) for digit in cpf]
        
        # Validate first digit
        sum_of_products = sum(a*b for a, b in zip(numbers[0:9], range(10, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if numbers[9] != expected_digit:
            return False
            
        # Validate second digit
        sum_of_products = sum(a*b for a, b in zip(numbers[0:10], range(11, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if numbers[10] != expected_digit:
            return False
            
        return True

    def get_bcb_interest_rate():
        # Using BCB API to get SELIC rate
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/1?formato=json"
        try:
            response = requests.get(url)
            data = response.json()
            return float(data[0]['valor'])
        except:
            return 12.75  # Default fallback rate

    def calculate_credit_score(cpf):
        # Simulated credit score calculation
        # In a real scenario, you would integrate with a credit score API
        cpf_sum = sum(int(digit) for digit in str(cpf) if digit.isdigit())
        base_score = (cpf_sum * 7) % 300 + 300  # Generate score between 300 and 600
        return base_score

    def calculate_loan_limit(salary, score):
        # Basic loan limit calculation based on salary and credit score
        base_limit = salary * 12
        score_multiplier = score / 600  # Score influence
        return min(base_limit * score_multiplier, salary * 20)  # Max 20x salary

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"}), 200

    @app.route('/inss/novo', methods=['POST'])
    def inss_novo():
        try:
            data = request.json

            # Validate required fields
            required_fields = ['cpf', 'salary', 'loan_amount', 'installments']
            if not all(field in data for field in required_fields):
                return jsonify({
                    "error": "Missing required fields",
                    "required_fields": required_fields
                }), 400

            # CPF validation
            if not validate_cpf(data['cpf']):
                return jsonify({"error": "Invalid CPF"}), 400

            # Basic data validation
            if data['salary'] <= 0 or data['loan_amount'] <= 0 or data['installments'] <= 0:
                return jsonify({"error": "Invalid values for salary, loan amount, or installments"}), 400

            # Get credit score
            credit_score = calculate_credit_score(data['cpf'])

            # Calculate loan limit
            loan_limit = calculate_loan_limit(data['salary'], credit_score)

            if data['loan_amount'] > loan_limit:
                return jsonify({
                    "error": "Loan amount exceeds available limit",
                    "available_limit": loan_limit
                }), 400

            # Get current interest rate
            base_rate = get_bcb_interest_rate()
            
            # Calculate monthly interest rate (base_rate + spread)
            monthly_rate = (base_rate + 2) / 12 / 100  # Adding 2% spread

            # Calculate monthly payment
            monthly_payment = (data['loan_amount'] * monthly_rate * (1 + monthly_rate)**data['installments']) / ((1 + monthly_rate)**data['installments'] - 1)

            # Create loan proposal
            loan_proposal = {
                "proposal_id": f"PROP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "approved",
                "loan_details": {
                    "amount": data['loan_amount'],
                    "installments": data['installments'],
                    "monthly_payment": round(monthly_payment, 2),
                    "annual_interest_rate": round(base_rate + 2, 2),
                    "total_amount": round(monthly_payment * data['installments'], 2)
                },
                "customer_info": {
                    "cpf": data['cpf'],
                    "credit_score": credit_score,
                    "salary": data['salary']
                }
            }

            return jsonify(loan_proposal), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/inss/consulta/<proposal_id>', methods=['GET'])
    def inss_consulta(proposal_id):
        # Simplified proposal status check
        if not proposal_id.startswith('PROP-'):
            return jsonify({"error": "Invalid proposal ID format"}), 400

        # In a real scenario, this would check a database
        # Here we're just returning a mock response
        mock_response = {
            "proposal_id": proposal_id,
            "status": "processing",
            "last_update": datetime.now().isoformat(),
            "message": "Proposal is being processed"
        }

        return jsonify(mock_response), 200

    # In app.py, modify the route from '/inss/novo' to '/api/simular-inss'

@app.route('/api/simular-inss', methods=['POST'])
def simular_inss():
    try:
        data = request.json

        # Validate required fields
        required_fields = ['cpf', 'salary', 'loan_amount', 'installments']
        if not all(field in data for field in required_fields):
            return jsonify({
                "error": "Missing required fields",
                "required_fields": required_fields
            }), 400

        # Extract data from the frontend format
        cpf = data.get('cpf', '').replace('.', '').replace('-', '')
        salary = float(data.get('salary', 0))
        loan_amount = float(data.get('loan_amount', 0))
        installments = int(data.get('installments', 0))

        # CPF validation
        if not validate_cpf(cpf):
            return jsonify({"error": "CPF inválido"}), 400

        # Basic data validation
        if salary <= 0 or loan_amount <= 0 or installments <= 0:
            return jsonify({"error": "Valores inválidos para salário, valor do empréstimo ou parcelas"}), 400

        # Get credit score
        credit_score = calculate_credit_score(cpf)

        # Calculate loan limit
        loan_limit = calculate_loan_limit(salary, credit_score)

        if loan_amount > loan_limit:
            return jsonify({
                "error": "Valor do empréstimo excede o limite disponível",
                "available_limit": loan_limit
            }), 400

        # Get current interest rate
        base_rate = get_bcb_interest_rate()
        
        # Calculate monthly interest rate (base_rate + spread)
        monthly_rate = (base_rate + 2) / 12 / 100

        # Calculate monthly payment
        monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate)**installments) / ((1 + monthly_rate)**installments - 1)

        # Create simulation response
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

    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)