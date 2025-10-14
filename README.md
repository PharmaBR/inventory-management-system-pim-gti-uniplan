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

- **[Constituição do Projeto](.specify/memory/constitution.md)** - Princípios e padrões obrigatórios
- **[Especificação](specs/001-sistema-de-gerenciamento/spec.md)** - Requisitos e user stories
- **[Plano de Implementação](specs/001-sistema-de-gerenciamento/plan.md)** - Decisões técnicas
- **[Modelo de Dados](specs/001-sistema-de-gerenciamento/data-model.md)** - Schema do banco
- **[Contratos API](specs/001-sistema-de-gerenciamento/contracts/api-contracts.md)** - Endpoints REST
- **[Tasks](specs/001-sistema-de-gerenciamento/tasks.md)** - Breakdown de 225 tarefas
- **[Guia Docker](README_DOCKER.md)** - Operações Docker Compose

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

### ✅ Phase 1: Setup (Completo)
- [x] Estrutura do projeto
- [x] Docker Compose
- [x] Backend FastAPI básico
- [x] Frontend React + Vite
- [x] Linting e testes configurados

### 🚧 Próximas Fases
- [ ] Phase 2: Foundational (DB, Auth, Middleware)
- [ ] Phase 3-5: MVP Features
- [ ] Phase 6-7: Advanced Features
- [ ] Phase 8-9: Customization & Polish

## 📄 Licença

Projeto desenvolvido como PIM para GTI UNIPLAN - 2025

---

**Status**: 🚧 Em Desenvolvimento Ativo | **Última atualização**: 14 de outubro de 2025
