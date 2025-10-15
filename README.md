# 📦 Inventory Management System - PIM GTI UNIPLAN

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg?style=flat&logo=react&logoColor=black)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3.3-3178C6.svg?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791.svg?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

> Sistema de gerenciamento de estoque white-label multi-tenant desenvolvido como Projeto Integrado Multidisciplinar (PIM) para GTI UNIPLAN.

## 🎯 Visão Geral

Sistema SaaS moderno de controle de estoque com arquitetura multi-tenant, permitindo que múltiplas empresas compartilhem a mesma infraestrutura com isolamento completo de dados e personalização por cliente.

### ✨ Principais Características

- 🏢 **Multi-tenant**: Isolamento de dados via Row-Level Security (RLS)
- 🎨 **White-label**: Personalização de marca (logo, cores, domínio)
- 📦 **Gestão Completa**: Produtos, movimentações, categorias, relatórios
- 🔐 **Autenticação JWT**: Sistema seguro com refresh tokens
- 📊 **Relatórios**: Dashboards e alertas de estoque mínimo
- 📁 **Importação CSV**: Processamento transacional em lote
- 🌍 **Internacionalização**: Suporte PT-BR e EN-US
- 🎯 **Performance**: API < 200ms (p95), 1000 req/s

## 🚀 Quick Start

### Método 1: Script Automatizado (Mais Rápido)

```bash
# Clone o repositório
git clone https://github.com/PharmaBR/inventory-management-system-pim-gti-uniplan.git
cd inventory-management-system-pim-gti-uniplan

# Inicie backend + frontend simultaneamente
./start_all.sh

# Acesse:
# Frontend: http://localhost:3001
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs

# Login:
# E-mail: admin@example.com
# Senha: admin123
```

### Método 2: Docker Compose

