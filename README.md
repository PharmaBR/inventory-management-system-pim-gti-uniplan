# Sistema de Gerenciamento de Estoque White Label

Sistema multi-tenant de gerenciamento de estoque com personalização de marca, controle de movimentações, relatórios e alertas.

## 🚀 Quick Start

### Usando Docker Compose (Recomendado)

```bash
# Clonar repositório
git clone <repository-url>
cd teste_speckit

# Iniciar todos os serviços
docker-compose up -d

# Aguardar inicialização (~30 segundos)
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### Setup Manual

#### Backend

```bash
cd backend

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements/dev.txt

# Configurar ambiente
cp .env.example .env
# Editar .env com suas configurações

# Iniciar servidor
uvicorn src.api.main:app --reload
```

#### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Configurar ambiente
cp .env.example .env.local

# Iniciar servidor
npm run dev
```

## 📋 Requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (opcional)

## 🏗️ Arquitetura

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 15+ com Row-Level Security
- **Cache**: Redis 7+
- **Auth**: JWT + Bcrypt

### Frontend
- **Framework**: React 18+ com TypeScript
- **Build**: Vite
- **Styling**: TailwindCSS + Shadcn/ui
- **i18n**: react-i18next (PT-BR, EN-US)

### Multi-Tenancy
- Isolamento por subdomain (tenant1.sistema.com)
- Row-Level Security (RLS) no PostgreSQL
- Personalização de marca (logo, cores) por tenant

## 📚 Documentação

- [Especificação](specs/001-sistema-de-gerenciamento/spec.md)
- [Plano de Implementação](specs/001-sistema-de-gerenciamento/plan.md)
- [Modelo de Dados](specs/001-sistema-de-gerenciamento/data-model.md)
- [Contratos de API](specs/001-sistema-de-gerenciamento/contracts/api-contracts.md)
- [Tarefas](specs/001-sistema-de-gerenciamento/tasks.md)
- [Guia de Desenvolvimento](specs/001-sistema-de-gerenciamento/quickstart.md)

## 🧪 Testes

### Backend

```bash
cd backend

# Executar todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/unit/test_products.py
```

### Frontend

```bash
cd frontend

# Executar testes
npm run test

# Com cobertura
npm run test:coverage

# Watch mode
npm run test:watch
```

## 🎯 Roadmap

### MVP (Release 1) - Semanas 1-6
- ✅ Setup do projeto
- [ ] US1: CRUD de Produtos
- [ ] US2: Movimentações de Estoque
- [ ] US3: Multi-tenant + Branding

### Release 2 - Semanas 7-10
- [ ] US4: Gestão de Usuários e Permissões
- [ ] US5: Relatórios e Alertas

### Release 3 - Semanas 11-14
- [ ] US6: Customização por Tenant

### Release 4 - Semanas 15-16
- [ ] Polish & Otimizações
- [ ] Deploy para Produção

## 📊 Performance Targets

- **API**: p95 < 200ms, p99 < 500ms
- **Throughput**: 1000 req/s
- **Escalabilidade**: 100 tenants simultâneos
- **Database Queries**: < 100ms (95%)
- **Test Coverage**: ≥ 80%

## 🛡️ Segurança

- Senhas hasheadas com Bcrypt
- Autenticação JWT com refresh tokens
- Row-Level Security para isolamento de tenants
- HTTPS/TLS obrigatório em produção
- Rate limiting (1000 req/h por usuário)

## 📝 Licença

[Definir licença]

## 👥 Contribuindo

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para guidelines de contribuição.

## 📞 Suporte

Para questões ou suporte, abra uma issue no repositório.
