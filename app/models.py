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
    role = db.Column(db.String(20), default='admin_unidade')  # 'admin_principal' ou 'admin_unidade'
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com unidades (para admin_unidade)
    unidades = db.relationship('UnidadeOrganizadora', backref='admin_responsavel', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin_principal(self):
        return self.role == 'admin_principal'
    
    def can_manage_unidade(self, unidade_id):
        """Verifica se o admin pode gerenciar uma unidade específica"""
        if self.is_admin_principal():
            return True
        return db.session.query(UnidadeOrganizadora).filter_by(
            id=unidade_id, admin_id=self.id
        ).first() is not None
    
    def can_manage_lista(self, lista):
        """Verifica se o admin pode gerenciar uma lista específica"""
        if self.is_admin_principal():
            return True
        return db.session.query(UnidadeOrganizadora).filter_by(
            id=lista.unidade_id, admin_id=self.id
        ).first() is not None
    
    def __repr__(self):
        return f'<Administrador {self.username}>'

class UnidadeOrganizadora(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Informações Básicas
    nome = db.Column(db.String(100), nullable=False)
    razao_social = db.Column(db.String(200))  # Nome legal da organização
    nome_fantasia = db.Column(db.String(100))  # Nome comercial
    responsavel = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    email_secundario = db.Column(db.String(120))
    descricao = db.Column(db.Text)
    
    # Dados Legais/Institucionais
    cnpj = db.Column(db.String(18))  # XX.XXX.XXX/XXXX-XX
    tipo_organizacao = db.Column(db.String(50))  # Igreja, ONG, Associação, Empresa, etc.
    data_fundacao = db.Column(db.Date)
    registro_inscricao = db.Column(db.String(50))  # Registro específico da categoria
    
    # Endereço Completo
    cep = db.Column(db.String(9))
    logradouro = db.Column(db.String(200))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    coordenadas_lat = db.Column(db.Float)  # Latitude para mapa
    coordenadas_lng = db.Column(db.Float)  # Longitude para mapa
    
    # Contatos
    telefone_fixo = db.Column(db.String(20))
    whatsapp_numero = db.Column(db.String(20))  # Já existia
    horario_funcionamento = db.Column(db.String(100))  # "Segunda a Sexta, 8h às 18h"
    dias_funcionamento = db.Column(db.String(100))  # "Segunda a Sexta"
    
    # Presença Digital
    website_url = db.Column(db.String(200))  # Já existia
    facebook_url = db.Column(db.String(200))  # Já existia
    instagram_url = db.Column(db.String(200))  # Já existia
    linkedin_url = db.Column(db.String(200))
    youtube_url = db.Column(db.String(200))
    
    # Dados para Relatórios
    categoria = db.Column(db.String(50))  # Religiosa, Social, Educacional, etc.
    publico_alvo = db.Column(db.String(100))  # Crianças, Idosos, Famílias, etc.
    area_atuacao = db.Column(db.String(50))  # Local, Regional, Nacional
    tamanho_organizacao = db.Column(db.String(20))  # Pequena, Média, Grande
    
    # Metadados
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamento com admin responsável
    admin_id = db.Column(db.Integer, db.ForeignKey('administrador.id'))
    
    # Relacionamentos
    listas = db.relationship('Lista', backref='unidade', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<UnidadeOrganizadora {self.nome}>'
    
    @property
    def endereco_completo(self):
        """Retorna o endereço formatado completo"""
        partes = []
        if self.logradouro:
            partes.append(self.logradouro)
        if self.numero:
            partes.append(self.numero)
        if self.complemento:
            partes.append(self.complemento)
        if self.bairro:
            partes.append(self.bairro)
        if self.cidade:
            partes.append(self.cidade)
        if self.estado:
            partes.append(self.estado)
        if self.cep:
            partes.append(self.cep)
        
        return ', '.join(partes) if partes else 'Endereço não informado'
    
    @property
    def cnpj_formatado(self):
        """Retorna CNPJ formatado"""
        if not self.cnpj:
            return None
        cnpj_limpo = ''.join(filter(str.isdigit, self.cnpj))
        if len(cnpj_limpo) == 14:
            return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
        return self.cnpj

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
    concluida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_conclusao = db.Column(db.DateTime)
    cancelada = db.Column(db.Boolean, default=False)
    motivo_cancelamento = db.Column(db.Text)
    unidade_id = db.Column(db.Integer, db.ForeignKey('unidade_organizadora.id'), nullable=False)
    solicitar_dados_pessoais = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    itens = db.relationship('Item', backref='lista', lazy=True, cascade='all, delete-orphan')
    sugestoes = db.relationship('SugestaoItem', backref='lista', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Lista {self.nome}>'
    
    @property
    def total_itens(self):
        return db.session.query(db.func.sum(Item.quantidade_necessaria)).filter_by(lista_id=self.id).scalar() or 0
    
    @property
    def total_arrecadado(self):
        return db.session.query(db.func.sum(Doacao.quantidade)).join(Item).filter(Item.lista_id == self.id).scalar() or 0
    
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
    def valor_financeiro_arrecadado(self):
        """Valor total em dinheiro arrecadado para este item"""
        valor = db.session.query(db.func.sum(Doacao.valor_dinheiro)).filter_by(
            item_id=self.id, tipo_doacao='dinheiro'
        ).scalar() or 0
        
        # Converter Decimal para float para compatibilidade
        return float(valor) if valor else 0.0
    
    @property
    def quantidade_arrecadada(self):
        # Doações físicas (quantidade de itens)
        doacoes_fisicas = db.session.query(db.func.sum(Doacao.quantidade)).filter_by(
            item_id=self.id, tipo_doacao='item'
        ).scalar() or 0
        
        # Doações financeiras (convertidas para quantidade baseada no valor)
        # Assumindo um valor médio por item para conversão
        doacoes_financeiras = db.session.query(db.func.sum(Doacao.valor_dinheiro)).filter_by(
            item_id=self.id, tipo_doacao='dinheiro'
        ).scalar() or 0
        
        # Converter valor financeiro para quantidade (exemplo: R$ 50 = 1 item)
        # Você pode ajustar essa lógica conforme necessário
        valor_por_item = 50.0  # R$ 50 por item (ajuste conforme necessário)
        
        # Converter Decimal para float para a divisão
        if doacoes_financeiras:
            doacoes_financeiras_float = float(doacoes_financeiras)
            quantidade_financeira = int(doacoes_financeiras_float / valor_por_item) if valor_por_item > 0 else 0
        else:
            quantidade_financeira = 0
        
        return doacoes_fisicas + quantidade_financeira
    
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

class Doador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True)
    cep = db.Column(db.String(9))
    contato = db.Column(db.String(50))  # telefone ou e-mail
    
    # Campos de endereço
    logradouro = db.Column(db.String(200))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento com doações
    doacoes = db.relationship('Doacao', backref='doador', lazy=True)

    def __repr__(self):
        return f'<Doador {self.nome} - {self.cpf or self.contato}>'

class Doacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doador_id = db.Column(db.Integer, db.ForeignKey('doador.id'))  # NOVO: referência ao doador
    doador_nome = db.Column(db.String(100), nullable=True)  # Agora opcional
    cpf = db.Column(db.String(14))  # Agora opcional
    cep = db.Column(db.String(9))   # Agora opcional
    contato = db.Column(db.String(50))  # Agora opcional
    
    # Tipo de doação
    tipo_doacao = db.Column(db.String(20), default='item')  # 'item' ou 'dinheiro'
    
    # Campos para doação física
    quantidade = db.Column(db.Integer, nullable=True)  # Quantidade de itens
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=True)  # Item específico (pode ser null para doação financeira)
    
    # Campos para doação financeira
    valor_dinheiro = db.Column(db.Numeric(10, 2), nullable=True)  # Valor em reais
    
    observacao = db.Column(db.Text)
    data_doacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        if self.tipo_doacao == 'item':
            return f'<Doacao {self.doador_nome} - {self.quantidade} itens>'
        else:
            return f'<Doacao {self.doador_nome} - R$ {self.valor_dinheiro}>'

class SugestaoItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    quantidade_necessaria = db.Column(db.Integer, nullable=False)
    unidade_medida = db.Column(db.String(20), default='unidades')
    descricao = db.Column(db.Text)
    sugestor_nome = db.Column(db.String(100), nullable=False)
    data_sugestao = db.Column(db.DateTime, default=datetime.utcnow)
    aprovada = db.Column(db.Boolean, default=False)
    lista_id = db.Column(db.Integer, db.ForeignKey('lista.id'), nullable=False)
    
    def __repr__(self):
        return f'<SugestaoItem {self.nome} - {self.sugestor_nome}>' 