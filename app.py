from flask import Flask, request, jsonify, render_template, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Flask configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://') if os.getenv('DATABASE_URL') else 'postgresql://af360bank_db_user:jAO3e85X5e7cuDzIYpCpuGyo5VeVcRPy@dpg-ctcr4taj1k6c73flmt1g-a/af360bank_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

def init_db():
    with app.app_context():
        try:
            # Get database connection
            conn = db.engine.connect()
            
            # Drop the users table if it exists and recreate it with the correct structure
            conn.execute(db.text("""
                DROP TABLE IF EXISTS users CASCADE;
                
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(120) NOT NULL UNIQUE,
                    phone VARCHAR(20),
                    role VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'active'
                );
            """))
            
            db.session.commit()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
            db.session.rollback()

# Initialize database tables
init_db()

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')

# BMP API Configuration
BMP_API_BASE_URL = "https://api.bmpbanco.com.br"  # Replace with actual BMP API base URL
API_KEY = os.getenv("BMP_API_KEY")

@app.route("/", methods=["GET"])
def index():
    return render_template('dashboard.html')

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "message": "BMP API Integration Service is running"})

@app.route("/account/balance", methods=["GET"])
def get_account_balance():
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BMP_API_BASE_URL}/account/balance",
            headers=headers
        )
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/transfer", methods=["POST"])
def make_transfer():
    try:
        transfer_data = request.json
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{BMP_API_BASE_URL}/transfer",
            headers=headers,
            json=transfer_data
        )
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/statement", methods=["GET"])
def get_statement():
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        params = {
            "start_date": start_date,
            "end_date": end_date
        }
        
        response = requests.get(
            f"{BMP_API_BASE_URL}/statement",
            headers=headers,
            params=params
        )
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route("/pagamento-comissoes")
def comissoes():
    return render_template('comissoes.html')

@app.route("/fgts")
def fgts():
    return render_template('fgts.html')

@app.route("/api/fgts/simular", methods=["POST"])
def simular_fgts():
    if not request.is_json:
        return jsonify({"error": "Content-Type deve ser application/json"}), 400
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Dados JSON inválidos"}), 400
        
    cpf = data.get('cpf')
    if not cpf:
        return jsonify({"error": "CPF é obrigatório"}), 400

    # Aqui você implementaria a chamada real à API do banco
    # Por enquanto, retornamos dados simulados
    simulacao = {
        'saldo_total': 15000.00,
        'parcelas_disponiveis': 12,
        'valor_parcela': 1250.00
    }
    
    return jsonify(simulacao)

@app.route("/credito-pessoal")
def credito_pessoal():
    return render_template('credito_pessoal.html')

@app.route("/capital-giro")
def capital_giro():
    return render_template('capital_giro.html')

@app.route("/usuarios")
def usuarios():
    try:
        users = User.query.all()
        print("Users retrieved successfully:", [{"id": user.id, "name": user.name, "email": user.email} for user in users])
        return render_template('usuarios.html', users=users)
    except Exception as e:
        print("Error in usuarios route:", str(e))
        return render_template('usuarios.html', users=[], error="Error loading users")

