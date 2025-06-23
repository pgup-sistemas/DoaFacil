from datetime import datetime
from app import db
import secrets
import string
from werkzeug.security import generate_password_hash, check_password_hash

def generate_slug():
    """Gera um slug único para as listas"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

def generate_token():
    """Gera um token único para acesso administrativo"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))

class Administrador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Administrador {self.username}>'

class UnidadeOrganizadora(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    responsavel = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    descricao = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    listas = db.relationship('Lista', backref='unidade', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<UnidadeOrganizadora {self.nome}>'

class Lista(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    modo = db.Column(db.String(20), default='fechado')  # 'aberto' ou 'fechado'
    aceita_pix = db.Column(db.Boolean, default=False)
    chave_pix = db.Column(db.String(100))
    slug = db.Column(db.String(8), unique=True, default=generate_slug)
    token_admin = db.Column(db.String(16), unique=True, default=generate_token)
    ativa = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidade_organizadora.id'), nullable=False)
    
    # Relacionamentos
    itens = db.relationship('Item', backref='lista', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Lista {self.nome}>'
    
    @property
    def total_itens(self):
        return sum(item.quantidade_necessaria for item in self.itens)
    
    @property
    def total_arrecadado(self):
        return sum(item.quantidade_arrecadada for item in self.itens)
    
    @property
    def percentual_conclusao(self):
        if self.total_itens == 0:
            return 0
        return (self.total_arrecadado / self.total_itens) * 100

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    quantidade_necessaria = db.Column(db.Integer, nullable=False)
    unidade_medida = db.Column(db.String(20), default='unidades')
    descricao = db.Column(db.Text)
    lista_id = db.Column(db.Integer, db.ForeignKey('lista.id'), nullable=False)
    
    # Relacionamentos
    doacoes = db.relationship('Doacao', backref='item', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Item {self.nome}>'
    
    @property
    def quantidade_arrecadada(self):
        return sum(doacao.quantidade for doacao in self.doacoes)
    
    @property
    def quantidade_restante(self):
        return max(0, self.quantidade_necessaria - self.quantidade_arrecadada)
    
    @property
    def percentual_conclusao(self):
        if self.quantidade_necessaria == 0:
            return 0
        return min(100, (self.quantidade_arrecadada / self.quantidade_necessaria) * 100)
    
    @property
    def esta_completo(self):
        return self.quantidade_arrecadada >= self.quantidade_necessaria

class Doacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doador_nome = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    observacao = db.Column(db.Text)
    data_doacao = db.Column(db.DateTime, default=datetime.utcnow)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    
    def __repr__(self):
        return f'<Doacao {self.doador_nome} - {self.quantidade}>' 