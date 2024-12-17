import random

def calculate_credit_score(cpf):
    # Simulate credit score calculation
    return random.randint(0, 1000)

def calculate_loan_limit(salary, credit_score):
    # Basic loan limit calculation
    base_limit = salary * 12
    credit_multiplier = credit_score / 1000
    return base_limit * credit_multiplier

def get_bcb_interest_rate():
    # Simulate getting BCB interest rate
    return 12.75  # Example fixed rate