@app.route("/criar-usuario", methods=["POST"])
def criar_usuario():
    try:
        data = request.json
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            flash('User with this email already exists', 'error')
            return jsonify({"error": "User already exists"}), 400
            
        new_user = User(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone', ''),
            role=data.get('role', 'user'),
            status='active'
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('User created successfully!', 'success')
        return jsonify({"message": "User created successfully"}), 201
        
    except Exception as e:
        db.session.rollback()
        flash('Error creating user', 'error')
        return jsonify({"error": str(e)}), 500

@app.route("/esteira-propostas")
def esteira_propostas():
    return render_template('esteira-propostas.html')

@app.route("/perfis")
def perfis():
    # Get query parameters for filtering
    nome = request.args.get('nome')
    status = request.args.get('status')
    
    # Sample data structure (replace with database)
    perfis_list = [
        {
            'nome': 'Administrador',
            'descricao': 'Acesso total ao sistema',
            'permissoes': ['dashboard', 'usuarios', 'perfis', 'parceiros', 'tabelas'],
            'status': 'Ativo'
        },
        {
            'nome': 'Operador',
            'descricao': 'Acesso às operações básicas',
            'permissoes': ['dashboard', 'usuarios'],
            'status': 'Ativo'
        }
    ]
    
    # Apply filters
    if nome:
        perfis_list = [p for p in perfis_list if nome.lower() in p['nome'].lower()]
    if status:
        perfis_list = [p for p in perfis_list if status.lower() == p['status'].lower()]
    
    return render_template('perfis.html', perfis=perfis_list)

@app.route("/api/perfis", methods=["POST"])
def criar_perfil():
    try:
        if not request.is_json:
            return jsonify({"error": "O conteúdo deve ser JSON"}), 400
            
        data = request.json
        if data is None:
            return jsonify({"error": "Dados inválidos"}), 400
            
        nome = data.get('nome')
        descricao = data.get('descricao')
        permissoes = data.get('permissoes', [])
        
        if not nome or not descricao:
            return jsonify({"error": "Nome e descrição são obrigatórios"}), 400
            
        # Aqui você implementaria a lógica para salvar no banco de dados
        novo_perfil = {
            'nome': nome,
            'descricao': descricao,
            'permissoes': permissoes,
            'status': 'Ativo'
        }
        
        return jsonify({"message": "Perfil criado com sucesso", "perfil": novo_perfil}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/perfis/<nome>", methods=["GET"])
def obter_perfil(nome):
    try:
        # Aqui você implementaria a busca no banco de dados
        perfil = {
            'nome': nome,
            'descricao': 'Descrição do perfil',
            'permissoes': ['dashboard', 'usuarios'],
            'status': 'Ativo'
        }
        
        if not perfil:
            return jsonify({"error": "Perfil não encontrado"}), 404
            
        return jsonify(perfil), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/perfis/<nome>", methods=["PUT"])
def atualizar_perfil(nome):
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Dados inválidos. Certifique-se de enviar um JSON válido"}), 400
        
        # Aqui você implementaria a atualização no banco de dados
        perfil_atualizado = {
            'nome': nome,
            'descricao': data.get('descricao'),
            'permissoes': data.get('permissoes', []),
            'status': data.get('status')
        }
        
        return jsonify({"message": "Perfil atualizado com sucesso", "perfil": perfil_atualizado}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/perfis/<nome>", methods=["DELETE"])
def excluir_perfil(nome):
    try:
        # Aqui você implementaria a exclusão no banco de dados
        return jsonify({"message": f"Perfil {nome} excluído com sucesso"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/parceiros")
def parceiros():
    return render_template("parceiros.html")

@app.route("/parceiros/<codigo>")
def obter_parceiro(codigo):
    # Simular dados do parceiro
    parceiro = {
        "codigo": codigo,
        "nome": "HIPER LOJÃO DO REAL",
        "documento": "16.829.975/0001-67",
        "telefone": "(17) 99135-1540",
        "email": "maristelabaraldo@hotmail.com",
        "tipo_pessoa": "Pessoa Jurídica",
        "is_varejista": False,
        "banco": "ITAU UNIBANCO S.A.",
        "tipo_conta": "Conta Corrente",
        "agencia": "7136",
        "digito_agencia": "0",
        "conta": "25050",
        "digito_conta": "8",
        "ativo": True
    }
    return jsonify(parceiro)

@app.route("/parceiros/salvar", methods=["POST"])
def salvar_parceiro():
    dados = request.json
    # Aqui você implementaria a lógica para salvar no banco de dados
    return jsonify({"success": True, "message": "Parceiro salvo com sucesso"})

@app.route("/parceiros/<codigo>/status", methods=["POST"])
def alterar_status_parceiro(codigo):
    # Aqui você implementaria a lógica para alterar o status no banco de dados
    return jsonify({"success": True, "message": "Status alterado com sucesso"})

@app.route("/tabelas")
def tabelas():
    return render_template("tabelas.html")

@app.route("/tabelas/<identificador>")
def obter_tabela(identificador):
    # Simular dados da tabela
    tabela = {
        "identificador": identificador,
        "nome": "VIA INVEST 1 - 75 A 250",
        "regra_tc": "De R$ 75,00 até R$ 250,00 = 26%",
        "antifraude": "TRUSTIC",
        "banco": "BMP",
        "orgao": "FGTS",
        "fundo": "Via Invest",
        "taxa_mensal": "1.79",
        "ativo": True
    }
    return jsonify(tabela)

@app.route("/tabelas/salvar", methods=["POST"])
def salvar_tabela():
    dados = request.json
    # Aqui você implementaria a lógica para salvar no banco de dados
    return jsonify({"success": True, "message": "Tabela salva com sucesso"})

@app.route("/tabelas/<identificador>/status", methods=["POST"])
def alterar_status_tabela(identificador):
    # Aqui você implementaria a lógica para alterar o status no banco de dados
    return jsonify({"success": True, "message": "Status alterado com sucesso"})

@app.cli.command("init-db")
def init_db_command():
    """Initialize the database."""
    db.create_all()
    print("Initialized the database.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
