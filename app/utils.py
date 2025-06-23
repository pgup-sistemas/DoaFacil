import csv
import io
from datetime import datetime
from weasyprint import HTML
from flask import render_template, current_app
from app.models import Lista, Item, Doacao

def export_lista_csv(lista):
    """Exporta uma lista para CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow(['Lista de Arrecadação - CSV'])
    writer.writerow([f'Nome: {lista.nome}'])
    writer.writerow([f'Unidade: {lista.unidade.nome}'])
    writer.writerow([f'Data de Criação: {lista.data_criacao.strftime("%d/%m/%Y %H:%M")}'])
    writer.writerow([f'Modo: {lista.modo.title()}'])
    writer.writerow([''])
    
    # Cabeçalho dos itens
    writer.writerow(['Item', 'Quantidade Necessária', 'Quantidade Arrecadada', 'Restante', 'Percentual', 'Doadores'])
    
    # Dados dos itens
    for item in lista.itens:
        doadores = ', '.join([d.doador_nome for d in item.doacoes])
        writer.writerow([
            item.nome,
            f"{item.quantidade_necessaria} {item.unidade_medida}",
            f"{item.quantidade_arrecadada} {item.unidade_medida}",
            f"{item.quantidade_restante} {item.unidade_medida}",
            f"{item.percentual_conclusao:.1f}%",
            doadores
        ])
    
    # Resumo
    writer.writerow([''])
    writer.writerow(['RESUMO'])
    writer.writerow([f'Total de Itens: {len(lista.itens)}'])
    writer.writerow([f'Total Arrecadado: {lista.total_arrecadado}'])
    writer.writerow([f'Percentual Geral: {lista.percentual_conclusao:.1f}%'])
    
    return output.getvalue()

def export_lista_pdf(lista):
    """Exporta uma lista para PDF"""
    # Renderizar template HTML
    html_content = render_template('export/pdf_lista.html', lista=lista)
    
    # Gerar PDF
    pdf = HTML(string=html_content).write_pdf()
    return pdf

def format_currency(value):
    """Formata valor como moeda brasileira"""
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def get_progress_color(percentual):
    """Retorna a cor baseada no percentual de conclusão"""
    if percentual >= 100:
        return 'is-success'
    elif percentual >= 75:
        return 'is-warning'
    elif percentual >= 50:
        return 'is-info'
    else:
        return 'is-danger'

def send_notification_email(lista, doacao):
    """Envia e-mail de notificação para o administrador"""
    try:
        from flask_mail import Message
        from app import mail
        
        if not lista.unidade.email:
            return False
            
        msg = Message(
            f'Nova doação na lista "{lista.nome}"',
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[lista.unidade.email]
        )
        
        msg.body = f"""
        Nova doação registrada!
        
        Lista: {lista.nome}
        Doador: {doacao.doador_nome}
        Item: {doacao.item.nome}
        Quantidade: {doacao.quantidade} {doacao.item.unidade_medida}
        Data: {doacao.data_doacao.strftime("%d/%m/%Y %H:%M")}
        
        Acesse o dashboard para mais detalhes.
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

def generate_whatsapp_share_url(lista):
    """Gera URL para compartilhamento via WhatsApp"""
    url = f"https://wa.me/?text=Ajude%20nossa%20arrecadação!%20{lista.nome}%20-%20"
    return url 