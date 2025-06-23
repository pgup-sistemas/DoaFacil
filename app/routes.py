from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_wtf.csrf import generate_csrf
from app import db
from app.models import UnidadeOrganizadora, Lista, Item, Doacao, Administrador
from app.forms import UnidadeForm, ListaForm, ItemForm, DoacaoForm, SugestaoItemForm, LoginAdminForm
from app.utils import export_lista_csv, export_lista_pdf, send_notification_email, get_progress_color
from functools import wraps
import io

main = Blueprint('main', __name__)

def admin_required(f):
    """Decorator para verificar se o usuário está logado como administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Acesso restrito a administradores.', 'error')
            return redirect(url_for('main.login_admin'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
def index():
    """Página inicial - criar nova unidade ou lista"""
    return render_template('index.html')

@main.route('/admin/login', methods=['GET', 'POST'])
def login_admin():
    """Login de administrador"""
    form = LoginAdminForm()
    
    if form.validate_on_submit():
        print(f"DEBUG: Tentativa de login - Usuário: {form.username.data}")
        
        admin = Administrador.query.filter_by(username=form.username.data, ativo=True).first()
        
        if admin:
            print(f"DEBUG: Administrador encontrado - {admin.nome}")
            if admin.check_password(form.password.data):
                print(f"DEBUG: Senha correta - Login bem-sucedido")
                session['admin_id'] = admin.id
                session['admin_nome'] = admin.nome
                flash(f'Bem-vindo, {admin.nome}!', 'success')
                return redirect(url_for('main.admin_dashboard'))
            else:
                print(f"DEBUG: Senha incorreta")
                flash('Usuário ou senha inválidos.', 'error')
        else:
            print(f"DEBUG: Administrador não encontrado ou inativo")
            flash('Usuário ou senha inválidos.', 'error')
    else:
        if form.errors:
            print(f"DEBUG: Erros de validação: {form.errors}")
    
    return render_template('admin/login.html', form=form)

@main.route('/admin/logout')
def logout_admin():
    """Logout de administrador"""
    session.pop('admin_id', None)
    session.pop('admin_nome', None)
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('main.index'))

@main.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Dashboard principal do administrador"""
    unidades = UnidadeOrganizadora.query.all()
    return render_template('admin/dashboard.html', unidades=unidades)

@main.route('/unidade/cadastrar', methods=['GET', 'POST'])
@admin_required
def cadastrar_unidade():
    """Cadastro de nova unidade organizadora - RESTRITO A ADMIN"""
    form = UnidadeForm()
    
    if form.validate_on_submit():
        unidade = UnidadeOrganizadora(
            nome=form.nome.data,
            responsavel=form.responsavel.data,
            email=form.email.data,
            descricao=form.descricao.data
        )
        db.session.add(unidade)
        db.session.commit()
        
        flash('Unidade cadastrada com sucesso!', 'success')
        return redirect(url_for('main.admin_dashboard'))
    
    return render_template('cadastrar_unidade.html', form=form)

@main.route('/lista/criar/<int:unidade_id>', methods=['GET', 'POST'])
@admin_required
def criar_lista(unidade_id):
    """Criação de lista associada a uma unidade - RESTRITO A ADMIN"""
    unidade = UnidadeOrganizadora.query.get_or_404(unidade_id)
    form = ListaForm()
    
    if form.validate_on_submit():
        lista = Lista(
            nome=form.nome.data,
            descricao=form.descricao.data,
            modo=form.modo.data,
            aceita_pix=form.aceita_pix.data,
            chave_pix=form.chave_pix.data if form.aceita_pix.data else None,
            unidade_id=unidade.id
        )
        db.session.add(lista)
        db.session.commit()
        
        flash('Lista criada com sucesso!', 'success')
        return redirect(url_for('main.adicionar_itens', lista_id=lista.id))
    
    return render_template('criar_lista.html', form=form, unidade=unidade)

@main.route('/lista/<int:lista_id>/itens', methods=['GET', 'POST'])
@admin_required
def adicionar_itens(lista_id):
    """Adicionar itens à lista - RESTRITO A ADMIN"""
    lista = Lista.query.get_or_404(lista_id)
    form = ItemForm()
    
    if form.validate_on_submit():
        item = Item(
            nome=form.nome.data,
            quantidade_necessaria=form.quantidade_necessaria.data,
            unidade_medida=form.unidade_medida.data or 'unidades',
            descricao=form.descricao.data,
            lista_id=lista.id
        )
        db.session.add(item)
        db.session.commit()
        
        flash('Item adicionado com sucesso!', 'success')
        return redirect(url_for('main.adicionar_itens', lista_id=lista.id))
    
    return render_template('adicionar_itens.html', form=form, lista=lista)

@main.route('/lista/<slug>')
def visualizar_lista(slug):
    """Página pública da lista - ACESSO PÚBLICO"""
    lista = Lista.query.filter_by(slug=slug, ativa=True).first_or_404()
    form = DoacaoForm()
    
    return render_template('visualizar_lista.html', lista=lista, form=form)

