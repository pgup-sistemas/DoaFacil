#!/usr/bin/env python3
"""
Script para testar o login do administrador
"""

from app import create_app, db
from app.models import Administrador

def test_admin_login():
    app = create_app()
    
    with app.app_context():
        # Verificar se o administrador existe
        admin = Administrador.query.filter_by(username='admin').first()
        
        if not admin:
            print("❌ Administrador 'admin' não encontrado!")
            return
        
        print(f"✅ Administrador encontrado:")
        print(f"   Usuário: {admin.username}")
        print(f"   Nome: {admin.nome}")
        print(f"   E-mail: {admin.email}")
        print(f"   Ativo: {admin.ativo}")
        
        # Testar senha
        senha_teste = 'admin123'
        if admin.check_password(senha_teste):
            print(f"✅ Senha '{senha_teste}' está correta!")
        else:
            print(f"❌ Senha '{senha_teste}' está incorreta!")
            
        # Listar todos os administradores
        print("\n📋 Todos os administradores:")
        admins = Administrador.query.all()
        for a in admins:
            print(f"   - {a.username} ({a.nome}) - Ativo: {a.ativo}")

if __name__ == '__main__':
    test_admin_login() 