# �� DoaFácil - Sistema Completo de Arrecadações

Sistema profissional para arrecadações e doações desenvolvido com Flask e Bulma CSS. Permite que organizações criem listas de arrecadação, gerenciem doações e acompanhem o progresso em tempo real com interface moderna e funcionalidades avançadas.

## ✨ Funcionalidades Principais

### 🔐 **Sistema de Autenticação Avançado**
- **Multi-nível de acesso**: Administrador Principal e Administrador de Unidade
- **Sessões seguras** com controle de permissões
- **Gerenciamento completo de usuários** (criar, editar, ativar/desativar)
- **Controle de senhas** e perfis de acesso

### 🏢 **Gerenciamento de Unidades Organizadoras**
- **Cadastro completo** com dados legais (CNPJ, razão social, nome fantasia)
- **Endereço completo** com consulta automática de CEP via ViaCEP
- **Contatos múltiplos** (email principal/secundário, telefone, WhatsApp)
- **Presença digital** (website, Facebook, Instagram, LinkedIn, YouTube)
- **Dados para relatórios** (categoria, público-alvo, área de atuação)
- **Coordenadas geográficas** para integração com mapas

### 📋 **Sistema de Listas de Arrecadação**
- **Modo aberto/fechado** para sugestões de itens
- **Configuração PIX** com geração automática de QR Code
- **Links únicos** para compartilhamento público
- **Tokens administrativos** para acesso seguro
- **Sistema de sugestões** para listas abertas
- **Aprovação/rejeição** de sugestões da comunidade

### 🎁 **Sistema de Doações Avançado**
- **Doações físicas** com controle de quantidades
- **Doações financeiras** via PIX com QR Code
- **Busca inteligente** de doadores por CPF, email ou telefone
- **Validação completa** de dados
- **Sistema de endereços** para doadores
- **Observações personalizadas**

### 📊 **Dashboard Administrativo Profissional**
- **Interface moderna** com design responsivo
- **Estatísticas em tempo real** com cards informativos
- **Paginação completa** em todas as listas
- **Filtros avançados** por categoria, estado, tipo e status
- **Ações rápidas** para acesso direto às funcionalidades
- **Navegação intuitiva** com breadcrumbs e menus

### 🔧 **Sistema de Sugestões**
- **Sugestões de itens** para listas abertas
- **Interface de gerenciamento** com paginação
- **Aprovação/rejeição** com notificações
- **Histórico completo** de sugestões

### 📤 **Exportação e Relatórios**
- **Múltiplos formatos**: CSV, PDF e Excel
- **Relatórios profissionais** com dados completos
- **Exportação de unidades** com todas as informações
- **Templates personalizados** para diferentes necessidades

### 🌐 **API REST Completa**
- **Endpoints para listas** (status, doações, criação)
- **Endpoints para unidades** (listagem, detalhes)
- **Consulta de CEP** via ViaCEP
- **Geração de QR Code PIX**
- **Busca de doadores** por identificadores

### 📧 **Sistema de Notificações**
- **Notificações por email** para novas doações
- **Configuração SMTP** flexível
- **Templates de email** personalizáveis
- **Notificações toast** na interface

### 🎨 **Interface Moderna e Responsiva**
- **Design Bulma CSS** com componentes modernos
- **Responsivo** para todos os dispositivos
- **Animações suaves** e transições
- **Ícones FontAwesome** para melhor UX
- **Temas consistentes** em todo o sistema

## 🚀 Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- pip
- Git

### Passos de Instalação

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd listArrecadacao
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente** (opcional)
```bash
# Crie um arquivo .env na raiz do projeto
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sqlite:///arrecadador.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app
```

5. **Execute as migrações do banco** (se necessário)
```bash
python migrate_admin.py
python migrate_doacao_financeira.py
python migrate_doador.py
python migrate_unidade_completa.py
python migrate_sugestoes.py
```

6. **Crie um administrador inicial**
```bash
python create_admin.py
```

7. **Execute a aplicação**
```bash
python run.py
```

A aplicação estará disponível em `http://localhost:5000`

## 📁 Estrutura do Projeto

