# 🚀 **Guia de Deploy e Configuração - DoaFácil**

## 📋 **Pré-requisitos**

### Servidor
- **Sistema Operacional**: Ubuntu 20.04+ ou CentOS 8+
- **RAM**: Mínimo 2GB (recomendado 4GB+)
- **CPU**: 2 cores (recomendado 4+)
- **Disco**: 20GB+ de espaço livre
- **Rede**: Acesso à internet para instalação de dependências

### Software Necessário
- **Python**: 3.8+ (recomendado 3.10+)
- **PostgreSQL**: 12+ (para produção)
- **Nginx**: 1.18+ (proxy reverso)
- **Redis**: 6+ (opcional, para cache)
- **Git**: Para deploy via repositório

---

## 🔧 **Instalação do Ambiente**

### 1. **Atualizar o Sistema**
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. **Instalar Python e Dependências**
```bash
sudo apt install python3 python3-pip python3-venv python3-dev -y
sudo apt install build-essential libpq-dev libssl-dev libffi-dev -y
```

### 3. **Instalar PostgreSQL**
```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 4. **Configurar PostgreSQL**
```bash
sudo -u postgres psql
CREATE DATABASE doafacil;
CREATE USER doafacil_user WITH PASSWORD 'sua_senha_segura';
GRANT ALL PRIVILEGES ON DATABASE doafacil TO doafacil_user;
\q
```

### 5. **Instalar Nginx**
```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 6. **Instalar Redis (Opcional)**
```bash
sudo apt install redis-server -y
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

---

## 📁 **Deploy da Aplicação**

### 1. **Criar Usuário da Aplicação**
```bash
sudo adduser doafacil
sudo usermod -aG sudo doafacil
```

### 2. **Clonar o Repositório**
```bash
sudo -u doafacil git clone https://github.com/seu-usuario/doafacil.git /home/doafacil/app
cd /home/doafacil/app
```

### 3. **Configurar Ambiente Virtual**
```bash
sudo -u doafacil python3 -m venv venv
sudo -u doafacil /home/doafacil/app/venv/bin/pip install --upgrade pip
sudo -u doafacil /home/doafacil/app/venv/bin/pip install -r requirements.txt
```

### 4. **Instalar Gunicorn**
```bash
sudo -u doafacil /home/doafacil/app/venv/bin/pip install gunicorn
```

---

## ⚙️ **Configuração da Aplicação**

### 1. **Criar Arquivo de Configuração**
```bash
sudo nano /home/doafacil/app/.env
```

**Conteúdo do arquivo .env:**
```env
# Configurações Básicas
FLASK_ENV=production
DEBUG=False
SECRET_KEY=sua-chave-super-secreta-e-complexa-aqui

# Banco de Dados
DATABASE_URL=postgresql://doafacil_user:sua_senha_segura@localhost/doafacil

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=seu-email@gmail.com
MAIL_PASSWORD=sua-senha-de-app-gmail

# Configurações Opcionais
FLASK_APP=run.py
FLASK_DEBUG=0
```

### 2. **Configurar Permissões**
```bash
sudo chown -R doafacil:doafacil /home/doafacil/app
sudo chmod -R 755 /home/doafacil/app
```

### 3. **Executar Migrações**
```bash
cd /home/doafacil/app
sudo -u doafacil /home/doafacil/app/venv/bin/python migrate_admin.py
sudo -u doafacil /home/doafacil/app/venv/bin/python migrate_doacao_financeira.py
sudo -u doafacil /home/doafacil/app/venv/bin/python migrate_doador.py
sudo -u doafacil /home/doafacil/app/venv/bin/python migrate_unidade_completa.py
sudo -u doafacil /home/doafacil/app/venv/bin/python migrate_sugestoes.py
```

### 4. **Criar Administrador Inicial**
```bash
sudo -u doafacil /home/doafacil/app/venv/bin/python create_admin.py
```

---

## 🐳 **Configuração do Gunicorn**

### 1. **Criar Arquivo de Configuração do Gunicorn**
```bash
sudo nano /home/doafacil/app/gunicorn.conf.py
```

**Conteúdo:**
```python
# Gunicorn configuration file
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
user = "doafacil"
group = "doafacil"
pidfile = "/home/doafacil/app/gunicorn.pid"
accesslog = "/home/doafacil/app/logs/access.log"
errorlog = "/home/doafacil/app/logs/error.log"
loglevel = "info"
```

### 2. **Criar Diretório de Logs**
```bash
sudo -u doafacil mkdir -p /home/doafacil/app/logs
```

### 3. **Criar Service do Systemd**
```bash
sudo nano /etc/systemd/system/doafacil.service
```

**Conteúdo:**
```ini
[Unit]
Description=DoaFácil Gunicorn daemon
After=network.target

