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
