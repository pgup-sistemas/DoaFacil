from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_restful import Api
from config import Config

db = SQLAlchemy()
mail = Mail()
api = Api()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensões
    db.init_app(app)
    mail.init_app(app)
    api.init_app(app)
    
    # Registrar blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Registrar API routes
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Registrar funções utilitárias no contexto do Jinja2
    from app.utils import (
        generate_whatsapp_share_url_with_unidade,
        generate_facebook_share_url_with_unidade,
        get_unidade_social_links
    )
    
    app.jinja_env.globals.update({
        'generate_whatsapp_share_url_with_unidade': generate_whatsapp_share_url_with_unidade,
        'generate_facebook_share_url_with_unidade': generate_facebook_share_url_with_unidade,
        'get_unidade_social_links': get_unidade_social_links
    })
    
    # Criar tabelas
    with app.app_context():
        db.create_all()
    
    return app 