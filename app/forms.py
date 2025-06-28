from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SelectField, FieldList, FormField, PasswordField, DecimalField, DateField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, Length, EqualTo, URL
from wtforms.widgets import TextArea

class LoginAdminForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Senha', validators=[DataRequired()])

class AdminForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(max=80)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=120)])
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Tipo de Administrador', choices=[
        ('admin_principal', 'Administrador Principal'),
        ('admin_unidade', 'Administrador de Unidade')
    ], validators=[DataRequired()])

class AdminEditForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(max=80)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=120)])
    nome = StringField('Nome Completo', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Nova Senha (deixe em branco para manter a atual)', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Nova Senha', validators=[Optional(), EqualTo('password')])
    role = SelectField('Tipo de Administrador', choices=[
        ('admin_principal', 'Administrador Principal'),
        ('admin_unidade', 'Administrador de Unidade')
    ], validators=[DataRequired()])
    ativo = BooleanField('Usuário Ativo')

class UnidadeForm(FlaskForm):
    # Informações Básicas
    nome = StringField('Nome da Organização*', validators=[DataRequired(), Length(max=100)])
    razao_social = StringField('Razão Social', validators=[Optional(), Length(max=200)])
    nome_fantasia = StringField('Nome Fantasia', validators=[Optional(), Length(max=100)])
    responsavel = StringField('Responsável*', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email Principal', validators=[Optional(), Email(), Length(max=120)])
    email_secundario = StringField('Email Secundário', validators=[Optional(), Email(), Length(max=120)])
    descricao = TextAreaField('Descrição da Organização', validators=[Optional()])
    
    # Dados Legais/Institucionais
    cnpj = StringField('CNPJ', validators=[Optional(), Length(max=18)])
    tipo_organizacao = SelectField('Tipo de Organização', choices=[
        ('', 'Selecione o tipo'),
        ('igreja', 'Igreja'),
        ('ong', 'ONG'),
        ('associacao', 'Associação'),
        ('empresa', 'Empresa'),
        ('escola', 'Escola/Instituição Educacional'),
        ('hospital', 'Hospital/Clínica'),
        ('orfanato', 'Orfanato'),
        ('asilo', 'Asilo'),
        ('outro', 'Outro')
    ], validators=[Optional()])
    data_fundacao = DateField('Data de Fundação', validators=[Optional()])
    registro_inscricao = StringField('Registro/Inscrição', validators=[Optional(), Length(max=50)])
    
    # Endereço Completo
    cep = StringField('CEP', validators=[Optional(), Length(max=9)])
    logradouro = StringField('Logradouro (Rua/Avenida)', validators=[Optional(), Length(max=200)])
    numero = StringField('Número', validators=[Optional(), Length(max=10)])
    complemento = StringField('Complemento', validators=[Optional(), Length(max=100)])
    bairro = StringField('Bairro', validators=[Optional(), Length(max=100)])
    cidade = StringField('Cidade', validators=[Optional(), Length(max=100)])
    estado = StringField('Estado', validators=[Optional(), Length(max=2)])
    
    # Contatos
    telefone_fixo = StringField('Telefone Fixo', validators=[Optional(), Length(max=20)])
    whatsapp_numero = StringField('WhatsApp', validators=[Optional(), Length(max=20)])
    horario_funcionamento = StringField('Horário de Funcionamento', validators=[Optional(), Length(max=100)])
    dias_funcionamento = StringField('Dias de Funcionamento', validators=[Optional(), Length(max=100)])
    
    # Presença Digital
    website_url = StringField('Website', validators=[Optional(), URL(), Length(max=200)])
    facebook_url = StringField('Facebook', validators=[Optional(), URL(), Length(max=200)])
    instagram_url = StringField('Instagram', validators=[Optional(), URL(), Length(max=200)])
    linkedin_url = StringField('LinkedIn', validators=[Optional(), URL(), Length(max=200)])
    youtube_url = StringField('YouTube', validators=[Optional(), URL(), Length(max=200)])
    
    # Dados para Relatórios
    categoria = SelectField('Categoria', choices=[
        ('', 'Selecione a categoria'),
        ('religiosa', 'Religiosa'),
        ('social', 'Social'),
        ('educacional', 'Educacional'),
        ('saude', 'Saúde'),
        ('ambiental', 'Ambiental'),
        ('cultural', 'Cultural'),
        ('esportiva', 'Esportiva'),
        ('outro', 'Outro')
    ], validators=[Optional()])
    publico_alvo = StringField('Público-Alvo', validators=[Optional(), Length(max=100)])
    area_atuacao = SelectField('Área de Atuação', choices=[
        ('', 'Selecione a área'),
        ('local', 'Local'),
        ('regional', 'Regional'),
        ('nacional', 'Nacional'),
        ('internacional', 'Internacional')
    ], validators=[Optional()])
    tamanho_organizacao = SelectField('Tamanho da Organização', choices=[
        ('', 'Selecione o tamanho'),
        ('pequena', 'Pequena (até 50 pessoas)'),
        ('media', 'Média (51-200 pessoas)'),
        ('grande', 'Grande (mais de 200 pessoas)')
    ], validators=[Optional()])

class ItemForm(FlaskForm):
    nome = StringField('Nome do Item', validators=[DataRequired(), Length(max=100)])
    quantidade_necessaria = IntegerField('Quantidade Necessária', validators=[DataRequired(), NumberRange(min=1)])
    unidade_medida = StringField('Unidade de Medida', validators=[Optional(), Length(max=20)])
    descricao = TextAreaField('Descrição', validators=[Optional()])

class ItemEditForm(FlaskForm):
    nome = StringField('Nome do Item', validators=[DataRequired(), Length(max=100)])
    quantidade_necessaria = IntegerField('Quantidade Necessária', validators=[DataRequired(), NumberRange(min=1)])
    unidade_medida = StringField('Unidade de Medida', validators=[Optional(), Length(max=20)])
    descricao = TextAreaField('Descrição', validators=[Optional()])

class ListaForm(FlaskForm):
    nome = StringField('Nome da Lista', validators=[DataRequired(), Length(max=100)])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    modo = SelectField('Modo da Lista', choices=[
        ('fechado', 'Fechado - Itens definidos pelo administrador'),
        ('aberto', 'Aberto - Doadores podem sugerir itens')
    ], validators=[DataRequired()])
    aceita_pix = BooleanField('Aceitar doações via PIX')
    chave_pix = StringField('Chave PIX', validators=[Optional(), Length(max=100)])
    solicitar_dados_pessoais = BooleanField('Solicitar dados pessoais do doador?')

class DoacaoForm(FlaskForm):
    identificador = StringField('CPF, e-mail ou telefone', validators=[DataRequired(), Length(max=50)])
    doador_nome = StringField('Seu Nome', validators=[Optional(), Length(max=100)])
    cpf = StringField('CPF', validators=[Optional(), Length(max=14)])
    cep = StringField('CEP', validators=[Optional(), Length(max=9)])
    contato = StringField('Contato (telefone ou e-mail)', validators=[Optional(), Length(max=50)])
    
    # Campos de endereço
    logradouro = StringField('Logradouro (Rua/Avenida)', validators=[Optional(), Length(max=200)])
    numero = StringField('Número', validators=[Optional(), Length(max=10)])
    complemento = StringField('Complemento', validators=[Optional(), Length(max=100)])
    bairro = StringField('Bairro', validators=[Optional(), Length(max=100)])
    cidade = StringField('Cidade', validators=[Optional(), Length(max=100)])
    estado = StringField('Estado', validators=[Optional(), Length(max=2)])
    
    # Tipo de doação
    tipo_doacao = SelectField('Tipo de Doação', choices=[
        ('', 'Selecione o tipo de doação'),
        ('item', 'Item Físico - Doar quantidade específica'),
        ('dinheiro', 'Doação Financeira - Valor em dinheiro')
    ], validators=[DataRequired()])
    
    # Campos para doação física
    quantidade = IntegerField('Quantidade de Itens', validators=[Optional(), NumberRange(min=1)])
    
    # Campos para doação financeira
    valor_dinheiro = DecimalField('Valor da Doação (R$)', validators=[Optional(), NumberRange(min=0.01)])
    
    observacao = TextAreaField('Observação (opcional)', validators=[Optional()])
    item_id = IntegerField('ID do Item', validators=[Optional()])

class SugestaoItemForm(FlaskForm):
    nome = StringField('Nome do Item', validators=[DataRequired(), Length(max=100)])
    quantidade_necessaria = IntegerField('Quantidade Necessária', validators=[DataRequired(), NumberRange(min=1)])
    unidade_medida = StringField('Unidade de Medida', validators=[Optional(), Length(max=20)])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    sugestor_nome = StringField('Seu Nome', validators=[DataRequired(), Length(max=100)]) 