# 🎯 DoaFácil - Sistema de Arrecadações

Sistema completo para arrecadações e doações desenvolvido com Flask e Bulma CSS. Permite que organizações criem listas de arrecadação, gerenciem doações e acompanhem o progresso em tempo real.

## ✨ Funcionalidades

- **Sistema de Autenticação** para administradores
- **Cadastro de Unidades Organizadoras** (igrejas, ONGs, grupos comunitários) - **RESTRITO A ADMIN**
- **Criação de Listas de Arrecadação** com itens e quantidades - **RESTRITO A ADMIN**
- **Doações via Interface Web** com modal responsivo - **ACESSO PÚBLICO**
- **Integração PIX** para doações financeiras
- **Dashboard Administrativo** com estatísticas e controles
- **Exportação de Relatórios** em CSV e PDF
- **API REST** para integração com outros sistemas
- **Interface Responsiva** otimizada para mobile
- **Notificações por E-mail** para novas doações

## 🚀 Instalação

### Pré-requisitos

- Python 3.8+
- pip

### Passos

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

5. **Crie um administrador inicial**
```bash
python create_admin.py
```

6. **Execute a aplicação**
```bash
python run.py
```

A aplicação estará disponível em `http://localhost:5000`

## 📁 Estrutura do Projeto

```
listArrecadacao/
├── app/
│   ├── __init__.py          # Configuração da aplicação Flask
│   ├── models.py            # Modelos do banco de dados
│   ├── forms.py             # Formulários WTForms
│   ├── routes.py            # Rotas principais
│   ├── api.py               # API REST
│   ├── utils.py             # Utilitários (exportação, notificações)
│   └── templates/           # Templates HTML
│       ├── base.html
│       ├── index.html
│       ├── admin/
│       │   ├── login.html
│       │   └── dashboard.html
│       ├── cadastrar_unidade.html
│       ├── criar_lista.html
│       ├── adicionar_itens.html
│       ├── visualizar_lista.html
│       ├── dashboard.html
│       ├── editar_lista.html
│       └── export/
│           └── pdf_lista.html
├── config.py                # Configurações
├── run.py                   # Arquivo de execução
├── create_admin.py          # Script para criar administrador
├── requirements.txt         # Dependências Python
└── README.md               # Este arquivo
```

## 🎯 Como Usar

### 1. Acesso Administrativo
- Acesse `/admin/login`
- Use as credenciais criadas pelo script `create_admin.py`
- **Credenciais padrão**: admin / admin123

### 2. Cadastrar Unidade Organizadora (ADMIN)
- Após fazer login, acesse o dashboard administrativo
- Clique em "Nova Unidade"
- Preencha nome, responsável e e-mail
- Clique em "Cadastrar Unidade"

### 3. Criar Lista de Arrecadação (ADMIN)
- No dashboard, clique em "Nova Lista" na unidade desejada
- Defina nome, descrição e modo (fechado/aberto)
- Configure PIX se desejar aceitar doações financeiras

### 4. Adicionar Itens (ADMIN)
- Adicione os itens necessários com quantidades
- Defina unidade de medida (kg, unidades, litros, etc.)

### 5. Compartilhar e Gerenciar (ADMIN)
- Use o link público para compartilhar a lista
- Acesse o dashboard administrativo para acompanhar o progresso
- Exporte relatórios em CSV ou PDF

### 6. Doações (PÚBLICO)
- Qualquer pessoa pode acessar o link público da lista
- Escolha os itens que deseja doar
- Preencha nome e quantidade
- Confirme a doação

## 🔐 Regras de Acesso

### Área Administrativa (RESTRITA)
- **Login**: `/admin/login`
- **Dashboard**: `/admin/dashboard`
- **Cadastro de Unidades**: `/unidade/cadastrar`
- **Criação de Listas**: `/lista/criar/<unidade_id>`
- **Adição de Itens**: `/lista/<lista_id>/itens`

### Área Pública (LIVRE)
- **Visualização de Lista**: `/lista/<slug>`
- **Doações**: `/lista/<slug>/doar`
- **Exportação**: `/exportar/<slug>.csv` e `/exportar/<slug>.pdf`
- **API**: `/api/listas/<slug>` e `/api/listas/<slug>/doacoes`

### Dashboard de Lista (VIA TOKEN)
- **Dashboard**: `/admin/<token>`
- **Edição**: `/admin/<token>/editar`

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sqlite:///arrecadador.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app
```

### Banco de Dados

O sistema usa SQLite por padrão. Para produção, configure PostgreSQL:

```env
DATABASE_URL=postgresql://usuario:senha@localhost/doafacil
```

### Criar Administrador

Execute o script para criar um administrador inicial:

```bash
python create_admin.py
```

**Credenciais padrão:**
- Usuário: `admin`
- Senha: `admin123`

⚠️ **IMPORTANTE**: Altere a senha após o primeiro login!

## 📱 API REST

### Endpoints Disponíveis

- `GET /api/listas/<slug>` - Obter informações de uma lista
- `POST /api/listas/<slug>/doacoes` - Criar nova doação
- `GET /api/listas/<slug>/doacoes` - Listar doações de uma lista
- `GET /api/unidades` - Listar todas as unidades
- `GET /api/unidades/<id>/listas` - Listar listas de uma unidade

### Exemplo de Uso

```bash
# Obter status de uma lista
curl http://localhost:5000/api/listas/ABC12345

# Criar doação via API
curl -X POST http://localhost:5000/api/listas/ABC12345/doacoes \
  -H "Content-Type: application/json" \
  -d '{"item_id": 1, "doador_nome": "João Silva", "quantidade": 5}'
```

## 🎨 Tecnologias Utilizadas

- **Backend**: Flask, SQLAlchemy, WTForms
- **Frontend**: Bulma CSS, Font Awesome, JavaScript
- **Banco de Dados**: SQLite (dev) / PostgreSQL (prod)
- **Exportação**: WeasyPrint (PDF), CSV nativo
- **E-mail**: Flask-Mail
- **API**: Flask-RESTful
- **Autenticação**: Session-based

## 🔒 Segurança

- **Autenticação de administradores** com senhas criptografadas
- **Proteção de rotas** com decorators
- **Tokens únicos** para acesso administrativo às listas
- **Validação de formulários** com WTForms
- **Proteção CSRF**
- **Validação de quantidades** de doação
- **Sanitização de dados**

## 📊 Funcionalidades Avançadas

### Modo de Lista
- **Fechado**: Administrador define todos os itens
- **Aberto**: Doadores podem sugerir itens adicionais

### Progresso em Tempo Real
- Barras de progresso coloridas
- Percentuais de conclusão
- Status visual dos itens

### Notificações
- E-mail automático para novas doações
- Configurável por unidade organizadora

### Exportação
- **CSV**: Dados estruturados para planilhas
- **PDF**: Relatório formatado para impressão

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Entre em contato através do e-mail de suporte

---

**DoaFácil** - Facilitando a solidariedade em sua comunidade! ❤️ 