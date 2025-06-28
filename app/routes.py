from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, session
from flask_wtf.csrf import generate_csrf
from app import db
from app.models import UnidadeOrganizadora, Lista, Item, Doacao, Administrador, SugestaoItem, Doador
from app.forms import UnidadeForm, ListaForm, ItemForm, DoacaoForm, SugestaoItemForm, LoginAdminForm, AdminForm, AdminEditForm, ItemEditForm
from app.utils import (
    export_lista_csv, export_lista_pdf, export_lista_excel, 
    send_notification_email, generate_whatsapp_share_url_with_unidade,
    generate_facebook_share_url_with_unidade, get_unidade_social_links,
    consultar_cep, formatar_cep, validar_cep, export_unidade_completa
)
from functools import wraps
import io
from datetime import datetime
import qrcode
import base64
from io import BytesIO

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

def admin_principal_required(f):
    """Decorator para verificar se o usuário é admin principal"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Acesso restrito a administradores.', 'error')
            return redirect(url_for('main.login_admin'))
        
        admin = Administrador.query.get(session['admin_id'])
        if not admin or not admin.is_admin_principal():
            flash('Acesso restrito ao administrador principal.', 'error')
            return redirect(url_for('main.admin_dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def can_manage_unidade(unidade_id):
    """Decorator para verificar se o admin pode gerenciar uma unidade"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'admin_id' not in session:
                flash('Acesso restrito a administradores.', 'error')
                return redirect(url_for('main.login_admin'))
            
            admin = Administrador.query.get(session['admin_id'])
            if not admin or not admin.can_manage_unidade(unidade_id):
                flash('Você não tem permissão para gerenciar esta unidade.', 'error')
                return redirect(url_for('main.admin_dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def can_manage_lista(lista_id):
    """Decorator para verificar se o admin pode gerenciar uma lista"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'admin_id' not in session:
                flash('Acesso restrito a administradores.', 'error')
                return redirect(url_for('main.login_admin'))
            
            lista = Lista.query.get_or_404(lista_id)
            admin = Administrador.query.get(session['admin_id'])
            if not admin or not admin.can_manage_lista(lista):
                flash('Você não tem permissão para gerenciar esta lista.', 'error')
                return redirect(url_for('main.admin_dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

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
    admin = Administrador.query.get(session['admin_id'])
    
    if not admin:
        flash('Usuário não encontrado.', 'error')
        session.pop('admin_id', None)
        session.pop('admin_nome', None)
        return redirect(url_for('main.login_admin'))
    
    # Paginação para unidades
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if admin.is_admin_principal():
        # Admin principal vê todas as unidades
        unidades_pagination = UnidadeOrganizadora.query.order_by(UnidadeOrganizadora.data_criacao.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        unidades = unidades_pagination.items
        admins = Administrador.query.all()
    else:
        # Admin de unidade vê apenas suas unidades
        unidades = admin.unidades
        unidades_pagination = None
        admins = []

    # Cálculo dos totais para os cards
    total_listas = 0
    total_ativas = 0
    total_concluidas = 0
    total_canceladas = 0
    total_doacoes = 0
    doadores_unicos = set()
    todas_listas = []

    for unidade in unidades:
        total_listas += len(unidade.listas)
        for lista in unidade.listas:
            todas_listas.append(lista)
            if not lista.concluida and not lista.cancelada:
                total_ativas += 1
            if lista.concluida:
                total_concluidas += 1
            if lista.cancelada:
                total_canceladas += 1
            for item in lista.itens:
                total_doacoes += len(item.doacoes)
                for doacao in item.doacoes:
                    doadores_unicos.add(doacao.doador_nome)

    # Ordenar listas por data de criação (mais recentes primeiro) e pegar as 10 mais recentes
    listas_recentes = sorted(todas_listas, key=lambda x: x.data_criacao, reverse=True)[:10]

    return render_template(
        'admin/dashboard.html',
        unidades=unidades,
        unidades_pagination=unidades_pagination,
        admins=admins,
        admin=admin,
        listas_recentes=listas_recentes,
        total_listas=total_listas,
        total_ativas=total_ativas,
        total_concluidas=total_concluidas,
        total_canceladas=total_canceladas,
        total_doacoes=total_doacoes,
        total_doadores_unicos=len(doadores_unicos)
    )

@main.route('/admin/usuarios')
@admin_principal_required
def gerenciar_usuarios():
    """Gerenciamento de usuários - apenas admin principal"""
    page = request.args.get('page', 1, type=int)
    per_page = 15
    
    pagination = Administrador.query.order_by(Administrador.data_criacao.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/usuarios.html', pagination=pagination)

@main.route('/admin/usuario/criar', methods=['GET', 'POST'])
@admin_principal_required
def criar_usuario():
    """Criar novo usuário - apenas admin principal"""
    form = AdminForm()
    if form.validate_on_submit():
        admin = Administrador(
            username=form.username.data,
            email=form.email.data,
            nome=form.nome.data,
            role=form.role.data
        )
        admin.set_password(form.password.data)
        
        db.session.add(admin)
        db.session.commit()
        
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('main.gerenciar_usuarios'))
    
    return render_template('admin/criar_usuario.html', form=form)

@main.route('/admin/usuario/<int:admin_id>/editar', methods=['GET', 'POST'])
@admin_principal_required
def editar_usuario(admin_id):
    """Editar usuário - apenas admin principal"""
    admin = Administrador.query.get_or_404(admin_id)
    form = AdminEditForm(obj=admin)
    
    if form.validate_on_submit():
        admin.username = form.username.data
        admin.email = form.email.data
        admin.nome = form.nome.data
        admin.role = form.role.data
        admin.ativo = form.ativo.data
        
        if form.password.data:
            admin.set_password(form.password.data)
        
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('main.gerenciar_usuarios'))
    
    return render_template('admin/editar_usuario.html', form=form, admin=admin)

@main.route('/unidade/cadastrar', methods=['GET', 'POST'])
@admin_required
def cadastrar_unidade():
    """Cadastro de nova unidade organizadora"""
    admin = Administrador.query.get(session['admin_id'])
    
    if not admin:
        flash('Usuário não encontrado.', 'error')
        session.pop('admin_id', None)
        session.pop('admin_nome', None)
        return redirect(url_for('main.login_admin'))
    
    form = UnidadeForm()
    
    if form.validate_on_submit():
        unidade = UnidadeOrganizadora(
            # Informações Básicas
            nome=form.nome.data,
            razao_social=form.razao_social.data,
            nome_fantasia=form.nome_fantasia.data,
            responsavel=form.responsavel.data,
            email=form.email.data,
            email_secundario=form.email_secundario.data,
            descricao=form.descricao.data,
            
            # Dados Legais/Institucionais
            cnpj=form.cnpj.data,
            tipo_organizacao=form.tipo_organizacao.data,
            data_fundacao=form.data_fundacao.data,
            registro_inscricao=form.registro_inscricao.data,
            
            # Endereço Completo
            cep=form.cep.data,
            logradouro=form.logradouro.data,
            numero=form.numero.data,
            complemento=form.complemento.data,
            bairro=form.bairro.data,
            cidade=form.cidade.data,
            estado=form.estado.data,
            
            # Contatos
            telefone_fixo=form.telefone_fixo.data,
            whatsapp_numero=form.whatsapp_numero.data,
            horario_funcionamento=form.horario_funcionamento.data,
            dias_funcionamento=form.dias_funcionamento.data,
            
            # Presença Digital
            website_url=form.website_url.data,
            facebook_url=form.facebook_url.data,
            instagram_url=form.instagram_url.data,
            linkedin_url=form.linkedin_url.data,
            youtube_url=form.youtube_url.data,
            
            # Dados para Relatórios
            categoria=form.categoria.data,
            publico_alvo=form.publico_alvo.data,
            area_atuacao=form.area_atuacao.data,
            tamanho_organizacao=form.tamanho_organizacao.data,
            
            # Relacionamento
            admin_id=admin.id if not admin.is_admin_principal() else None
        )
        db.session.add(unidade)
        db.session.commit()
        
        flash('Unidade cadastrada com sucesso!', 'success')
        return redirect(url_for('main.admin_dashboard'))
    
    return render_template('cadastrar_unidade.html', form=form)

@main.route('/unidade/<int:unidade_id>/editar', methods=['GET', 'POST'])
@admin_required
def editar_unidade(unidade_id):
    """Editar unidade organizadora"""
    admin = Administrador.query.get(session['admin_id'])
    
    if not admin:
        flash('Usuário não encontrado.', 'error')
        session.pop('admin_id', None)
        session.pop('admin_nome', None)
        return redirect(url_for('main.login_admin'))
    
    # Verificar permissão
    if not admin.can_manage_unidade(unidade_id):
        flash('Você não tem permissão para editar esta unidade.', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    unidade = UnidadeOrganizadora.query.get_or_404(unidade_id)
    form = UnidadeForm(obj=unidade)
    
    if form.validate_on_submit():
        # Informações Básicas
        unidade.nome = form.nome.data
        unidade.razao_social = form.razao_social.data
        unidade.nome_fantasia = form.nome_fantasia.data
        unidade.responsavel = form.responsavel.data
        unidade.email = form.email.data
        unidade.email_secundario = form.email_secundario.data
        unidade.descricao = form.descricao.data
        
        # Dados Legais/Institucionais
        unidade.cnpj = form.cnpj.data
        unidade.tipo_organizacao = form.tipo_organizacao.data
        unidade.data_fundacao = form.data_fundacao.data
        unidade.registro_inscricao = form.registro_inscricao.data
        
        # Endereço Completo
        unidade.cep = form.cep.data
        unidade.logradouro = form.logradouro.data
        unidade.numero = form.numero.data
        unidade.complemento = form.complemento.data
        unidade.bairro = form.bairro.data
        unidade.cidade = form.cidade.data
        unidade.estado = form.estado.data
        
        # Contatos
        unidade.telefone_fixo = form.telefone_fixo.data
        unidade.whatsapp_numero = form.whatsapp_numero.data
        unidade.horario_funcionamento = form.horario_funcionamento.data
        unidade.dias_funcionamento = form.dias_funcionamento.data
        
        # Presença Digital
        unidade.website_url = form.website_url.data
        unidade.facebook_url = form.facebook_url.data
        unidade.instagram_url = form.instagram_url.data
        unidade.linkedin_url = form.linkedin_url.data
        unidade.youtube_url = form.youtube_url.data
        
        # Dados para Relatórios
        unidade.categoria = form.categoria.data
        unidade.publico_alvo = form.publico_alvo.data
        unidade.area_atuacao = form.area_atuacao.data
        unidade.tamanho_organizacao = form.tamanho_organizacao.data
        
        db.session.commit()
        
        flash('Unidade atualizada com sucesso!', 'success')
        return redirect(url_for('main.admin_dashboard'))
    
    return render_template('editar_unidade.html', form=form, unidade=unidade)

@main.route('/lista/criar/<int:unidade_id>', methods=['GET', 'POST'])
@admin_required
def criar_lista(unidade_id):
    """Criação de lista associada a uma unidade"""
    # Verificar permissão
    admin = Administrador.query.get(session['admin_id'])
    
    if not admin:
        flash('Usuário não encontrado.', 'error')
        session.pop('admin_id', None)
        session.pop('admin_nome', None)
        return redirect(url_for('main.login_admin'))
    
    if not admin.can_manage_unidade(unidade_id):
        flash('Você não tem permissão para gerenciar esta unidade.', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    unidade = UnidadeOrganizadora.query.get_or_404(unidade_id)
    form = ListaForm()
    
    if form.validate_on_submit():
        lista = Lista(
            nome=form.nome.data,
            descricao=form.descricao.data,
            modo=form.modo.data,
            aceita_pix=form.aceita_pix.data,
            chave_pix=form.chave_pix.data if form.aceita_pix.data else None,
            unidade_id=unidade.id,
            solicitar_dados_pessoais=form.solicitar_dados_pessoais.data
        )
        db.session.add(lista)
        db.session.commit()
        
        flash('Lista criada com sucesso!', 'success')
        return redirect(url_for('main.adicionar_itens', lista_id=lista.id))
    
    return render_template('criar_lista.html', form=form, unidade=unidade)

@main.route('/lista/<int:lista_id>/itens', methods=['GET', 'POST'])
@admin_required
def adicionar_itens(lista_id):
    """Adicionar itens à lista"""
    # Verificar permissão
    lista = Lista.query.get_or_404(lista_id)
    admin = Administrador.query.get(session['admin_id'])
    
    if not admin:
        flash('Usuário não encontrado.', 'error')
        session.pop('admin_id', None)
        session.pop('admin_nome', None)
        return redirect(url_for('main.login_admin'))
    
    if not admin.can_manage_lista(lista):
        flash('Você não tem permissão para gerenciar esta lista.', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
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
    if lista.cancelada:
        flash('Esta campanha foi cancelada e não está mais disponível para doações.', 'error')
        return redirect(url_for('main.index'))
    if lista.concluida:
        flash('Esta campanha foi concluída e não aceita mais doações.', 'info')
    
    # Verificar se houve uma doação bem-sucedida
    doacao_sucesso = request.args.get('doacao_sucesso') == 'true'
    
    form = DoacaoForm()
    return render_template('visualizar_lista.html', lista=lista, form=form, doacao_sucesso=doacao_sucesso)

@main.route('/lista/<slug>/doar', methods=['POST'])
def doar(slug):
    """Processar doação - ACESSO PÚBLICO"""
    lista = Lista.query.filter_by(slug=slug, ativa=True).first_or_404()
    
    if lista.concluida:
        flash('Esta lista foi concluída e não aceita mais doações.', 'error')
        return redirect(url_for('main.visualizar_lista', slug=slug))
    
    if lista.cancelada:
        flash('Esta lista foi cancelada e não aceita doações.', 'error')
        return redirect(url_for('main.visualizar_lista', slug=slug))
    
    form = DoacaoForm()
    
    if form.validate_on_submit():
        item = Item.query.get_or_404(form.item_id.data)
        
        # Verificar se o item pertence à lista
        if item.lista_id != lista.id:
            flash('Item inválido.', 'error')
            return redirect(url_for('main.visualizar_lista', slug=slug))
        
        # Verificar se a quantidade não excede o necessário
        if item.quantidade_restante < form.quantidade.data:
            flash('Quantidade excede o necessário para este item.', 'error')
            return redirect(url_for('main.visualizar_lista', slug=slug))
        
        # Verificar se PIX está habilitado se for doação PIX
        if form.tipo_doacao.data == 'dinheiro' and not lista.aceita_pix:
            flash('Esta lista não aceita doações financeiras.', 'error')
            return redirect(url_for('main.visualizar_lista', slug=slug))
        
        # Lógica de identificação/cadastro do doador
        identificador = (form.identificador.data or '').strip()
        doador = None
        if identificador:
            doador = Doador.query.filter(
                (Doador.cpf == identificador) |
                (Doador.contato == identificador)
            ).first()
        if not doador:
            # Cadastro de novo doador
            doador = Doador(
                nome=form.doador_nome.data,
                cpf=form.cpf.data,
                cep=form.cep.data,
                contato=form.contato.data,
                # Campos de endereço
                logradouro=form.logradouro.data,
                numero=form.numero.data,
                complemento=form.complemento.data,
                bairro=form.bairro.data,
                cidade=form.cidade.data,
                estado=form.estado.data
            )
            db.session.add(doador)
            db.session.commit()
        else:
            # Atualizar dados se fornecidos
            if form.doador_nome.data:
                doador.nome = form.doador_nome.data
            if form.cpf.data:
                doador.cpf = form.cpf.data
            if form.cep.data:
                doador.cep = form.cep.data
            if form.contato.data:
                doador.contato = form.contato.data
            # Atualizar campos de endereço
            if form.logradouro.data:
                doador.logradouro = form.logradouro.data
            if form.numero.data:
                doador.numero = form.numero.data
            if form.complemento.data:
                doador.complemento = form.complemento.data
            if form.bairro.data:
                doador.bairro = form.bairro.data
            if form.cidade.data:
                doador.cidade = form.cidade.data
            if form.estado.data:
                doador.estado = form.estado.data
            db.session.commit()
        
        # Criar doação baseada no tipo
        if form.tipo_doacao.data == 'item':
            doacao = Doacao(
                doador_id=doador.id,
                doador_nome=doador.nome,
                cpf=doador.cpf,
                cep=doador.cep,
                contato=doador.contato,
                tipo_doacao='item',
                quantidade=form.quantidade.data,
                item_id=item.id,
                observacao=form.observacao.data
            )
        else:  # dinheiro
            doacao = Doacao(
                doador_id=doador.id,
                doador_nome=doador.nome,
                cpf=doador.cpf,
                cep=doador.cep,
                contato=doador.contato,
                tipo_doacao='dinheiro',
                valor_dinheiro=form.valor_dinheiro.data,
                item_id=item.id,  # Associar ao item específico
                observacao=form.observacao.data
            )
        
        db.session.add(doacao)
        db.session.commit()
        
        # Enviar notificação por email
        send_notification_email(lista, doacao)
        
        flash(f'Doação registrada com sucesso! Obrigado pela sua contribuição, {doador.nome}!', 'success')
        return redirect(url_for('main.visualizar_lista', slug=slug, doacao_sucesso='true'))
    
    return redirect(url_for('main.visualizar_lista', slug=slug))

@main.route('/lista/<slug>/sugerir', methods=['POST'])
def sugerir_item(slug):
    """Processar sugestão de item - ACESSO PÚBLICO"""
    lista = Lista.query.filter_by(slug=slug, ativa=True).first_or_404()
    
    # Verificar se a lista está no modo aberto
    if lista.modo != 'aberto':
        flash('Esta lista não aceita sugestões de itens.', 'error')
        return redirect(url_for('main.visualizar_lista', slug=slug))
    
    form = SugestaoItemForm()
    
    if form.validate_on_submit():
        sugestao = SugestaoItem(
            nome=form.nome.data,
            quantidade_necessaria=form.quantidade_necessaria.data,
            unidade_medida=form.unidade_medida.data or 'unidades',
            descricao=form.descricao.data,
            sugestor_nome=form.sugestor_nome.data,
            lista_id=lista.id
        )
        db.session.add(sugestao)
        db.session.commit()
        
        flash('Sugestão enviada com sucesso! O administrador irá analisar sua sugestão.', 'success')
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
        lista.solicitar_dados_pessoais = form.solicitar_dados_pessoais.data
        db.session.commit()
        flash('Lista atualizada com sucesso!', 'success')
        return redirect(url_for('main.dashboard', token=token))
    
    return render_template('editar_lista.html', form=form, lista=lista)

@main.route('/admin/<token>/adicionar-itens', methods=['GET', 'POST'])
def adicionar_itens_lista(token):
    """Adicionar itens a uma lista existente - ACESSO VIA TOKEN"""
    lista = Lista.query.filter_by(token_admin=token).first_or_404()
    
    # Impedir adicionar itens se a lista não estiver aberta
    if lista.modo != 'aberto' or lista.concluida or lista.cancelada:
        flash('Só é possível adicionar itens em listas abertas e ativas.', 'error')
        return redirect(url_for('main.dashboard', token=token))

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
@admin_required
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
@admin_required
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

@main.route('/exportar/<slug>.xlsx')
@admin_required
def exportar_excel(slug):
    """Exportar lista em Excel (XLSX) - ACESSO PÚBLICO"""
    lista = Lista.query.filter_by(slug=slug).first_or_404()
    xlsx_content = export_lista_excel(lista)
    output = io.BytesIO()
    output.write(xlsx_content)
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'lista_{lista.slug}.xlsx'
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

@main.route('/admin/<token>/sugestoes')
def gerenciar_sugestoes(token):
    """Gerenciar sugestões de itens para uma lista"""
    lista = Lista.query.filter_by(token_admin=token).first_or_404()
    
    # Paginação para sugestões
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Buscar sugestões com paginação
    sugestoes_query = SugestaoItem.query.filter_by(lista_id=lista.id).order_by(SugestaoItem.data_sugestao.desc())
    pagination = sugestoes_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('gerenciar_sugestoes.html', lista=lista, pagination=pagination)

@main.route('/admin/<token>/sugestao/<int:sugestao_id>/aprovar', methods=['POST'])
def aprovar_sugestao(token, sugestao_id):
    """Aprovar sugestão e criar item - ACESSO VIA TOKEN"""
    lista = Lista.query.filter_by(token_admin=token).first_or_404()
    sugestao = SugestaoItem.query.get_or_404(sugestao_id)
    
    if sugestao.lista_id != lista.id:
        flash('Sugestão não pertence a esta lista.', 'error')
        return redirect(url_for('main.gerenciar_sugestoes', token=token))
    
    # Criar item a partir da sugestão
    item = Item(
        nome=sugestao.nome,
        quantidade_necessaria=sugestao.quantidade_necessaria,
        unidade_medida=sugestao.unidade_medida,
        descricao=sugestao.descricao,
        lista_id=lista.id
    )
    
    # Marcar sugestão como aprovada
    sugestao.aprovada = True
    
    db.session.add(item)
    db.session.commit()
    
    flash(f'Sugestão "{sugestao.nome}" aprovada e adicionada à lista!', 'success')
    return redirect(url_for('main.gerenciar_sugestoes', token=token))

@main.route('/admin/<token>/sugestao/<int:sugestao_id>/rejeitar', methods=['POST'])
def rejeitar_sugestao(token, sugestao_id):
    """Rejeitar sugestão - ACESSO VIA TOKEN"""
    lista = Lista.query.filter_by(token_admin=token).first_or_404()
    sugestao = SugestaoItem.query.get_or_404(sugestao_id)
    
    if sugestao.lista_id != lista.id:
        flash('Sugestão não pertence a esta lista.', 'error')
        return redirect(url_for('main.gerenciar_sugestoes', token=token))
    
    # Remover sugestão
    db.session.delete(sugestao)
    db.session.commit()
    
    flash(f'Sugestão "{sugestao.nome}" rejeitada.', 'success')
    return redirect(url_for('main.gerenciar_sugestoes', token=token))

@main.route('/admin/listas-ativas')
@admin_required
def listas_ativas():
    """Lista de arrecadações ativas com paginação"""
    admin = Administrador.query.get(session['admin_id'])
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if admin.is_admin_principal():
        # Admin principal vê todas as listas ativas
        pagination = Lista.query.filter_by(concluida=False).order_by(Lista.data_criacao.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        # Buscar todas as listas ativas para estatísticas (sem paginação)
        todas_listas_ativas = Lista.query.filter_by(concluida=False).all()
    else:
        # Admin de unidade vê apenas suas listas ativas
        unidade_ids = [unidade.id for unidade in admin.unidades]
        pagination = Lista.query.filter_by(concluida=False).filter(Lista.unidade_id.in_(unidade_ids)).order_by(Lista.data_criacao.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        # Buscar todas as listas ativas do admin para estatísticas (sem paginação)
        todas_listas_ativas = Lista.query.filter_by(concluida=False).filter(Lista.unidade_id.in_(unidade_ids)).all()
    
    # Calcular estatísticas completas
    total_listas = len(todas_listas_ativas)
    total_itens = 0
    total_doacoes = 0
    doadores_unicos = set()
    
    for lista in todas_listas_ativas:
        total_itens += len(lista.itens)
        for item in lista.itens:
            total_doacoes += len(item.doacoes)
            for doacao in item.doacoes:
                doadores_unicos.add(doacao.doador_nome)
    
    return render_template(
        'admin/listas_ativas.html', 
        pagination=pagination, 
        admin=admin,
        total_listas=total_listas,
        total_itens=total_itens,
        total_doacoes=total_doacoes,
        total_doadores_unicos=len(doadores_unicos)
    )

@main.route('/admin/listas-concluidas')
@admin_required
def listas_concluidas():
    """Lista de arrecadações concluídas com paginação"""
    admin = Administrador.query.get(session['admin_id'])
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if admin.is_admin_principal():
        # Admin principal vê todas as listas concluídas
        pagination = Lista.query.filter_by(concluida=True).order_by(Lista.data_conclusao.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        # Buscar todas as listas concluídas para estatísticas (sem paginação)
        todas_listas_concluidas = Lista.query.filter_by(concluida=True).all()
    else:
        # Admin de unidade vê apenas suas listas concluídas
        unidade_ids = [unidade.id for unidade in admin.unidades]
        pagination = Lista.query.filter_by(concluida=True).filter(Lista.unidade_id.in_(unidade_ids)).order_by(Lista.data_conclusao.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        # Buscar todas as listas concluídas do admin para estatísticas (sem paginação)
        todas_listas_concluidas = Lista.query.filter_by(concluida=True).filter(Lista.unidade_id.in_(unidade_ids)).all()
    
    # Calcular estatísticas completas
    total_listas = len(todas_listas_concluidas)
    total_itens = 0
    total_doacoes = 0
    doadores_unicos = set()
    
    for lista in todas_listas_concluidas:
        total_itens += len(lista.itens)
        for item in lista.itens:
            total_doacoes += len(item.doacoes)
            for doacao in item.doacoes:
                doadores_unicos.add(doacao.doador_nome)
    
    return render_template(
        'admin/listas_concluidas.html', 
        pagination=pagination, 
        admin=admin,
        total_listas=total_listas,
        total_itens=total_itens,
        total_doacoes=total_doacoes,
        total_doadores_unicos=len(doadores_unicos)
    )

@main.route('/admin/lista/<int:lista_id>/concluir', methods=['POST'])
@admin_required
def concluir_lista(lista_id):
    """Marcar lista como concluída"""
    admin = Administrador.query.get(session['admin_id'])
    lista = Lista.query.get_or_404(lista_id)
    
    if not admin.can_manage_lista(lista):
        flash('Você não tem permissão para gerenciar esta lista.', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    lista.concluida = True
    from datetime import datetime
    lista.data_conclusao = datetime.utcnow()
    db.session.commit()
    
    flash(f'Lista "{lista.nome}" marcada como concluída!', 'success')
    return redirect(url_for('main.listas_ativas'))

@main.route('/admin/lista/<int:lista_id>/cancelar', methods=['POST'])
@admin_required
def cancelar_lista(lista_id):
    """Cancelar/desativar lista"""
    admin = Administrador.query.get(session['admin_id'])
    lista = Lista.query.get_or_404(lista_id)
    motivo = (request.form.get('motivo_cancelamento') or '').strip()
    if not admin.can_manage_lista(lista):
        flash('Você não tem permissão para gerenciar esta lista.', 'error')
        return redirect(url_for('main.admin_dashboard'))
    lista.cancelada = True
    lista.motivo_cancelamento = motivo
    db.session.commit()
    flash(f'Lista "{lista.nome}" cancelada com sucesso!', 'success')
    return redirect(url_for('main.listas_ativas'))

@main.route('/admin/lista/<int:lista_id>/reativar', methods=['POST'])
@admin_required
def reativar_lista(lista_id):
    """Reativar lista cancelada (não permite para concluídas)"""
    admin = Administrador.query.get(session['admin_id'])
    lista = Lista.query.get_or_404(lista_id)
    if not admin.can_manage_lista(lista):
        flash('Você não tem permissão para gerenciar esta lista.', 'error')
        return redirect(url_for('main.admin_dashboard'))
    if lista.concluida:
        flash('Campanhas concluídas não podem ser reabertas. Para uma nova rodada, utilize a opção de clonar campanha.', 'warning')
        return redirect(url_for('main.listas_concluidas'))
    lista.cancelada = False
    lista.motivo_cancelamento = None
    db.session.commit()
    flash(f'Lista "{lista.nome}" reativada com sucesso!', 'success')
    return redirect(url_for('main.listas_ativas'))

@main.route('/admin/lista/<int:lista_id>/excluir', methods=['POST'])
@admin_principal_required
def excluir_lista(lista_id):
    """Excluir lista definitivamente (apenas admin principal)"""
    lista = Lista.query.get_or_404(lista_id)
    nome = lista.nome
    db.session.delete(lista)
    db.session.commit()
    flash(f'Lista "{nome}" excluída permanentemente!', 'success')
    return redirect(url_for('main.listas_ativas'))

@main.route('/admin/lista/<int:lista_id>/clonar', methods=['POST'])
@admin_required
def clonar_lista(lista_id):
    """Clonar uma lista concluída para nova campanha"""
    admin = Administrador.query.get(session['admin_id'])
    lista_original = Lista.query.get_or_404(lista_id)
    if not admin.can_manage_lista(lista_original):
        flash('Você não tem permissão para clonar esta lista.', 'error')
        return redirect(url_for('main.admin_dashboard'))
    if not lista_original.concluida:
        flash('Só é possível clonar campanhas concluídas.', 'warning')
        return redirect(url_for('main.listas_concluidas'))
    # Criar nova lista
    nova_lista = Lista(
        nome=f'Cópia de {lista_original.nome}',
        descricao=lista_original.descricao,
        modo=lista_original.modo,
        aceita_pix=lista_original.aceita_pix,
        chave_pix=lista_original.chave_pix,
        unidade_id=lista_original.unidade_id,
        ativa=True,
        concluida=False,
        cancelada=False,
        data_criacao=datetime.utcnow()
    )
    db.session.add(nova_lista)
    db.session.commit()
    # Clonar itens (sem doações)
    for item in lista_original.itens:
        novo_item = Item(
            nome=item.nome,
            quantidade_necessaria=item.quantidade_necessaria,
            unidade_medida=item.unidade_medida,
            descricao=item.descricao,
            lista_id=nova_lista.id
        )
        db.session.add(novo_item)
    db.session.commit()
    flash(f'Campanha clonada com sucesso! Edite os detalhes antes de publicar.', 'success')
    return redirect(url_for('main.editar_lista', token=nova_lista.token_admin))

@main.route('/admin/<token>/item/<int:item_id>/editar', methods=['GET', 'POST'])
def editar_item(token, item_id):
    """Editar item individual - ACESSO VIA TOKEN"""
    lista = Lista.query.filter_by(token_admin=token).first_or_404()
    item = Item.query.get_or_404(item_id)
    
    # Verificar se o item pertence à lista
    if item.lista_id != lista.id:
        flash('Item não pertence a esta lista.', 'error')
        return redirect(url_for('main.dashboard', token=token))
    
    # Verificar se o item tem doações
    if item.doacoes:
        flash('Não é possível editar itens que já possuem doações registradas.', 'error')
        return redirect(url_for('main.adicionar_itens_lista', token=token))
    
    # Impedir editar se a lista não estiver aberta
    if lista.modo != 'aberto' or lista.concluida or lista.cancelada:
        flash('Só é possível editar itens em listas abertas e ativas.', 'error')
        return redirect(url_for('main.dashboard', token=token))
    
    form = ItemEditForm(obj=item)
    
    if form.validate_on_submit():
        item.nome = form.nome.data
        item.quantidade_necessaria = form.quantidade_necessaria.data
        item.unidade_medida = form.unidade_medida.data or 'unidades'
        item.descricao = form.descricao.data
        
        db.session.commit()
        flash('Item atualizado com sucesso!', 'success')
        return redirect(url_for('main.adicionar_itens_lista', token=token))
    
    return render_template('editar_item.html', form=form, item=item, lista=lista)

@main.route('/admin/<token>/item/<int:item_id>/excluir', methods=['POST'])
def excluir_item(token, item_id):
    """Excluir item individual - ACESSO VIA TOKEN"""
    lista = Lista.query.filter_by(token_admin=token).first_or_404()
    item = Item.query.get_or_404(item_id)
    
    # Verificar se o item pertence à lista
    if item.lista_id != lista.id:
        flash('Item não pertence a esta lista.', 'error')
        return redirect(url_for('main.adicionar_itens_lista', token=token))
    
    # Verificar se o item tem doações
    if item.doacoes:
        flash('Não é possível excluir itens que possuem doações registradas.', 'error')
        return redirect(url_for('main.adicionar_itens_lista', token=token))
    
    # Impedir excluir se a lista não estiver aberta
    if lista.modo != 'aberto' or lista.concluida or lista.cancelada:
        flash('Só é possível excluir itens em listas abertas e ativas.', 'error')
        return redirect(url_for('main.adicionar_itens_lista', token=token))
    
    nome_item = item.nome
    db.session.delete(item)
    db.session.commit()
    
    flash(f'Item "{nome_item}" excluído com sucesso!', 'success')
    return redirect(url_for('main.adicionar_itens_lista', token=token))

@main.route('/doar/<slug>/<int:item_id>', methods=['GET', 'POST'])
def doar_pagina(slug, item_id):
    """Página dedicada para doação de um item específico"""
    lista = Lista.query.filter_by(slug=slug, ativa=True).first_or_404()
    item = Item.query.get_or_404(item_id)
    if item.lista_id != lista.id:
        flash('Item inválido.', 'error')
        return redirect(url_for('main.visualizar_lista', slug=slug))
    if lista.concluida:
        flash('Esta lista foi concluída e não aceita mais doações.', 'error')
        return redirect(url_for('main.visualizar_lista', slug=slug))
    if lista.cancelada:
        flash('Esta lista foi cancelada e não aceita doações.', 'error')
        return redirect(url_for('main.visualizar_lista', slug=slug))
    form = DoacaoForm()
    if form.validate_on_submit():
        # Verificar tipo de doação
        if form.tipo_doacao.data == 'item':
            # Doação física - verificar quantidade
            if not form.quantidade.data or form.quantidade.data < 1:
                flash('Quantidade deve ser maior que zero.', 'error')
                return redirect(url_for('main.doar_pagina', slug=slug, item_id=item_id))
            
            if item.quantidade_restante < form.quantidade.data:
                flash('Quantidade excede o necessário para este item.', 'error')
                return redirect(url_for('main.doar_pagina', slug=slug, item_id=item_id))
        
        elif form.tipo_doacao.data == 'dinheiro':
            # Doação financeira - verificar valor
            if not form.valor_dinheiro.data or form.valor_dinheiro.data <= 0:
                flash('Valor da doação deve ser maior que zero.', 'error')
                return redirect(url_for('main.doar_pagina', slug=slug, item_id=item_id))
        
        # Verificar se PIX está habilitado se for doação PIX
        if form.tipo_doacao.data == 'dinheiro' and not lista.aceita_pix:
            flash('Esta lista não aceita doações financeiras.', 'error')
            return redirect(url_for('main.visualizar_lista', slug=slug))
        
        # Lógica de identificação/cadastro do doador
        identificador = (form.identificador.data or '').strip()
        doador = None
        if identificador:
            doador = Doador.query.filter(
                (Doador.cpf == identificador) |
                (Doador.contato == identificador)
            ).first()
        if not doador:
            # Cadastro de novo doador
            doador = Doador(
                nome=form.doador_nome.data,
                cpf=form.cpf.data,
                cep=form.cep.data,
                contato=form.contato.data,
                # Campos de endereço
                logradouro=form.logradouro.data,
                numero=form.numero.data,
                complemento=form.complemento.data,
                bairro=form.bairro.data,
                cidade=form.cidade.data,
                estado=form.estado.data
            )
            db.session.add(doador)
            db.session.commit()
        else:
            # Atualizar dados se fornecidos
            if form.doador_nome.data:
                doador.nome = form.doador_nome.data
            if form.cpf.data:
                doador.cpf = form.cpf.data
            if form.cep.data:
                doador.cep = form.cep.data
            if form.contato.data:
                doador.contato = form.contato.data
            # Atualizar campos de endereço
            if form.logradouro.data:
                doador.logradouro = form.logradouro.data
            if form.numero.data:
                doador.numero = form.numero.data
            if form.complemento.data:
                doador.complemento = form.complemento.data
            if form.bairro.data:
                doador.bairro = form.bairro.data
            if form.cidade.data:
                doador.cidade = form.cidade.data
            if form.estado.data:
                doador.estado = form.estado.data
            db.session.commit()
        
        # Criar doação baseada no tipo
        if form.tipo_doacao.data == 'item':
            doacao = Doacao(
                doador_id=doador.id,
                doador_nome=doador.nome,
                cpf=doador.cpf,
                cep=doador.cep,
                contato=doador.contato,
                tipo_doacao='item',
                quantidade=form.quantidade.data,
                item_id=item.id,
                observacao=form.observacao.data
            )
        else:  # dinheiro
            doacao = Doacao(
                doador_id=doador.id,
                doador_nome=doador.nome,
                cpf=doador.cpf,
                cep=doador.cep,
                contato=doador.contato,
                tipo_doacao='dinheiro',
                valor_dinheiro=form.valor_dinheiro.data,
                item_id=item.id,  # Associar ao item específico
                observacao=form.observacao.data
            )
        
        db.session.add(doacao)
        db.session.commit()
        send_notification_email(lista, doacao)
        return redirect(url_for('main.agradecimento_doacao', slug=slug, doador_nome=doador.nome))
    return render_template('doar_pagina.html', lista=lista, item=item, form=form)

@main.route('/doar/<slug>/obrigado')
def agradecimento_doacao(slug):
    lista = Lista.query.filter_by(slug=slug, ativa=True).first_or_404()
    doador_nome = request.args.get('doador_nome', '')
    return render_template('agradecimento_doacao.html', lista=lista, doador_nome=doador_nome)

@main.route('/api/buscar-doador/<identificador>')
def buscar_doador(identificador):
    """API para buscar doador por CPF, e-mail ou telefone"""
    if not identificador or len(identificador.strip()) < 3:
        return jsonify({'encontrado': False})
    
    identificador = identificador.strip()
    
    # Buscar doador por CPF, e-mail ou telefone
    doador = Doador.query.filter(
        (Doador.cpf == identificador) |
        (Doador.contato == identificador)
    ).first()
    
    if doador:
        return jsonify({
            'encontrado': True,
            'doador': {
                'nome': doador.nome,
                'cpf': doador.cpf,
                'cep': doador.cep,
                'contato': doador.contato
            }
        })
    
    return jsonify({'encontrado': False})

@main.route('/api/gerar-qrcode-pix', methods=['POST'])
def gerar_qrcode_pix():
    """Gera QR Code PIX no backend"""
    print("=== INÍCIO: API gerar-qrcode-pix chamada ===")
    try:
        data = request.get_json()
        print(f"Dados recebidos: {data}")
        
        chave_pix = data.get('chave_pix')
        valor = data.get('valor')
        
        print(f"Chave PIX: {chave_pix}")
        print(f"Valor: {valor}")
        
        if not chave_pix or not valor:
            print("Erro: Chave PIX ou valor não fornecidos")
            return jsonify({'erro': 'Chave PIX e valor são obrigatórios'}), 400
        
        # Gerar payload PIX (formato EMV QR Code)
        payload_pix = gerar_payload_pix(chave_pix, valor)
        print(f"Payload PIX gerado: {payload_pix}")
        
        # Criar QR Code
        print("Criando QR Code...")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(payload_pix)
        qr.make(fit=True)
        
        # Criar imagem
        print("Criando imagem...")
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter para base64
        print("Convertendo para base64...")
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)
        img_data = buffer.getvalue()
        if img_data:
            img_str = base64.b64encode(img_data).decode()
            print(f"Imagem base64 gerada (primeiros 100 chars): {img_str[:100]}...")
            
            link_pix = f'pix://{chave_pix}?amount={valor}'
            print(f"Link PIX gerado: {link_pix}")
            
            response_data = {
                'success': True,
                'qrcode_base64': f'data:image/png;base64,{img_str}',
                'payload_pix': payload_pix,
                'link_pix': link_pix
            }
            print("Resposta enviada com sucesso")
            return jsonify(response_data)
        else:
            print("Erro: Imagem vazia")
            return jsonify({'erro': 'Erro ao gerar imagem'}), 500
        
    except Exception as e:
        print(f"Erro ao gerar QR Code: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'erro': 'Erro interno ao gerar QR Code'}), 500

def gerar_payload_pix(chave, valor):
    """Gera payload PIX no formato EMV QR Code"""
    # Gerar payload PIX básico (formato simplificado)
    merchant_name = 'Lista de Arrecadação'
    merchant_city = 'BRASIL'
    amount = str(valor)
    
    # Estrutura básica do payload PIX
    payload = '000201'  # Payload Format Indicator
    payload += '010212'  # Point of Initiation Method
    payload += '2662'  # Merchant Account Information
    payload += '0014BR.GOV.BCB.PIX'  # Global Unique Identifier
    payload += '01' + str(len(chave)).zfill(2) + chave  # PIX Key
    payload += '52040000'  # Merchant Category Code
    payload += '5303986'  # Transaction Currency
    payload += '54' + str(len(amount)).zfill(2) + amount  # Transaction Amount
    payload += '5802BR'  # Country Code
    payload += '59' + str(len(merchant_name)).zfill(2) + merchant_name  # Merchant Name
    payload += '60' + str(len(merchant_city)).zfill(2) + merchant_city  # Merchant City
    payload += '6304'  # CRC16
    
    # Calcular CRC16 (simplificado)
    crc = '1234'  # CRC16 simplificado
    payload += crc
    
    return payload 

@main.route('/api/consultar-cep/<cep>')
def api_consultar_cep(cep):
    """API para consultar CEP via ViaCEP"""
    try:
        # Validar formato do CEP
        if not validar_cep(cep):
            return jsonify({
                'success': False,
                'error': 'Formato de CEP inválido. Use apenas números ou formato 00000-000.'
            }), 400
        
        # Consultar CEP
        resultado = consultar_cep(cep)
        
        if resultado:
            return jsonify({
                'success': True,
                'endereco': resultado
            })
        else:
            return jsonify({
                'success': False,
                'error': 'CEP não encontrado ou erro na consulta.'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Erro interno do servidor.'
        }), 500

@main.route('/exportar/unidade/<int:unidade_id>.xlsx')
@admin_required
def exportar_unidade_completa(unidade_id):
    """Exportar dados completos da unidade em Excel"""
    # Verificar permissão
    admin = Administrador.query.get(session['admin_id'])
    if not admin.can_manage_unidade(unidade_id):
        flash('Você não tem permissão para exportar dados desta unidade.', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    unidade = UnidadeOrganizadora.query.get_or_404(unidade_id)
    excel_content = export_unidade_completa(unidade)
    
    output = io.BytesIO()
    output.write(excel_content)
    output.seek(0)
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'unidade_{unidade.nome.replace(" ", "_")}.xlsx'
    )

@main.route('/admin/unidade/<int:unidade_id>/listas')
@admin_required
def listas_unidade(unidade_id):
    """Visualizar todas as listas de uma unidade específica"""
    admin = Administrador.query.get(session['admin_id'])
    unidade = UnidadeOrganizadora.query.get_or_404(unidade_id)
    
    # Verificar se o admin tem permissão para ver esta unidade
    if not admin.is_admin_principal() and unidade not in admin.unidades:
        flash('Você não tem permissão para visualizar esta unidade.', 'error')
        return redirect(url_for('main.admin_dashboard'))
    
    # Paginação para listas
    page = request.args.get('page', 1, type=int)
    per_page = 15
    
    # Ordenar listas por data de criação (mais recentes primeiro)
    listas_query = Lista.query.filter_by(unidade_id=unidade_id).order_by(Lista.data_criacao.desc())
    pagination = listas_query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template(
        'admin/listas_unidade.html',
        unidade=unidade,
        listas=pagination.items,
        pagination=pagination,
        admin=admin
    ) 