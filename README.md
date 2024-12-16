<<<<<<< HEAD
# BMP Bank API Integration

This Flask application provides a REST API interface to interact with BMP Bank's APIs.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
   - Rename `.env.example` to `.env`
   - Add your BMP API key to the `.env` file

3. Run the application:
```bash
python app.py
```

## Available Endpoints

### Health Check
- GET `/health`
  - Check if the service is running

### Account Balance
- GET `/account/balance`
  - Retrieve account balance

### Transfer
- POST `/transfer`
  - Make a bank transfer
  - Required JSON body:
    ```json
    {
        "destination_account": "account_number",
        "amount": 100.00,
        "description": "Transfer description"
    }
    ```

### Statement
- GET `/statement`
  - Get account statement
  - Query parameters:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)

## Security
- API keys and sensitive information are stored in environment variables
- CORS is enabled for cross-origin requests
- All requests to BMP APIs are made with proper authentication
=======
# Banco INSS - AF360 Bank

Sistema de gerenciamento de empréstimos INSS integrado ao AF360 Bank.

## Funcionalidades

- Autenticação via token do sistema principal
- Criação e gestão de propostas de empréstimo INSS
- Interface moderna e responsiva
- Validação de dados em tempo real
- Integração com o sistema principal AF360 Bank

## Configuração

1. Clone o repositório:
```bash
git clone https://github.com/rafaavmsilva/banco-inss.af360bank.git
cd banco-inss.af360bank
```

2. Crie um ambiente virtual e instale as dependências:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com:
```
DATABASE_URL=sua_url_do_banco_de_dados
SECRET_KEY=sua_chave_secreta
```

4. Inicialize o banco de dados:
```bash
flask db init
flask db migrate
flask db upgrade
```

5. Execute o aplicativo:
```bash
flask run
```

## Tecnologias Utilizadas

- Flask
- SQLAlchemy
- PostgreSQL
- Bootstrap 5
- Font Awesome
- jQuery com Masks
- Gunicorn (produção)
>>>>>>> 962a945fa4dd789bd430a42a045294721c2935cb
