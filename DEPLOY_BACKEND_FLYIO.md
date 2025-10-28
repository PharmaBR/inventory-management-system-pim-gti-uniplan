# 🚀 Guia: Deploy do Backend FastAPI no Fly.io

## 📋 Passo a Passo Completo

### 1️⃣ Preparar o Backend

#### Verificar/Criar Dockerfile

Verifique se já existe `backend/Dockerfile`. Se não existir, crie:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements/prod.txt requirements.txt

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para SQLite (se usar)
RUN mkdir -p /data

# Expor porta
EXPOSE 8000

# Variável de ambiente
ENV PYTHONPATH=/app

# Comando de inicialização
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Verificar requirements/prod.txt

Certifique-se de que `backend/requirements/prod.txt` tem todas as dependências:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
aiosqlite==0.19.0
```

---

### 2️⃣ Instalar Fly.io CLI

```bash
# macOS (Homebrew)
brew install flyctl

# Ou script de instalação universal
curl -L https://fly.io/install.sh | sh

# Verificar instalação
flyctl version
```

---

### 3️⃣ Login no Fly.io

```bash
# Fazer login (abrirá o navegador)
flyctl auth login

# Verificar autenticação
flyctl auth whoami
```

---

### 4️⃣ Criar Aplicação no Fly.io

```bash
# Vá para o diretório do backend
cd /Users/pharmabio/code/github_speckit/teste_speckit/backend

# Inicializar aplicação Fly.io
flyctl launch

# Siga o assistente:
# - App name: inventory-backend (ou deixe gerar automático)
# - Region: escolha a mais próxima (ex: gru - São Paulo)
# - PostgreSQL database? No (usaremos SQLite inicialmente)
# - Redis? No
# - Deploy now? No (vamos configurar antes)
```

Isso criará um arquivo `fly.toml` no diretório do backend.

---

### 5️⃣ Configurar fly.toml

Edite o arquivo `backend/fly.toml` gerado:

```toml
app = "inventory-backend"
primary_region = "gru"

[build]
  dockerfile = "Dockerfile"

[env]
  ENVIRONMENT = "production"
  DEBUG = "false"
  APP_NAME = "Inventory Management System"
  APP_VERSION = "1.0.0"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

  [[http_service.checks]]
    grace_period = "10s"
    interval = "30s"
    method = "GET"
    timeout = "5s"
    path = "/health"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

---

### 6️⃣ Configurar Secrets (Variáveis de Ambiente)

```bash
# Defina as variáveis sensíveis como secrets
flyctl secrets set SECRET_KEY="seu-secret-key-super-seguro-aqui-min-32-chars"
flyctl secrets set DATABASE_URL="sqlite+aiosqlite:////data/app.db"
flyctl secrets set CORS_ORIGINS="https://inventory-frontend.vercel.app,http://localhost:3000"

# Para multi-tenancy (se necessário)
flyctl secrets set REDIS_URL="redis://localhost:6379/0"  # Opcional
```

Gerar SECRET_KEY seguro:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### 7️⃣ Configurar Volume Persistente (para SQLite)

Se usar SQLite, crie um volume para persistir o banco de dados:

```bash
# Criar volume
flyctl volumes create data --region gru --size 1

# Adicionar ao fly.toml (se não existir)
```

Adicione ao `fly.toml`:

```toml
[mounts]
  source = "data"
  destination = "/data"
```

---

### 8️⃣ Deploy da Aplicação

```bash
# Deploy inicial
flyctl deploy

# Acompanhe os logs durante o deploy
flyctl logs
```

O deploy pode levar 2-5 minutos. Após concluído, você verá a URL da aplicação.

---

### 9️⃣ Executar Migrações do Banco

```bash
# Conectar via SSH ao container
flyctl ssh console

# Dentro do container, execute as migrações
cd /app
alembic upgrade head

# Sair do container
exit
```

Ou crie um script de inicialização que rode as migrações automaticamente.

---

### 🔟 Testar a API

```bash
# Verificar status
flyctl status

# Ver URL da aplicação
flyctl info

# Testar health endpoint
curl https://inventory-backend.fly.dev/health

# Testar API docs
# Acesse: https://inventory-backend.fly.dev/docs
```

---

## 🔧 Configuração Avançada

### Adicionar PostgreSQL (Recomendado para Produção)