[Service]
User=doafacil
Group=doafacil
WorkingDirectory=/home/doafacil/app
Environment="PATH=/home/doafacil/app/venv/bin"
ExecStart=/home/doafacil/app/venv/bin/gunicorn --config gunicorn.conf.py run:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 4. **Ativar e Iniciar o Service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable doafacil
sudo systemctl start doafacil
sudo systemctl status doafacil
```

---

## 🌐 **Configuração do Nginx**

### 1. **Criar Configuração do Site**
```bash
sudo nano /etc/nginx/sites-available/doafacil
```

**Conteúdo:**
```nginx
server {
    listen 80;
    server_name seu-dominio.com www.seu-dominio.com;

    # Redirecionar para HTTPS (descomente após configurar SSL)
    # return 301 https://$server_name$request_uri;

    # Logs
    access_log /var/log/nginx/doafacil_access.log;
    error_log /var/log/nginx/doafacil_error.log;

    # Configurações de segurança
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Proxy para Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Servir arquivos estáticos (se houver)
    location /static/ {
        alias /home/doafacil/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Configurações de upload (para arquivos grandes)
    client_max_body_size 10M;
}
```

### 2. **Ativar o Site**
```bash
sudo ln -s /etc/nginx/sites-available/doafacil /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔒 **Configuração SSL (HTTPS)**

### 1. **Instalar Certbot**
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 2. **Obter Certificado SSL**
```bash
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

### 3. **Renovação Automática**
```bash
sudo crontab -e
# Adicionar linha:
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 **Monitoramento e Logs**

### 1. **Configurar Logrotate**
```bash
sudo nano /etc/logrotate.d/doafacil
```

**Conteúdo:**
```
/home/doafacil/app/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 doafacil doafacil
    postrotate
        systemctl reload doafacil
    endscript
}
```

### 2. **Monitoramento Básico**
```bash
# Verificar status dos serviços
sudo systemctl status doafacil nginx postgresql

# Verificar logs
sudo journalctl -u doafacil -f
sudo tail -f /home/doafacil/app/logs/error.log

# Verificar uso de recursos
htop
df -h
free -h
```

---

## 🔄 **Deploy Automático**

### 1. **Script de Deploy**
```bash
sudo nano /home/doafacil/deploy.sh
```

**Conteúdo:**
```bash
#!/bin/bash
cd /home/doafacil/app

# Backup do banco
pg_dump doafacil > backup_$(date +%Y%m%d_%H%M%S).sql

# Pull das alterações
git pull origin main

# Atualizar dependências
source venv/bin/activate
pip install -r requirements.txt

# Executar migrações
python migrate_admin.py
python migrate_doacao_financeira.py
python migrate_doador.py
python migrate_unidade_completa.py
python migrate_sugestoes.py

# Reiniciar aplicação
sudo systemctl restart doafacil

echo "Deploy concluído!"
```

### 2. **Tornar Executável**
```bash
sudo chmod +x /home/doafacil/deploy.sh
```

---

## 🛡️ **Segurança**

### 1. **Configurar Firewall**
```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. **Configurar Fail2ban**
```bash
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. **Configurações de Segurança do PostgreSQL**
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
# Adicionar/modificar:
listen_addresses = 'localhost'
max_connections = 100
```

```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
# Garantir que apenas conexões locais são permitidas
```

---

## 📈 **Otimização de Performance**

### 1. **Configurações do PostgreSQL**
```sql
-- Conectar como postgres
sudo -u postgres psql

-- Configurações de performance
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reiniciar PostgreSQL
SELECT pg_reload_conf();
```

### 2. **Configurações do Nginx**
```nginx
# Adicionar ao arquivo de configuração do site
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
```

### 3. **Cache com Redis (Opcional)**
```bash
# Instalar redis-py
sudo -u doafacil /home/doafacil/app/venv/bin/pip install redis

# Configurar no código da aplicação
```

---

## 🔧 **Manutenção**

### 1. **Backup Automático**
```bash
sudo nano /home/doafacil/backup.sh
```

**Conteúdo:**
```bash
#!/bin/bash
BACKUP_DIR="/home/doafacil/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco
pg_dump doafacil > $BACKUP_DIR/doafacil_$DATE.sql

# Backup dos arquivos de configuração
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /home/doafacil/app/.env

# Manter apenas os últimos 7 backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup concluído: $DATE"
```

### 2. **Cron para Backup Diário**
```bash
sudo crontab -e
# Adicionar linha:
0 2 * * * /home/doafacil/backup.sh
```

### 3. **Monitoramento de Espaço**
```bash
sudo crontab -e
# Adicionar linha:
0 8 * * * df -h | awk '$5 > "80%" {print $0}' | mail -s "Alerta de Disco" admin@seu-dominio.com
```

---

## 🚨 **Troubleshooting**

### Problemas Comuns

#### 1. **Aplicação não inicia**
```bash
# Verificar logs
sudo journalctl -u doafacil -f

# Verificar permissões
sudo chown -R doafacil:doafacil /home/doafacil/app

# Verificar configuração
sudo -u doafacil /home/doafacil/app/venv/bin/python -c "import config; print('OK')"
```

#### 2. **Erro de conexão com banco**
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Testar conexão
sudo -u doafacil psql -h localhost -U doafacil_user -d doafacil
```

#### 3. **Erro 502 Bad Gateway**
```bash
# Verificar se Gunicorn está rodando
sudo systemctl status doafacil

# Verificar porta
sudo netstat -tlnp | grep 8000

# Reiniciar serviços
sudo systemctl restart doafacil nginx
```

#### 4. **Problemas de SSL**
```bash
# Verificar certificado
sudo certbot certificates

# Renovar manualmente
sudo certbot renew --dry-run
```

---

## 📞 **Suporte**

### Contatos
- **Desenvolvedor**: Oézios Normando
- **Empresa**: PageUp Sistemas
- **Email**: contato@pageup.com.br

### Logs Importantes
- **Aplicação**: `/home/doafacil/app/logs/`
- **Nginx**: `/var/log/nginx/`
- **Systemd**: `sudo journalctl -u doafacil`
- **PostgreSQL**: `/var/log/postgresql/`

### Comandos Úteis
```bash
# Reiniciar todos os serviços
sudo systemctl restart doafacil nginx postgresql

# Verificar status
sudo systemctl status doafacil nginx postgresql

# Ver logs em tempo real
sudo tail -f /home/doafacil/app/logs/error.log

# Backup manual
/home/doafacil/backup.sh

# Deploy manual
/home/doafacil/deploy.sh
```

---

**DoaFácil** - Sistema profissional em produção! 🚀✨ 