```
listArrecadacao/
├── app/
│   ├── __init__.py              # Configuração da aplicação Flask
│   ├── models.py                # Modelos do banco de dados
│   ├── forms.py                 # Formulários WTForms
│   ├── routes.py                # Rotas principais
│   ├── api.py                   # API REST
│   ├── utils.py                 # Utilitários (exportação, notificações, CEP)
│   └── templates/               # Templates HTML
│       ├── base.html            # Template base
│       ├── index.html           # Página inicial
│       ├── admin/               # Área administrativa
│       │   ├── login.html       # Login
│       │   ├── dashboard.html   # Dashboard principal
│       │   ├── usuarios.html    # Gerenciar usuários
│       │   ├── criar_usuario.html
│       │   ├── editar_usuario.html
│       │   ├── listas_ativas.html
│       │   ├── listas_concluidas.html
│       │   └── listas_unidade.html
│       ├── cadastrar_unidade.html
│       ├── editar_unidade.html
│       ├── criar_lista.html
│       ├── editar_lista.html
│       ├── adicionar_itens.html
│       ├── adicionar_itens_lista.html
│       ├── editar_item.html
│       ├── visualizar_lista.html
│       ├── doar_pagina.html
│       ├── agradecimento_doacao.html
│       ├── dashboard.html
│       ├── gerenciar_sugestoes.html
│       └── export/
│           └── pdf_lista.html
├── config.py                    # Configurações
├── run.py                       # Arquivo de execução
├── create_admin.py              # Script para criar administrador
├── create_test_data.py          # Script para criar dados de teste
├── requirements.txt             # Dependências Python
└── README.md                    # Este arquivo
```

## 🎯 Como Usar

### 1. Acesso Administrativo
- Acesse `/admin/login`
- Use as credenciais criadas pelo script `create_admin.py`
- **Credenciais padrão**: admin / admin123

### 2. Gerenciar Usuários (ADMIN PRINCIPAL)
- Após fazer login como admin principal, acesse "Usuários" no navbar
- Clique em "Novo Usuário" para criar administradores de unidade
- Edite usuários existentes para modificar dados, senhas ou status
- Defina o tipo de acesso (Principal ou Unidade)

### 3. Cadastrar Unidade Organizadora
- Após fazer login, acesse o dashboard administrativo
- Clique em "Nova Unidade" ou use as ações rápidas
- Preencha todos os dados (básicos, legais, endereço, contatos, presença digital)
- **Admin de Unidade**: A unidade será automaticamente associada ao seu usuário
- **Admin Principal**: Pode criar unidades para qualquer admin de unidade

### 4. Criar Lista de Arrecadação
- No dashboard, clique em "Nova Lista" na unidade desejada
- Defina nome, descrição e modo (fechado/aberto)
- Configure PIX se desejar aceitar doações financeiras
- **Restrição**: Apenas admin da unidade ou admin principal pode criar listas

### 5. Adicionar Itens
- Adicione os itens necessários com quantidades
- Defina unidade de medida (kg, unidades, litros, etc.)
- **Restrição**: Apenas admin da lista pode adicionar itens

### 6. Gerenciar Sugestões (Listas Abertas)
- Para listas em modo aberto, gerencie sugestões da comunidade
- Aprove ou rejeite sugestões de itens
- Acesse via dashboard da lista ou link direto

### 7. Compartilhar e Gerenciar
- Use o link público para compartilhar a lista
- Acesse o dashboard administrativo para acompanhar o progresso
- Exporte relatórios em CSV, PDF ou Excel

### 8. Doações (PÚBLICO)
- Qualquer pessoa pode acessar o link público da lista
- Escolha os itens que deseja doar
- Preencha dados pessoais e endereço
- Confirme a doação (física ou PIX)

## 🔐 Regras de Acesso

### Área Administrativa (RESTRITA)
- **Login**: `/admin/login`
- **Dashboard**: `/admin/dashboard`
- **Gerenciar Usuários**: `/admin/usuarios` (apenas admin principal)
- **Criar Usuário**: `/admin/usuario/criar` (apenas admin principal)
- **Editar Usuário**: `/admin/usuario/<id>/editar` (apenas admin principal)
- **Cadastro de Unidades**: `/unidade/cadastrar`
- **Criação de Listas**: `/lista/criar/<unidade_id>` (apenas admin da unidade)
- **Adição de Itens**: `/lista/<lista_id>/itens` (apenas admin da lista)
- **Gerenciar Sugestões**: `/admin/<token>/sugestoes` (apenas admin da lista)

### Área Pública (LIVRE)
- **Visualização de Lista**: `/lista/<slug>`
- **Doações**: `/lista/<slug>/doar`
- **Sugestões**: `/lista/<slug>/sugerir` (apenas listas abertas)
- **Exportação**: `/exportar/<slug>.csv`, `/exportar/<slug>.pdf`, `/exportar/<slug>.xlsx`
- **API**: `/api/listas/<slug>`, `/api/listas/<slug>/doacoes`

