def validate_cpf(cpf):
    # Remove any non-digit characters
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Check if CPF has 11 digits
    if len(cpf) != 11:
        return False
    
    # Check if all digits are the same
    if len(set(cpf)) == 1:
        return False
    
    # Validate first digit
    sum = 0
    for i in range(9):
        sum += int(cpf[i]) * (10 - i)
    digit = (sum * 10) % 11
    if digit == 10:
        digit = 0
    if digit != int(cpf[9]):
        return False
    
    # Validate second digit
    sum = 0
    for i in range(10):
        sum += int(cpf[i]) * (11 - i)
    digit = (sum * 10) % 11
    if digit == 10:
        digit = 0
    if digit != int(cpf[10]):
        return False
    
    return True