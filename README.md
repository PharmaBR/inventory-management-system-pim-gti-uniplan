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

### Usando Docker Compose (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/PharmaBR/inventory-management-system-pim-gti-uniplan.git
cd inventory-management-system-pim-gti-uniplan

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

### Operacional
- **[Guia Docker](README_DOCKER.md)** - Operações Docker Compose
- **[Changelog](CHANGELOG.md)** - Histórico de versões e mudanças

## 🏗️ Stack Tecnológico

**Backend:**
- Python 3.11+ com FastAPI
- PostgreSQL 15+ com RLS
- Redis 7 para cache
- SQLAlchemy 2.0 + Alembic
- JWT + Bcrypt

**Frontend:**
- React 18 + TypeScript
- Vite 5
- TailwindCSS 3
- TanStack Query
- react-i18next

## 📋 Status do Projeto

### ✅ Phase 1: Setup (Completo - T001-T013)
- [x] Estrutura do projeto (backend + frontend)
- [x] Docker Compose (4 serviços: PostgreSQL, Redis, Backend, Frontend)
- [x] Backend FastAPI básico com CORS
- [x] Frontend React + Vite com hot reload
- [x] Linting e testes configurados
- [x] **Testado**: Stack completo validado

### ✅ Phase 2: Foundational Infrastructure (Completo - T014-T040)

**Backend (27 tarefas):**
- [x] **Database**: SQLAlchemy 2.0 async + 8 modelos ORM + 55 índices
  - Tenants, Users, Categories, Products, Movements, Alerts, CustomFieldDefinitions, AuditLogs
- [x] **Autenticação**: Sistema JWT completo (access + refresh tokens, Bcrypt)
- [x] **Middleware**: Tenant (subdomain/query/header) + Auth (JWT + RBAC)
- [x] **Dependency Injection**: Database session, Auth, Tenant context
- [x] **Infrastructure**: Redis cache + Logging estruturado + Error handlers globais
- [x] **Schemas**: Pydantic base schemas + Pagination + Responses
- [x] **Migrations**: Alembic configurado com async support
- [x] **Testado**: 10/10 testes passando (tables, health, swagger, redis, indexes)

**Frontend (27 tarefas):**
- [x] **i18n**: react-i18next (PT-BR + EN-US) com fallback
- [x] **UI Components**: Button, Input, Modal, Toast (com variants e estados)
- [x] **Layout**: Header (branding + menu), Sidebar (nav), Footer
- [x] **API Client**: Axios com interceptors (JWT injection + auto refresh)
- [x] **Hooks**: useAuth (login/logout/RBAC) + useTenant (context/branding)
- [x] **Utils**: cn() para Tailwind class merging

**Estatísticas da Fase 2:**
- 📦 40+ arquivos criados/modificados
- 💻 ~3.500 linhas de código
- 🔨 7 commits bem documentados
- ✅ 100% dos testes passando

### 🚧 Próximas Fases
- [ ] **Phase 3**: User Story 1 - Products CRUD (T041-T072)
  - TDD workflow: Testes → Schemas → Services → Endpoints → Components
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