### Dashboard de Lista (VIA TOKEN)
- **Dashboard**: `/admin/<token>`
- **Edição**: `/admin/<token>/editar`
- **Adicionar Itens**: `/admin/<token>/adicionar-itens`
- **Gerenciar Sugestões**: `/admin/<token>/sugestoes`

## 🔧 Configuração Avançada

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Configurações básicas
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sqlite:///arrecadador.db

# Configurações de email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app

# Configurações opcionais
DEBUG=True
FLASK_ENV=development
```

### Banco de Dados

O sistema usa SQLite por padrão. Para produção, configure PostgreSQL:

```env
DATABASE_URL=postgresql://usuario:senha@localhost/doafacil
```

### Configuração de Email

Para notificações funcionarem, configure um servidor SMTP:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app
```

### Criar Administrador

Execute o script para criar um administrador inicial:

```bash
python create_admin.py
```

### Dados de Teste

Para testar o sistema com dados de exemplo:

```bash
python create_test_data.py
```

## 🌐 API REST

### Endpoints Disponíveis

#### Listas
- `GET /api/listas/<slug>` - Obter dados da lista
- `POST /api/listas/<slug>/doacoes` - Criar doação
- `GET /api/listas/<slug>/doacoes` - Listar doações

#### Unidades
- `GET /api/unidades` - Listar unidades
- `GET /api/unidades/<id>/listas` - Listar listas da unidade

#### Utilitários
- `GET /api/consultar-cep/<cep>` - Consultar CEP
- `POST /api/gerar-qrcode-pix` - Gerar QR Code PIX
- `GET /api/buscar-doador/<identificador>` - Buscar doador

## 📊 Funcionalidades Avançadas

### Sistema de Paginação
- **Dashboard principal**: 10 unidades por página
- **Listas de unidade**: 15 listas por página
- **Sugestões**: 12 sugestões por página
- **Listas ativas/concluídas**: 10 listas por página
- **Usuários**: 15 usuários por página

### Filtros Avançados
- **Por categoria**: Religiosa, Social, Educacional, etc.
- **Por estado**: Todos os estados brasileiros
- **Por tipo**: Igreja, ONG, Associação, etc.
- **Por status**: Ativa, Concluída, Cancelada

### Exportação de Dados
- **CSV**: Para análise em planilhas
- **PDF**: Para relatórios formais
- **Excel**: Para relatórios completos com formatação

### Integração PIX
- **Geração automática** de QR Code
- **Validação de chaves** PIX
- **Interface intuitiva** para configuração

## 🎨 Interface e UX

### Design Responsivo
- **Mobile-first** com Bulma CSS
- **Adaptável** para todos os dispositivos
- **Navegação intuitiva** com menus e breadcrumbs

### Componentes Modernos
- **Cards informativos** com estatísticas
- **Barras de progresso** visuais
- **Tags coloridas** para status
- **Botões com ícones** para melhor UX

### Animações e Transições
- **Hover effects** em cards e botões
- **Transições suaves** entre páginas
- **Notificações toast** para feedback

## 🔒 Segurança

### Autenticação
- **Sessões seguras** com Flask-Session
- **Verificação de permissões** em todas as rotas
- **Controle de acesso** por tipo de usuário

### Validação de Dados
- **WTForms** para validação de formulários
- **Sanitização** de dados de entrada
- **Proteção CSRF** em todos os formulários

### Tokens de Acesso
- **Tokens únicos** para dashboards de lista
- **Validação de permissões** por token
- **Expiração automática** de sessões

## 🚀 Deploy em Produção

### Configurações Recomendadas
- **WSGI Server**: Gunicorn ou uWSGI
- **Proxy Reverso**: Nginx
- **Banco de Dados**: PostgreSQL
- **Email**: Serviço SMTP confiável

### Variáveis de Ambiente de Produção
```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=chave-super-secreta-e-complexa
DATABASE_URL=postgresql://usuario:senha@localhost/doafacil
```

## 📞 Suporte

Para dúvidas, sugestões ou problemas:

- **Desenvolvedor**: Oézios Normando
- **Empresa**: PageUp Sistemas
- **Email**: contato@pageup.com.br

## 📄 Licença

Este projeto é desenvolvido por **PageUp Sistemas** e está disponível para uso comercial e não comercial.

---

**DoaFácil** - Transformando a forma como organizações gerenciam arrecadações e doações! 🎯✨ 