```bash
# Criar banco PostgreSQL
flyctl postgres create

# Conectar ao app
flyctl postgres attach <postgres-app-name>

# Isso define automaticamente DATABASE_URL
```

Atualizar `backend/requirements/prod.txt`:

```txt
# Adicionar
psycopg2-binary==2.9.9
```

Atualizar `DATABASE_URL`:

```bash
flyctl secrets set DATABASE_URL="postgresql+asyncpg://user:pass@host/db"
```

### Script de Inicialização com Migrações

Crie `backend/start.sh`:

```bash
#!/bin/bash
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Atualizar Dockerfile:

```dockerfile
# ...
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
```

---

## 📊 Monitoramento e Logs

### Ver Logs em Tempo Real

```bash
flyctl logs
```

### Ver Métricas

```bash
flyctl status
flyctl metrics
```

### Escalar Aplicação

```bash
# Aumentar memória
flyctl scale memory 512

# Adicionar mais instâncias
flyctl scale count 2
```

---

## 🔄 Workflow de Deploy

### Deploy Manual

```bash
cd backend
flyctl deploy
```

### Deploy Automático via GitHub Actions

Crie `.github/workflows/deploy-backend.yml`:

```yaml
name: Deploy Backend to Fly.io

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    name: Deploy app
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: superfly/flyctl-actions/setup-flyctl@master
      
      - run: flyctl deploy --remote-only
        working-directory: ./backend
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Configurar token:

```bash
# Criar token
flyctl auth token

# Adicionar ao GitHub:
# Settings > Secrets > Actions > New secret
# Name: FLY_API_TOKEN
# Value: <seu-token>
```

---

## 🐛 Troubleshooting

### Build Falha

```bash
# Ver logs detalhados
flyctl logs

# Testar build localmente
docker build -t test-backend -f backend/Dockerfile backend/
docker run -p 8000:8000 test-backend
```

### Aplicação Não Inicia

```bash
# Verificar logs
flyctl logs

# Conectar via SSH e investigar
flyctl ssh console
```

### Banco de Dados Não Persiste

- Certifique-se de que o volume está montado em `/data`
- Verifique `DATABASE_URL` aponta para `/data/app.db`

### CORS Errors

```bash
# Atualizar CORS_ORIGINS
flyctl secrets set CORS_ORIGINS="https://seu-frontend.vercel.app,http://localhost:3000"

# Redeploy
flyctl deploy
```

---

## 🔒 Segurança

### Variáveis de Ambiente Sensíveis

**NUNCA** commite secrets no código. Use `flyctl secrets`:

```bash
flyctl secrets list  # Ver secrets configurados
flyctl secrets set KEY=VALUE  # Adicionar/atualizar
flyctl secrets unset KEY  # Remover
```

### HTTPS

Fly.io fornece certificado SSL automaticamente. Force HTTPS no `fly.toml`:

```toml
[http_service]
  force_https = true
```

---

## 💰 Custos

### Plano Gratuito (Hobby)

- 3 VMs compartilhadas (256MB RAM)
- 160GB de transferência/mês
- Volume persistente de 3GB

Suficiente para MVP e testes!

### Monitorar Uso

```bash
flyctl dashboard
```

---

## 📚 Recursos Úteis

- [Fly.io Documentation](https://fly.io/docs/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/docker/)
- [Fly.io Python Guide](https://fly.io/docs/languages-and-frameworks/python/)

---

## ✅ Checklist Rápido

- [ ] Instalar Fly.io CLI
- [ ] Login no Fly.io
- [ ] Verificar/criar Dockerfile
- [ ] Executar `flyctl launch`
- [ ] Configurar `fly.toml`
- [ ] Definir secrets (SECRET_KEY, DATABASE_URL, CORS_ORIGINS)
- [ ] Criar volume para SQLite (se aplicável)
- [ ] Deploy com `flyctl deploy`
- [ ] Executar migrações do banco
- [ ] Testar endpoints (/health, /docs)
- [ ] Configurar CORS com URL do frontend
- [ ] Atualizar VITE_API_BASE_URL no frontend Vercel

---

**Pronto!** Seu backend FastAPI está no ar no Fly.io! 🎉

**Próximo passo:** Conecte o frontend na Vercel com a URL do backend:

```bash
# Na Vercel, configure:
VITE_API_BASE_URL=https://inventory-backend.fly.dev/api/v1
```