@main.route('/lista/<slug>/doar', methods=['POST'])
def doar(slug):
    """Processar doação - ACESSO PÚBLICO"""
    lista = Lista.query.filter_by(slug=slug, ativa=True).first_or_404()
    form = DoacaoForm()
    
    if form.validate_on_submit():
        item_id = request.form.get('item_id')
        item = Item.query.get_or_404(item_id)
        
        # Verificar se a quantidade não excede o necessário
        if item.quantidade_restante < form.quantidade.data:
            flash('Quantidade solicitada excede o necessário para este item.', 'error')
            return redirect(url_for('main.visualizar_lista', slug=slug))
        
        doacao = Doacao(
            doador_nome=form.doador_nome.data,
            quantidade=form.quantidade.data,
            observacao=form.observacao.data,
            item_id=item.id
        )
        db.session.add(doacao)
        db.session.commit()
        
        # Enviar notificação por e-mail
        send_notification_email(lista, doacao)
        
        flash('Doação registrada com sucesso! Obrigado pela sua contribuição.', 'success')
        return redirect(url_for('main.visualizar_lista', slug=slug))
    
    return redirect(url_for('main.visualizar_lista', slug=slug))

@main.route('/admin/<token>')
def dashboard(token):
    """Dashboard administrativo da lista - ACESSO VIA TOKEN"""
    lista = Lista.query.filter_by(token_admin=token).first_or_404()
    
    return render_template('dashboard.html', lista=lista)

@main.route('/admin/<token>/editar', methods=['GET', 'POST'])
def editar_lista(token):
    """Editar lista (apenas itens não doados) - ACESSO VIA TOKEN"""
    lista = Lista.query.filter_by(token_admin=token).first_or_404()
    form = ListaForm(obj=lista)
    
    if form.validate_on_submit():
        lista.nome = form.nome.data
        lista.descricao = form.descricao.data
        lista.aceita_pix = form.aceita_pix.data
        lista.chave_pix = form.chave_pix.data if form.aceita_pix.data else None
        
        db.session.commit()
        flash('Lista atualizada com sucesso!', 'success')
        return redirect(url_for('main.dashboard', token=token))
    
    return render_template('editar_lista.html', form=form, lista=lista)

@main.route('/admin/<token>/adicionar-itens', methods=['GET', 'POST'])
def adicionar_itens_lista(token):
    """Adicionar itens a uma lista existente - ACESSO VIA TOKEN"""
    lista = Lista.query.filter_by(token_admin=token).first_or_404()
    form = ItemForm()
    
    if form.validate_on_submit():
        item = Item(
            nome=form.nome.data,
            quantidade_necessaria=form.quantidade_necessaria.data,
            unidade_medida=form.unidade_medida.data or 'unidades',
            descricao=form.descricao.data,
            lista_id=lista.id
        )
        db.session.add(item)
        db.session.commit()
        
        flash('Item adicionado com sucesso!', 'success')
        return redirect(url_for('main.adicionar_itens_lista', token=token))
    
    return render_template('adicionar_itens_lista.html', form=form, lista=lista)

@main.route('/exportar/<slug>.csv')
def exportar_csv(slug):
    """Exportar lista em CSV - ACESSO PÚBLICO"""
    lista = Lista.query.filter_by(slug=slug).first_or_404()
    csv_content = export_lista_csv(lista)
    
    output = io.BytesIO()
    output.write(csv_content.encode('utf-8'))
    output.seek(0)
    
    return send_file(
        output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'lista_{lista.slug}.csv'
    )

@main.route('/exportar/<slug>.pdf')
def exportar_pdf(slug):
    """Exportar lista em PDF - ACESSO PÚBLICO"""
    lista = Lista.query.filter_by(slug=slug).first_or_404()
    pdf_content = export_lista_pdf(lista)
    
    output = io.BytesIO()
    output.write(pdf_content)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'lista_{lista.slug}.pdf'
    )

@main.route('/api/lista/<slug>/status')
def api_lista_status(slug):
    """API para status da lista - ACESSO PÚBLICO"""
    lista = Lista.query.filter_by(slug=slug, ativa=True).first_or_404()
    
    return jsonify({
        'nome': lista.nome,
        'descricao': lista.descricao,
        'percentual_geral': lista.percentual_conclusao,
        'total_itens': lista.total_itens,
        'total_arrecadado': lista.total_arrecadado,
        'itens': [{
            'nome': item.nome,
            'quantidade_necessaria': item.quantidade_necessaria,
            'quantidade_arrecadada': item.quantidade_arrecadada,
            'quantidade_restante': item.quantidade_restante,
            'percentual': item.percentual_conclusao,
            'unidade_medida': item.unidade_medida
        } for item in lista.itens]
    })

@main.route('/api/lista/<slug>/doar', methods=['POST'])
def api_doar(slug):
    """API para doação - ACESSO PÚBLICO"""
    lista = Lista.query.filter_by(slug=slug, ativa=True).first_or_404()
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    item_id = data.get('item_id')
    doador_nome = data.get('doador_nome')
    quantidade = data.get('quantidade')
    
    if not all([item_id, doador_nome, quantidade]):
        return jsonify({'error': 'Dados incompletos'}), 400
    
    item = Item.query.get_or_404(item_id)
    
    if item.quantidade_restante < quantidade:
        return jsonify({'error': 'Quantidade excede o necessário'}), 400
    
    doacao = Doacao(
        doador_nome=doador_nome,
        quantidade=quantidade,
        item_id=item.id
    )
    db.session.add(doacao)
    db.session.commit()
    
    send_notification_email(lista, doacao)
    
    return jsonify({
        'success': True,
        'message': 'Doação registrada com sucesso',
        'item_atualizado': {
            'quantidade_arrecadada': item.quantidade_arrecadada,
            'quantidade_restante': item.quantidade_restante,
            'percentual': item.percentual_conclusao
        }
    }) 