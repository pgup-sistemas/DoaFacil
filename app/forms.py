from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SelectField, FieldList, FormField, PasswordField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, Length
from wtforms.widgets import TextArea

class LoginAdminForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired(), Length(max=80)])
    password = PasswordField('Senha', validators=[DataRequired()])

class UnidadeForm(FlaskForm):
    nome = StringField('Nome da Unidade', validators=[DataRequired(), Length(max=100)])
    responsavel = StringField('Responsável', validators=[DataRequired(), Length(max=100)])
    email = StringField('E-mail', validators=[Optional(), Email(), Length(max=120)])
    descricao = TextAreaField('Descrição', validators=[Optional()])

class ItemForm(FlaskForm):
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

class DoacaoForm(FlaskForm):
    doador_nome = StringField('Seu Nome', validators=[DataRequired(), Length(max=100)])
    quantidade = IntegerField('Quantidade', validators=[DataRequired(), NumberRange(min=1)])
    observacao = TextAreaField('Observação (opcional)', validators=[Optional()])

class SugestaoItemForm(FlaskForm):
    nome = StringField('Nome do Item', validators=[DataRequired(), Length(max=100)])
    quantidade_necessaria = IntegerField('Quantidade Necessária', validators=[DataRequired(), NumberRange(min=1)])
    unidade_medida = StringField('Unidade de Medida', validators=[Optional(), Length(max=20)])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    sugestor_nome = StringField('Seu Nome', validators=[DataRequired(), Length(max=100)]) 