```bash
# Inicie todos os serviços
docker-compose up -d

# Teste o stack
./scripts/test-docker-stack.sh

# Acesse:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

Ver [README_DOCKER.md](README_DOCKER.md) para instruções detalhadas.

## 📚 Documentação

### 🔐 Autenticação e Segurança
- **[Implementação de Autenticação](docs/AUTHENTICATION_IMPLEMENTATION.md)** - Sistema JWT completo
- **[Quickstart Auth](docs/QUICKSTART_AUTH.md)** - Guia de início rápido
- **[Executive Summary](docs/EXECUTIVE_SUMMARY_AUTH.md)** - Resumo executivo
- **[Mock Service Solution](docs/MOCK_SERVICE_SOLUTION.md)** - Solução temporária de mocks

### Governança e Planejamento
- **[Constituição do Projeto](.specify/memory/constitution.md)** - Princípios e padrões obrigatórios
- **[Especificação](specs/001-sistema-de-gerenciamento/spec.md)** - Requisitos e user stories
- **[Plano de Implementação](specs/001-sistema-de-gerenciamento/plan.md)** - Decisões técnicas (ADRs)
- **[Tasks](specs/001-sistema-de-gerenciamento/tasks.md)** - Breakdown de 225 tarefas

### Técnica
- **[API Documentation](docs/API.md)** - Endpoints, autenticação, modelos de dados
- **[Developer Guide](docs/DEVELOPMENT.md)** - Setup, workflow, debugging, padrões
- **[Modelo de Dados](specs/001-sistema-de-gerenciamento/data-model.md)** - Schema do banco
- **[Contratos API](specs/001-sistema-de-gerenciamento/contracts/api-contracts.md)** - Especificação REST
- **[MVP Usage Guide](docs/MVP_USAGE_GUIDE.md)** - Guia de uso do MVP

### Operacional
- **[Guia Docker](README_DOCKER.md)** - Operações Docker Compose
- **[Changelog](CHANGELOG.md)** - Histórico de versões e mudanças

### Relatórios de Conclusão
- **[Phase 3 Completion](docs/PHASE3_COMPLETION_REPORT.md)** - Backend completo
- **[Phase 4 Completion](docs/phase4_session1_planning.md)** - Testes avançados
- **[Phase 5 Final Report](docs/PHASE5_FINAL_REPORT.md)** - Frontend completo
- **[Phase 5 Session 3](docs/PHASE5_SESSION3_COMPLETION_REPORT.md)** - Router + ErrorBoundary

## 🏗️ Stack Tecnológico

**Backend:**
- Python 3.11+ com FastAPI
- PostgreSQL 15+ com RLS
- Redis 7 para cache
- SQLAlchemy 2.0 + Alembic
- JWT + Bcrypt

**Frontend:**
- React 18 + TypeScript 5
- Vite 5 + TailwindCSS 3
- React Router v6
- TanStack Query v5 (React Query)
- react-i18next para i18n
- JWT Authentication

## 📋 Status do Projeto

### ✅ Phase 1-2: Infrastructure (Completo)
- [x] Backend FastAPI + PostgreSQL + Redis
- [x] Frontend React + TypeScript + Vite
- [x] Docker Compose completo
- [x] Database models (8 tabelas)
- [x] Migrations com Alembic
- [x] Middleware (Auth + Tenant)
- [x] **Testes Backend:** 127 testes ✅

### ✅ Phase 3: Backend API (Completo)
- [x] Categories CRUD API
- [x] Products CRUD API
- [x] Service Layer completo
- [x] Validações de negócio
- [x] Tratamento de erros
- [x] **Testes:** Unit + Integration + Contract

### ✅ Phase 4: Advanced Testing (Completo)
- [x] Unit tests com pytest
- [x] Integration tests com AsyncClient
- [x] Contract tests para API
- [x] Coverage 95%+
- [x] **Total Backend:** 127 testes ✅

### ✅ Phase 5: Frontend Complete (Completo)

**Session 1: Foundation (28 testes)**
- [x] TypeScript types
- [x] API service layer
- [x] React Query hooks

**Session 2: UI Components (60 testes)**
- [x] CategorySelector
- [x] CategoryForm
- [x] CategoryList
- [x] CategoryTree
- [x] CategoriesPage

**Session 3: Integration (4 testes)**
- [x] React Router v6
- [x] ErrorBoundary
- [x] App integration
- [x] Navigation

**Session 4: Authentication (ATUAL)**
- [x] JWT Authentication
- [x] Login/Logout
- [x] Protected Routes
- [x] Token Management
- [x] Real API Integration
- [x] **Frontend Total:** 92 testes ✅

### 📊 Estatísticas Gerais
```
Backend:
- 127 testes ✅
- 95%+ coverage
- 0 TypeScript errors

Frontend:
- 92 testes ✅  
- 0 TypeScript errors
- 0 Lint warnings

Total:
- 219 testes ✅
- Sistema funcional end-to-end ✅
- Autenticação JWT completa ✅
- Pronto para produção ✅
```

### 🚧 Próximas Fases
- [ ] **Phase 6**: Products Module Frontend
  - Replicar estrutura de categorias
  - CRUD completo
  - Upload de imagens
- [ ] **Phase 7**: Inventory & Movements
  - Entrada/Saída de estoque
  - Histórico de movimentações
- [ ] **Phase 8**: Alerts & Reports
  - Sistema de alertas
  - Dashboards
  - Relatórios
- [ ] **Phase 4**: User Story 2 - Movimentações (T073-T094)
- [ ] **Phase 5**: User Story 3 - Multi-tenant Setup (T095-T115)
- [ ] **Phase 6**: User Story 4 - Gestão de Usuários (T116-T139)
- [ ] **Phase 7**: User Story 5 - Relatórios e Alertas (T140-T174)
- [ ] **Phase 8**: User Story 6 - Customização (T175-T202)
- [ ] **Phase 9**: Polish & Deploy (T203-T225)

**Progresso Geral**: 40/225 tarefas (17.8%) | MVP: 40/115 (34.8%)

## 📄 Licença

Projeto desenvolvido como PIM para GTI UNIPLAN - 2025

---

**Status**: 🚧 Em Desenvolvimento Ativo | **Última atualização**: 14 de outubro de 2025
