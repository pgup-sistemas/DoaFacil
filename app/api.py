from flask import Blueprint, request, jsonify
from app import db
from app.models import Lista, Item, Doacao, UnidadeOrganizadora
from app.utils import send_notification_email

api_bp = Blueprint('api', __name__)

@api_bp.route('/listas/<slug>', methods=['GET'])
def get_lista(slug):
    """Obter informações de uma lista"""
    lista = Lista.query.filter_by(slug=slug, ativa=True).first()
    
    if not lista:
        return jsonify({'error': 'Lista não encontrada'}), 404
    
    return jsonify({
        'id': lista.id,
        'nome': lista.nome,
        'descricao': lista.descricao,
        'modo': lista.modo,
        'aceita_pix': lista.aceita_pix,
        'chave_pix': lista.chave_pix,
        'percentual_geral': lista.percentual_conclusao,
        'unidade': {
            'nome': lista.unidade.nome,
            'responsavel': lista.unidade.responsavel
        },
        'itens': [{
            'id': item.id,
            'nome': item.nome,
            'quantidade_necessaria': item.quantidade_necessaria,
            'quantidade_arrecadada': item.quantidade_arrecadada,
            'quantidade_restante': item.quantidade_restante,
            'percentual': item.percentual_conclusao,
            'unidade_medida': item.unidade_medida,
            'descricao': item.descricao
        } for item in lista.itens]
    })

@api_bp.route('/listas/<slug>/doacoes', methods=['POST'])
def criar_doacao(slug):
    """Criar uma nova doação via API"""
    lista = Lista.query.filter_by(slug=slug, ativa=True).first()
    
    if not lista:
        return jsonify({'error': 'Lista não encontrada'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    item_id = data.get('item_id')
    doador_nome = data.get('doador_nome')
    quantidade = data.get('quantidade')
    observacao = data.get('observacao', '')
    
    if not all([item_id, doador_nome, quantidade]):
        return jsonify({'error': 'Dados incompletos'}), 400
    
    item = Item.query.get(item_id)
    if not item or item.lista_id != lista.id:
        return jsonify({'error': 'Item inválido'}), 400
    
    if item.quantidade_restante < quantidade:
        return jsonify({'error': 'Quantidade excede o necessário'}), 400
    
    doacao = Doacao(
        doador_nome=doador_nome,
        quantidade=quantidade,
        observacao=observacao,
        item_id=item.id
    )
    
    db.session.add(doacao)
    db.session.commit()
    
    # Enviar notificação
    send_notification_email(lista, doacao)
    
    return jsonify({
        'success': True,
        'message': 'Doação registrada com sucesso',
        'doacao': {
            'id': doacao.id,
            'doador_nome': doacao.doador_nome,
            'quantidade': doacao.quantidade,
            'data_doacao': doacao.data_doacao.isoformat()
        },
        'item_atualizado': {
            'quantidade_arrecadada': item.quantidade_arrecadada,
            'quantidade_restante': item.quantidade_restante,
            'percentual': item.percentual_conclusao
        }
    }), 201

@api_bp.route('/listas/<slug>/doacoes', methods=['GET'])
def listar_doacoes(slug):
    """Listar doações de uma lista"""
    lista = Lista.query.filter_by(slug=slug, ativa=True).first()
    
    if not lista:
        return jsonify({'error': 'Lista não encontrada'}), 404
    
    doacoes = []
    for item in lista.itens:
        for doacao in item.doacoes:
            doacoes.append({
                'id': doacao.id,
                'doador_nome': doacao.doador_nome,
                'quantidade': doacao.quantidade,
                'observacao': doacao.observacao,
                'data_doacao': doacao.data_doacao.isoformat(),
                'item': {
                    'id': item.id,
                    'nome': item.nome,
                    'unidade_medida': item.unidade_medida
                }
            })
    
    # Ordenar por data de doação (mais recentes primeiro)
    doacoes.sort(key=lambda x: x['data_doacao'], reverse=True)
    
    return jsonify({
        'lista': lista.nome,
        'total_doacoes': len(doacoes),
        'doacoes': doacoes
    })

@api_bp.route('/unidades', methods=['GET'])
def listar_unidades():
    """Listar todas as unidades organizadoras"""
    unidades = UnidadeOrganizadora.query.all()
    
    return jsonify({
        'unidades': [{
            'id': unidade.id,
            'nome': unidade.nome,
            'responsavel': unidade.responsavel,
            'email': unidade.email,
            'total_listas': len(unidade.listas)
        } for unidade in unidades]
    })

@api_bp.route('/unidades/<int:unidade_id>/listas', methods=['GET'])
def listar_listas_unidade(unidade_id):
    """Listar listas de uma unidade específica"""
    unidade = UnidadeOrganizadora.query.get(unidade_id)
    
    if not unidade:
        return jsonify({'error': 'Unidade não encontrada'}), 404
    
    return jsonify({
        'unidade': {
            'id': unidade.id,
            'nome': unidade.nome,
            'responsavel': unidade.responsavel
        },
        'listas': [{
            'id': lista.id,
            'nome': lista.nome,
            'slug': lista.slug,
            'modo': lista.modo,
            'ativa': lista.ativa,
            'percentual_conclusao': lista.percentual_conclusao,
            'total_itens': lista.total_itens,
            'total_arrecadado': lista.total_arrecadado,
            'data_criacao': lista.data_criacao.isoformat()
        } for lista in unidade.listas]
    }) 