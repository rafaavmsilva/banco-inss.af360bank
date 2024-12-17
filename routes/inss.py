from flask import Blueprint, render_template, request, jsonify
from datetime import datetime
from utils.validators import validate_cpf
from utils.calculations import calculate_credit_score, calculate_loan_limit, get_bcb_interest_rate

bp = Blueprint('inss', __name__, url_prefix='/inss')

@bp.route('/novo', methods=['GET'])
def novo():
    return render_template('inss/novo.html')

@bp.route('/portabilidade', methods=['GET'])
def portabilidade():
    return render_template('inss/portabilidade.html')

@bp.route('/portabilidade-out', methods=['GET'])
def portabilidade_out():
    return render_template('inss/portabilidade_out.html')

@bp.route('/refinanciamento', methods=['GET'])
def refinanciamento():
    return render_template('inss/refinanciamento.html')

@bp.route('/api/simular', methods=['POST', 'OPTIONS'])
def simular_inss():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
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

@bp.route('/api/simular-portabilidade', methods=['POST', 'OPTIONS'])
def simular_portabilidade():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
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

@bp.route('/api/solicitar-portabilidade-out', methods=['POST', 'OPTIONS'])
def solicitar_portabilidade_out():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
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

# Change this line in routes/inss.py
@bp.route('/api/simular-refinanciamento', methods=['POST', 'OPTIONS'])
def simular_refinanciamento():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
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