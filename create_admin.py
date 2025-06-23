#!/usr/bin/env python3
"""
Script para criar um administrador inicial no sistema DoaFácil
"""

from app import create_app, db
from app.models import Administrador

def create_admin():
    app = create_app()
    
    with app.app_context():
        # Verificar se já existe um administrador
        admin = Administrador.query.filter_by(username='admin').first()
        
        if admin:
            print("Administrador 'admin' já existe!")
            return
        
        # Criar novo administrador
        admin = Administrador(
            username='admin',
            email='admin@doafacil.com',
            nome='Administrador Principal',
            ativo=True
        )
        admin.set_password('admin123')
        
        db.session.add(admin)
        db.session.commit()
        
        print("✅ Administrador criado com sucesso!")
        print("👤 Usuário: admin")
        print("🔑 Senha: admin123")
        print("⚠️  IMPORTANTE: Altere a senha após o primeiro login!")

if __name__ == '__main__':
    create_admin() 