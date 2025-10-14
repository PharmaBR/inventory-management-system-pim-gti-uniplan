# Tasks: Sistema de Gerenciamento de Estoque White Label

**Branch**: `001-sistema-de-gerenciamento`  
**Input**: Design documents from `/specs/001-sistema-de-gerenciamento/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-contracts.md

**Tests**: Seguindo o princípio TDD da constituição, todos os testes devem ser escritos ANTES da implementação (Red-Green-Refactor).

**Constitution Compliance**: Todas as tarefas devem alinhar com os princípios da constituição do projeto:
- **Code Quality**: Linting (Ruff, Black, isort), formatação, documentação (Google-style docstrings), complexidade < 10
- **TDD**: Escrever testes PRIMEIRO (Red-Green-Refactor), manter cobertura ≥ 80%
- **UX Consistency**: Seguir design system (TailwindCSS + Shadcn/ui), atender WCAG 2.1 AA, fornecer feedback ao usuário
- **Performance**: Atender metas de tempo de resposta (API p95 < 200ms), implementar otimizações (caching, paginação)

**Organization**: Tarefas agrupadas por user story para permitir implementação e teste independente de cada história.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Pode executar em paralelo (arquivos diferentes, sem dependências)
- **[Story]**: A qual user story a tarefa pertence (US1, US2, US3, US4, US5, US6)
- Caminhos de arquivo exatos incluídos nas descrições

---

## Phase 1: Setup (Infraestrutura Compartilhada)

**Objetivo**: Inicialização do projeto e estrutura básica

- [ ] **T001** [P] Criar estrutura de diretórios do projeto conforme plan.md (backend/, frontend/, .github/workflows/)
- [ ] **T002** [P] Inicializar projeto Python 3.11+ com Poetry em `backend/pyproject.toml`
- [ ] **T003** [P] Configurar FastAPI em `backend/src/api/main.py` com CORS, middleware base
- [ ] **T004** [P] Inicializar projeto React 18+ com Vite em `frontend/package.json`
- [ ] **T005** [P] Configurar TailwindCSS e Shadcn/ui em `frontend/tailwind.config.js`
- [ ] **T006** [P] Configurar linting Python (Ruff) em `backend/.ruff.toml`
- [ ] **T007** [P] Configurar formatação Python (Black, isort) em `backend/pyproject.toml`
- [ ] **T008** [P] Configurar linting TypeScript (ESLint) em `frontend/.eslintrc.json`
- [ ] **T009** [P] Configurar formatação TypeScript (Prettier) em `frontend/.prettierrc`
- [ ] **T010** [P] Configurar pytest em `backend/tests/conftest.py` com fixtures base
- [ ] **T011** [P] Configurar Vitest em `frontend/vite.config.ts`
- [ ] **T012** [P] Configurar Docker Compose em `docker-compose.yml` (PostgreSQL, Redis, backend, frontend)
- [ ] **T013** [P] Criar arquivo `.env.example` com variáveis de ambiente necessárias

**Checkpoint**: ✅ Estrutura do projeto inicializada e ferramentas configuradas

---

## Phase 2: Foundational (Pré-requisitos Bloqueantes)

**Objetivo**: Infraestrutura core que DEVE estar completa antes de QUALQUER user story ser implementada

**⚠️ CRÍTICO**: Nenhum trabalho de user story pode começar até esta fase estar completa

- [ ] **T014** Configurar SQLAlchemy 2.0 (async) em `backend/src/db/base.py` com session management
- [ ] **T015** Configurar Alembic para migrations em `backend/alembic.ini` e `backend/alembic/env.py`
- [ ] **T016** [P] Criar schema inicial do banco de dados conforme data-model.md em `backend/alembic/versions/001_initial_schema.py`
- [ ] **T017** [P] Criar modelo ORM `Tenant` em `backend/src/db/models/tenant.py` com RLS policies
- [ ] **T018** [P] Criar modelo ORM `User` em `backend/src/db/models/user.py` com RLS policies
- [ ] **T019** [P] Criar modelo ORM `Category` em `backend/src/db/models/category.py` com RLS policies
- [ ] **T020** [P] Criar modelo ORM `Product` em `backend/src/db/models/product.py` com RLS policies e JSONB custom_fields
- [ ] **T021** [P] Criar modelo ORM `Movement` em `backend/src/db/models/movement.py` com RLS policies
- [ ] **T022** [P] Criar modelo ORM `Alert` em `backend/src/db/models/alert.py` com RLS policies
- [ ] **T023** [P] Criar modelo ORM `CustomFieldDefinition` em `backend/src/db/models/custom_field.py` com RLS policies
- [ ] **T024** [P] Criar modelo ORM `AuditLog` em `backend/src/db/models/audit_log.py` com RLS policies
- [ ] **T025** Implementar sistema de autenticação JWT em `backend/src/core/security.py` (hash passwords, create/verify tokens)
- [ ] **T026** Implementar middleware de identificação de tenant via subdomain em `backend/src/api/middleware/tenant.py`
- [ ] **T027** Implementar middleware de autenticação JWT em `backend/src/api/middleware/auth.py`
- [ ] **T028** Implementar dependency injection para DB session em `backend/src/api/dependencies/database.py`
- [ ] **T029** Implementar dependency injection para current user em `backend/src/api/dependencies/auth.py`
- [ ] **T030** Implementar dependency injection para tenant context em `backend/src/api/dependencies/tenant.py`
- [ ] **T031** [P] Configurar logging estruturado em `backend/src/core/logging.py` (níveis: ERROR, WARN, INFO, DEBUG)
- [ ] **T032** [P] Configurar tratamento global de exceções em `backend/src/api/middleware/error_handler.py`
- [ ] **T033** [P] Configurar Redis para caching em `backend/src/core/cache.py`
- [ ] **T034** [P] Criar schemas Pydantic base em `backend/src/schemas/base.py` (BaseModel, timestamps, pagination)
- [ ] **T035** [P] Configurar react-i18next em `frontend/src/i18n/index.ts` com PT-BR e EN-US
- [ ] **T036** [P] Criar componentes UI base (Button, Input, Modal, Toast) em `frontend/src/components/ui/`
- [ ] **T037** [P] Criar layout base (Header, Sidebar, Footer) em `frontend/src/components/layout/`
- [ ] **T038** [P] Configurar axios client com interceptors (JWT, tenant header) em `frontend/src/services/api.ts`
- [ ] **T039** [P] Criar hook useAuth para autenticação em `frontend/src/hooks/useAuth.ts`
- [ ] **T040** [P] Criar hook useTenant para contexto de tenant em `frontend/src/hooks/useTenant.ts`

**Checkpoint**: ✅ Fundação pronta - implementação de user stories pode começar em paralelo

---

## Phase 3: User Story 1 - Gestão Básica de Produtos (Priority: P1) 🎯 MVP

**Objetivo**: Gestores podem cadastrar, visualizar, editar e excluir produtos do catálogo.

**Teste Independente**: Criar um produto, visualizar na listagem, editar seus dados e deletar. Sistema permite controlar inventário básico.

### Testes para User Story 1 (TDD - ESCREVER PRIMEIRO)

**NOTA: Escrever estes testes PRIMEIRO, garantir que FALHAM antes da implementação**

- [ ] **T041** [P] [US1] Contract test para POST /products em `backend/tests/contract/test_products_create.py`
- [ ] **T042** [P] [US1] Contract test para GET /products (list) em `backend/tests/contract/test_products_list.py`
- [ ] **T043** [P] [US1] Contract test para GET /products/{id} em `backend/tests/contract/test_products_get.py`
- [ ] **T044** [P] [US1] Contract test para PUT /products/{id} em `backend/tests/contract/test_products_update.py`
- [ ] **T045** [P] [US1] Contract test para DELETE /products/{id} em `backend/tests/contract/test_products_delete.py`
- [ ] **T046** [P] [US1] Unit test para ProductService.create() em `backend/tests/unit/test_product_service.py`
- [ ] **T047** [P] [US1] Unit test para validação de SKU único em `backend/tests/unit/test_product_validation.py`
- [ ] **T048** [P] [US1] Integration test para jornada completa CRUD de produto em `backend/tests/integration/test_product_crud.py`
- [ ] **T049** [P] [US1] Component test para ProductForm em `frontend/tests/unit/ProductForm.test.tsx`
- [ ] **T050** [P] [US1] Component test para ProductList em `frontend/tests/unit/ProductList.test.tsx`
- [ ] **T051** [P] [US1] E2E test para jornada de cadastro de produto em `frontend/tests/e2e/product-creation.spec.ts`

### Implementação para User Story 1

- [ ] **T052** [P] [US1] Criar schema Pydantic ProductCreate em `backend/src/schemas/product.py`
- [ ] **T053** [P] [US1] Criar schema Pydantic ProductUpdate em `backend/src/schemas/product.py`
- [ ] **T054** [P] [US1] Criar schema Pydantic ProductResponse em `backend/src/schemas/product.py`
- [ ] **T055** [US1] Implementar ProductService.create() em `backend/src/services/product.py` (validação SKU único, tenant_id)
- [ ] **T056** [US1] Implementar ProductService.get_by_id() em `backend/src/services/product.py` (com RLS)
- [ ] **T057** [US1] Implementar ProductService.list() em `backend/src/services/product.py` (paginação, filtros, RLS)
- [ ] **T058** [US1] Implementar ProductService.update() em `backend/src/services/product.py` (validação, audit log)
- [ ] **T059** [US1] Implementar ProductService.soft_delete() em `backend/src/services/product.py` (status='inactive', audit log)
- [ ] **T060** [US1] Implementar endpoint POST /products em `backend/src/api/routes/products.py`
- [ ] **T061** [US1] Implementar endpoint GET /products em `backend/src/api/routes/products.py` (com paginação)
- [ ] **T062** [US1] Implementar endpoint GET /products/{id} em `backend/src/api/routes/products.py`
- [ ] **T063** [US1] Implementar endpoint PUT /products/{id} em `backend/src/api/routes/products.py`
- [ ] **T064** [US1] Implementar endpoint DELETE /products/{id} em `backend/src/api/routes/products.py`
- [ ] **T065** [P] [US1] Criar serviço API products.ts em `frontend/src/services/products.ts` (CRUD functions)
- [ ] **T066** [P] [US1] Criar componente ProductForm em `frontend/src/components/products/ProductForm.tsx` (validação, i18n)
- [ ] **T067** [P] [US1] Criar componente ProductCard em `frontend/src/components/products/ProductCard.tsx`
- [ ] **T068** [P] [US1] Criar componente ProductList em `frontend/src/components/products/ProductList.tsx` (paginação, loading states)
- [ ] **T069** [US1] Criar página Products.tsx em `frontend/src/pages/Products.tsx` (integração completa)
- [ ] **T070** [US1] Adicionar validação de formulário com feedback em ProductForm (loading, success, error)
- [ ] **T071** [US1] Adicionar acessibilidade WCAG 2.1 AA em componentes de produto (keyboard nav, ARIA labels)
- [ ] **T072** [US1] Adicionar traduções PT-BR e EN-US em `frontend/src/i18n/pt-BR.json` e `en-US.json`

**Checkpoint**: ✅ User Story 1 totalmente funcional e testável independentemente

---

## Phase 4: User Story 2 - Movimentação de Estoque (Priority: P1)

**Objetivo**: Gestores registram entradas/saídas de estoque, atualizando quantidades automaticamente.

**Teste Independente**: Criar entrada de 50 unidades de um produto, depois saída de 20 unidades. Verificar saldo atualiza para 30 e histórico registra ambas movimentações.

### Testes para User Story 2 (TDD - ESCREVER PRIMEIRO)

- [ ] **T073** [P] [US2] Contract test para POST /movements em `backend/tests/contract/test_movements_create.py`
- [ ] **T074** [P] [US2] Contract test para GET /movements em `backend/tests/contract/test_movements_list.py`
- [ ] **T075** [P] [US2] Contract test para GET /products/{id}/movements em `backend/tests/contract/test_product_movements.py`
- [ ] **T076** [P] [US2] Unit test para MovementService.create() em `backend/tests/unit/test_movement_service.py`
- [ ] **T077** [P] [US2] Unit test para atualização automática de saldo em `backend/tests/unit/test_stock_update.py`
- [ ] **T078** [P] [US2] Integration test para jornada de movimentação completa em `backend/tests/integration/test_movement_flow.py`
- [ ] **T079** [P] [US2] Component test para MovementForm em `frontend/tests/unit/MovementForm.test.tsx`
- [ ] **T080** [P] [US2] Component test para MovementHistory em `frontend/tests/unit/MovementHistory.test.tsx`

### Implementação para User Story 2

- [ ] **T081** [P] [US2] Criar schema Pydantic MovementCreate em `backend/src/schemas/movement.py`
- [ ] **T082** [P] [US2] Criar schema Pydantic MovementResponse em `backend/src/schemas/movement.py`
- [ ] **T083** [US2] Implementar MovementService.create() em `backend/src/services/movement.py` (atualização de saldo, validação, audit log)
- [ ] **T084** [US2] Implementar MovementService.list() em `backend/src/services/movement.py` (filtros por produto/data, paginação)
- [ ] **T085** [US2] Implementar MovementService.get_by_product() em `backend/src/services/movement.py` (histórico do produto)
- [ ] **T086** [US2] Implementar endpoint POST /movements em `backend/src/api/routes/movements.py`
- [ ] **T087** [US2] Implementar endpoint GET /movements em `backend/src/api/routes/movements.py`
- [ ] **T088** [US2] Implementar endpoint GET /products/{id}/movements em `backend/src/api/routes/products.py`
- [ ] **T089** [P] [US2] Criar serviço API movements.ts em `frontend/src/services/movements.ts`
- [ ] **T090** [P] [US2] Criar componente MovementForm em `frontend/src/components/movements/MovementForm.tsx` (entrada/saída, validação)
- [ ] **T091** [P] [US2] Criar componente MovementHistory em `frontend/src/components/movements/MovementHistory.tsx` (timeline, filtros)
- [ ] **T092** [US2] Criar página Movements.tsx em `frontend/src/pages/Movements.tsx`
- [ ] **T093** [US2] Adicionar alerta visual para estoque negativo em MovementForm
- [ ] **T094** [US2] Adicionar traduções PT-BR e EN-US para movimentações

**Checkpoint**: ✅ User Stories 1 E 2 funcionam independentemente

---

## Phase 5: User Story 3 - Multi-tenant White Label (Priority: P1)

**Objetivo**: Cada cliente tem ambiente isolado com marca personalizada (logo, cores).

**Teste Independente**: Criar dois tenants, cadastrar produtos em cada um, fazer login com usuário de cada tenant e verificar que cada um vê apenas seus próprios dados.

### Testes para User Story 3 (TDD - ESCREVER PRIMEIRO)

- [ ] **T095** [P] [US3] Contract test para GET /tenant/config em `backend/tests/contract/test_tenant_config.py`
- [ ] **T096** [P] [US3] Contract test para PUT /tenant/config em `backend/tests/contract/test_tenant_update.py`
- [ ] **T097** [P] [US3] Unit test para isolamento de dados por tenant em `backend/tests/unit/test_tenant_isolation.py`
- [ ] **T098** [P] [US3] Integration test para criação de tenant e primeiro admin em `backend/tests/integration/test_tenant_setup.py`
- [ ] **T099** [P] [US3] E2E test para personalização de marca em `frontend/tests/e2e/tenant-branding.spec.ts`
- [ ] **T100** [P] [US3] Security test para tentativa de acesso cross-tenant em `backend/tests/security/test_tenant_access.py`

### Implementação para User Story 3

- [ ] **T101** [P] [US3] Criar schema Pydantic TenantConfig em `backend/src/schemas/tenant.py`
- [ ] **T102** [P] [US3] Criar schema Pydantic TenantUpdate em `backend/src/schemas/tenant.py`
- [ ] **T103** [US3] Implementar TenantService.get_config() em `backend/src/services/tenant.py` (com cache Redis 1h)
- [ ] **T104** [US3] Implementar TenantService.update_config() em `backend/src/services/tenant.py` (invalidar cache)
- [ ] **T105** [US3] Implementar endpoint GET /tenant/config em `backend/src/api/routes/tenant.py`
- [ ] **T106** [US3] Implementar endpoint PUT /tenant/config em `backend/src/api/routes/tenant.py` (admin only)
- [ ] **T107** [US3] Criar script de criação de tenant em `backend/scripts/create_tenant.py`
- [ ] **T108** [P] [US3] Criar serviço API tenant.ts em `frontend/src/services/tenant.ts`
- [ ] **T109** [P] [US3] Criar hook useTenantConfig em `frontend/src/hooks/useTenantConfig.ts` (load config, apply theme)
- [ ] **T110** [P] [US3] Criar componente TenantConfigForm em `frontend/src/components/tenant/TenantConfigForm.tsx`
- [ ] **T111** [US3] Implementar aplicação dinâmica de cores (CSS variables) em `frontend/src/utils/theme.ts`
- [ ] **T112** [US3] Implementar exibição de logo no Header em `frontend/src/components/layout/Header.tsx`
- [ ] **T113** [US3] Criar página Settings.tsx em `frontend/src/pages/Settings.tsx` (configuração de marca)
- [ ] **T114** [US3] Adicionar validação de formato de cores hex em TenantConfigForm
- [ ] **T115** [US3] Adicionar traduções PT-BR e EN-US para configurações de tenant

**Checkpoint**: ✅ Todas as 3 user stories P1 funcionam independentemente (MVP completo)

---

## Phase 6: User Story 4 - Gestão de Usuários e Permissões (Priority: P2)

**Objetivo**: Admins criam usuários com diferentes níveis de acesso (admin, gestor, operador).

**Teste Independente**: Criar usuário com perfil "operador" (apenas leitura), fazer login e verificar que pode visualizar produtos mas não pode editá-los.

### Testes para User Story 4 (TDD - ESCREVER PRIMEIRO)

- [ ] **T116** [P] [US4] Contract test para POST /users em `backend/tests/contract/test_users_create.py`
- [ ] **T117** [P] [US4] Contract test para GET /users em `backend/tests/contract/test_users_list.py`
- [ ] **T118** [P] [US4] Contract test para PUT /users/{id} em `backend/tests/contract/test_users_update.py`
- [ ] **T119** [P] [US4] Unit test para verificação de permissões por role em `backend/tests/unit/test_permissions.py`
- [ ] **T120** [P] [US4] Integration test para criação de usuário e primeiro login em `backend/tests/integration/test_user_flow.py`
- [ ] **T121** [P] [US4] Component test para UserForm em `frontend/tests/unit/UserForm.test.tsx`

### Implementação para User Story 4

- [ ] **T122** [P] [US4] Criar schema Pydantic UserCreate em `backend/src/schemas/user.py`
- [ ] **T123** [P] [US4] Criar schema Pydantic UserUpdate em `backend/src/schemas/user.py`
- [ ] **T124** [P] [US4] Criar schema Pydantic UserResponse em `backend/src/schemas/user.py`
- [ ] **T125** [US4] Implementar UserService.create() em `backend/src/services/user.py` (hash password, validação email único)
- [ ] **T126** [US4] Implementar UserService.list() em `backend/src/services/user.py` (admin/manager only)
- [ ] **T127** [US4] Implementar UserService.update() em `backend/src/services/user.py` (audit log)
- [ ] **T128** [US4] Implementar UserService.soft_delete() em `backend/src/services/user.py` (desativação)
- [ ] **T129** [US4] Implementar decorador @require_role() em `backend/src/api/dependencies/permissions.py`
- [ ] **T130** [US4] Implementar endpoint POST /users em `backend/src/api/routes/users.py` (admin only)
- [ ] **T131** [US4] Implementar endpoint GET /users em `backend/src/api/routes/users.py` (admin/manager only)
- [ ] **T132** [US4] Implementar endpoint PUT /users/{id} em `backend/src/api/routes/users.py` (admin only)
- [ ] **T133** [US4] Implementar endpoint DELETE /users/{id} em `backend/src/api/routes/users.py` (admin only)
- [ ] **T134** [P] [US4] Criar serviço API users.ts em `frontend/src/services/users.ts`
- [ ] **T135** [P] [US4] Criar componente UserForm em `frontend/src/components/users/UserForm.tsx`
- [ ] **T136** [P] [US4] Criar componente UserList em `frontend/src/components/users/UserList.tsx`
- [ ] **T137** [US4] Criar página Users.tsx em `frontend/src/pages/Users.tsx` (admin/manager only)
- [ ] **T138** [US4] Implementar controle de visibilidade de UI baseado em role (useAuth hook)
- [ ] **T139** [US4] Adicionar traduções PT-BR e EN-US para gestão de usuários

**Checkpoint**: ✅ User Stories 1, 2, 3 E 4 funcionam independentemente

---

## Phase 7: User Story 5 - Relatórios e Alertas de Estoque (Priority: P2)

**Objetivo**: Gestores visualizam relatórios de estoque, produtos em falta, movimentações e exportam para Excel/CSV. Alertas automáticos para estoque baixo.

**Teste Independente**: Configurar nível mínimo de 10 unidades para produto, reduzir estoque para 8, verificar que alerta é exibido no dashboard.

### Testes para User Story 5 (TDD - ESCREVER PRIMEIRO)

- [ ] **T140** [P] [US5] Contract test para GET /reports/stock em `backend/tests/contract/test_reports_stock.py`
- [ ] **T141** [P] [US5] Contract test para GET /reports/low-stock em `backend/tests/contract/test_reports_low_stock.py`
- [ ] **T142** [P] [US5] Contract test para GET /reports/movements em `backend/tests/contract/test_reports_movements.py`
- [ ] **T143** [P] [US5] Contract test para POST /reports/export em `backend/tests/contract/test_reports_export.py`
- [ ] **T144** [P] [US5] Contract test para GET /alerts em `backend/tests/contract/test_alerts_list.py`
- [ ] **T145** [P] [US5] Unit test para geração de alerta automático em `backend/tests/unit/test_alert_generation.py`
- [ ] **T146** [P] [US5] Unit test para exportação CSV em `backend/tests/unit/test_csv_export.py`
- [ ] **T147** [P] [US5] Component test para ReportViewer em `frontend/tests/unit/ReportViewer.test.tsx`

### Implementação para User Story 5

- [ ] **T148** [P] [US5] Criar schema Pydantic StockReportResponse em `backend/src/schemas/report.py`
- [ ] **T149** [P] [US5] Criar schema Pydantic AlertResponse em `backend/src/schemas/alert.py`
- [ ] **T150** [US5] Implementar ReportService.get_stock_report() em `backend/src/services/report.py` (ordenação por quantidade)
- [ ] **T151** [US5] Implementar ReportService.get_low_stock() em `backend/src/services/report.py` (produtos abaixo do mínimo)
- [ ] **T152** [US5] Implementar ReportService.get_movements_report() em `backend/src/services/report.py` (filtros por período)
- [ ] **T153** [US5] Implementar ReportService.export_to_csv() em `backend/src/services/report.py`
- [ ] **T154** [US5] Implementar ReportService.export_to_excel() em `backend/src/services/report.py` (usando openpyxl)
- [ ] **T155** [US5] Implementar AlertService.create_alert() em `backend/src/services/alert.py` (chamado após movimentação)
- [ ] **T156** [US5] Implementar AlertService.get_unread() em `backend/src/services/alert.py`
- [ ] **T157** [US5] Implementar AlertService.mark_as_read() em `backend/src/services/alert.py`
- [ ] **T158** [US5] Implementar endpoint GET /reports/stock em `backend/src/api/routes/reports.py`
- [ ] **T159** [US5] Implementar endpoint GET /reports/low-stock em `backend/src/api/routes/reports.py`
- [ ] **T160** [US5] Implementar endpoint GET /reports/movements em `backend/src/api/routes/reports.py`
- [ ] **T161** [US5] Implementar endpoint POST /reports/export em `backend/src/api/routes/reports.py` (retorna file download)
- [ ] **T162** [US5] Implementar endpoint GET /alerts em `backend/src/api/routes/alerts.py`
- [ ] **T163** [US5] Implementar endpoint PUT /alerts/{id}/read em `backend/src/api/routes/alerts.py`
- [ ] **T164** [US5] Adicionar trigger para geração de alerta em MovementService.create()
- [ ] **T165** [P] [US5] Criar serviço API reports.ts em `frontend/src/services/reports.ts`
- [ ] **T166** [P] [US5] Criar serviço API alerts.ts em `frontend/src/services/alerts.ts`
- [ ] **T167** [P] [US5] Criar componente ReportViewer em `frontend/src/components/reports/ReportViewer.tsx` (tabela com filtros)
- [ ] **T168** [P] [US5] Criar componente ExportButton em `frontend/src/components/reports/ExportButton.tsx` (CSV/Excel)
- [ ] **T169** [P] [US5] Criar componente AlertBadge em `frontend/src/components/alerts/AlertBadge.tsx` (notificação no header)
- [ ] **T170** [P] [US5] Criar componente AlertList em `frontend/src/components/alerts/AlertList.tsx`
- [ ] **T171** [US5] Criar página Reports.tsx em `frontend/src/pages/Reports.tsx` (tabs para diferentes relatórios)
- [ ] **T172** [US5] Criar página Dashboard.tsx em `frontend/src/pages/Dashboard.tsx` (visão geral com alertas)
- [ ] **T173** [US5] Adicionar indicador de alertas não lidos no Header
- [ ] **T174** [US5] Adicionar traduções PT-BR e EN-US para relatórios e alertas

**Checkpoint**: ✅ User Stories 1, 2, 3, 4 E 5 funcionam independentemente

---

## Phase 8: User Story 6 - Customização por Tenant (Priority: P3)

**Objetivo**: Admins de tenant ativam/desativam funcionalidades, configuram campos customizados, ajustam fluxos.

**Teste Independente**: Tenant A ativa campo customizado "Lote", cadastra produto com lote. Tenant B não ativa este campo e não vê opção de lote.

### Testes para User Story 6 (TDD - ESCREVER PRIMEIRO)

- [ ] **T175** [P] [US6] Contract test para POST /tenant/custom-fields em `backend/tests/contract/test_custom_fields_create.py`
- [ ] **T176** [P] [US6] Contract test para GET /tenant/custom-fields em `backend/tests/contract/test_custom_fields_list.py`
- [ ] **T177** [P] [US6] Contract test para POST /products/import em `backend/tests/contract/test_products_import.py`
- [ ] **T178** [P] [US6] Unit test para validação de campos customizados em `backend/tests/unit/test_custom_field_validation.py`
- [ ] **T179** [P] [US6] Unit test para importação transacional em `backend/tests/unit/test_transactional_import.py`
- [ ] **T180** [P] [US6] Integration test para produto com campos customizados em `backend/tests/integration/test_custom_fields_flow.py`

### Implementação para User Story 6

- [ ] **T181** [P] [US6] Criar schema Pydantic CustomFieldDefinitionCreate em `backend/src/schemas/custom_field.py`
- [ ] **T182** [P] [US6] Criar schema Pydantic CustomFieldDefinitionResponse em `backend/src/schemas/custom_field.py`
- [ ] **T183** [P] [US6] Criar schema Pydantic ProductImportRow em `backend/src/schemas/product.py`
- [ ] **T184** [US6] Implementar CustomFieldService.create_definition() em `backend/src/services/custom_field.py`
- [ ] **T185** [US6] Implementar CustomFieldService.get_definitions() em `backend/src/services/custom_field.py`
- [ ] **T186** [US6] Implementar CustomFieldService.validate_value() em `backend/src/services/custom_field.py` (valida tipo/formato)
- [ ] **T187** [US6] Implementar ProductService.import_from_csv() em `backend/src/services/product.py` (2 fases: validação + inserção)
- [ ] **T188** [US6] Implementar ProductService.validate_import_file() em `backend/src/services/product.py` (valida todas linhas)
- [ ] **T189** [US6] Implementar ProductService.generate_import_error_report() em `backend/src/services/product.py`
- [ ] **T190** [US6] Implementar endpoint POST /tenant/custom-fields em `backend/src/api/routes/tenant.py` (admin only)
- [ ] **T191** [US6] Implementar endpoint GET /tenant/custom-fields em `backend/src/api/routes/tenant.py`
- [ ] **T192** [US6] Implementar endpoint POST /products/import em `backend/src/api/routes/products.py` (multipart/form-data)
- [ ] **T193** [US6] Adicionar suporte a custom_fields JSONB em ProductService.create() e update()
- [ ] **T194** [P] [US6] Criar serviço API customFields.ts em `frontend/src/services/customFields.ts`
- [ ] **T195** [P] [US6] Criar componente CustomFieldDefinitionForm em `frontend/src/components/tenant/CustomFieldDefinitionForm.tsx`
- [ ] **T196** [P] [US6] Criar componente DynamicCustomFields em `frontend/src/components/products/DynamicCustomFields.tsx` (renderiza campos JSONB)
- [ ] **T197** [P] [US6] Criar componente ImportProductsDialog em `frontend/src/components/products/ImportProductsDialog.tsx` (upload CSV)
- [ ] **T198** [US6] Integrar DynamicCustomFields em ProductForm (carrega definições do tenant)
- [ ] **T199** [US6] Adicionar botão de importação em Products.tsx
- [ ] **T200** [US6] Exibir campos customizados em ProductCard e ProductList
- [ ] **T201** [US6] Incluir campos customizados em exportações de relatórios
- [ ] **T202** [US6] Adicionar traduções PT-BR e EN-US para customização

**Checkpoint**: ✅ Todas as user stories funcionam independentemente (sistema completo)

---

## Phase 9: Polish & Cross-Cutting Concerns

**Objetivo**: Refinamentos finais, otimizações de performance, documentação, CI/CD

- [ ] **T203** [P] Implementar paginação com cursors em listagens grandes (>1000 itens)
- [ ] **T204** [P] Adicionar índices de banco em campos de busca frequente (SKU, name, tenant_id+created_at)
- [ ] **T205** [P] Implementar cache Redis para configurações de tenant (TTL 1h)
- [ ] **T206** [P] Implementar lazy loading de imagens de produtos
- [ ] **T207** [P] Adicionar compressão gzip/brotli em assets estáticos
- [ ] **T208** [P] Configurar rate limiting (1000 req/h por usuário, 10000/h por tenant)
- [ ] **T209** [P] Implementar métricas Prometheus em `backend/src/core/metrics.py` (request_count, latency, errors)
- [ ] **T210** [P] Adicionar health check endpoint GET /health em `backend/src/api/routes/health.py`
- [ ] **T211** [P] Criar pipeline CI backend em `.github/workflows/backend-ci.yml` (lint, test, coverage)
- [ ] **T212** [P] Criar pipeline CI frontend em `.github/workflows/frontend-ci.yml` (lint, test, build)
- [ ] **T213** [P] Configurar pre-commit hooks em `.pre-commit-config.yaml` (black, ruff, eslint)
- [ ] **T214** [P] Documentar API com OpenAPI/Swagger em `backend/src/api/main.py` (autodoc)
- [ ] **T215** [P] Criar guia de contribuição em `CONTRIBUTING.md`
- [ ] **T216** [P] Atualizar README.md com badges, quick start, arquitetura
- [ ] **T217** [P] Criar script de seed data para desenvolvimento em `backend/scripts/seed_data.py`
- [ ] **T218** [P] Adicionar tratamento de erros 404, 403, 500 com mensagens i18n
- [ ] **T219** [P] Adicionar loading skeletons em listagens
- [ ] **T220** [P] Implementar dark mode toggle (opcional, além do escopo)
- [ ] **T221** Executar auditoria de acessibilidade (WCAG 2.1 AA) com axe-core
- [ ] **T222** Executar testes de carga com Locust (1000 req/s, 100 tenants)
- [ ] **T223** Validar cobertura de testes ≥ 80% em backend e frontend
- [ ] **T224** Revisar e otimizar queries N+1 com eager loading
- [ ] **T225** Documentar decisões de arquitetura em ADRs (Architecture Decision Records)

**Checkpoint**: ✅ Sistema pronto para produção

---

## Dependencies & Execution Order

### Dependency Graph (User Story Completion Order)

```
Setup (Phase 1) → Foundational (Phase 2) → ┌─ US1: Produtos (P1) ────────┐
                                           ├─ US2: Movimentações (P1) ───┤ → MVP
                                           └─ US3: Multi-tenant (P1) ────┘
                                                      ↓
                                           ┌─ US4: Usuários (P2) ────────┐
                                           └─ US5: Relatórios (P2) ──────┘
                                                      ↓
                                           ┌─ US6: Customização (P3) ────┘
                                                      ↓
                                           Polish & Cross-Cutting (Phase 9)
```

### Parallelização Detalhada

**Phase 2 (Foundational) - Após T016:**
- Grupo A (modelos ORM): T017, T018, T019, T020, T021, T022, T023, T024 (paralelo)
- Grupo B (middleware): T031, T032, T033 (paralelo após modelos)
- Grupo C (frontend base): T035, T036, T037, T038, T039, T040 (paralelo após T016)

**Phase 3 (US1 - Produtos):**
- Testes: T041-T051 (paralelo, escrever PRIMEIRO)
- Backend schemas: T052, T053, T054 (paralelo)
- Backend services: T055-T059 (sequencial, dependem de schemas)
- Backend routes: T060-T064 (sequencial, dependem de services)
- Frontend: T065-T072 (paralelo após routes prontas)

**Phase 4 (US2 - Movimentações):**
- Testes: T073-T080 (paralelo, escrever PRIMEIRO)
- Backend: T081-T088 (mesma lógica de US1)
- Frontend: T089-T094 (paralelo após backend)

**Phases 5-8 (US3-US6):**
- Seguem mesmo padrão: testes → backend → frontend
- US4, US5, US6 podem começar em paralelo APÓS US1, US2, US3 completarem

**Phase 9 (Polish):**
- T203-T220 são todos paralelos
- T221-T225 são validações finais (sequenciais)

---

## Implementation Strategy

### MVP First (Minimum Viable Product)

**Escopo MVP**: User Stories 1, 2, 3 (Prioridade P1)
- **US1**: CRUD de produtos
- **US2**: Movimentações de estoque
- **US3**: Multi-tenancy + branding

**Entrega de Valor**: Com apenas as 3 primeiras user stories, o sistema já é funcional e comercializável:
- Cliente pode controlar inventário completo
- Múltiplos clientes isolados
- Marca personalizada por tenant

**Tempo Estimado MVP**: ~4-6 semanas (assumindo 1 desenvolvedor full-stack)

### Incremental Delivery

**Release 1 (MVP)**: US1 + US2 + US3 → Sistema básico funcional
**Release 2**: + US4 + US5 → Gestão de usuários e relatórios
**Release 3**: + US6 → Customização avançada
**Release 4**: Polish → Otimizações e refinamentos

### Development Best Practices

1. **TDD Workflow** (Red-Green-Refactor):
   - ❌ Escrever teste → deve FALHAR
   - ✅ Implementar código mínimo → teste PASSA
   - 🔧 Refatorar código mantendo testes passando

2. **Code Quality Gates**:
   - Linting obrigatório antes de commit (pre-commit hooks)
   - Complexidade ciclomática < 10 (Radon para Python)
   - Cobertura ≥ 80% para novo código
   - Code review obrigatório (1+ aprovação)

3. **Performance Checkpoints**:
   - Após cada user story: validar API p95 < 200ms
   - Após US5: validar relatórios grandes < 5s
   - Antes de Release 1: load test 1000 req/s

4. **Accessibility Checkpoints**:
   - Após cada componente frontend: validar navegação por teclado
   - Antes de Release 1: audit completo com axe-core
   - Validar contraste de cores com tenant customizado

---

## Summary

**Total Tasks**: 225 tarefas
**Task Count per User Story**:
- Setup & Foundational: 40 tarefas
- US1 (Produtos): 32 tarefas
- US2 (Movimentações): 22 tarefas
- US3 (Multi-tenant): 21 tarefas
- US4 (Usuários): 24 tarefas
- US5 (Relatórios/Alertas): 35 tarefas
- US6 (Customização): 28 tarefas
- Polish: 23 tarefas

**Parallel Opportunities**: 120+ tarefas podem executar em paralelo (marcadas com [P])

**Independent Test Criteria**:
- US1: CRUD completo de produto funcionando
- US2: Registro de movimentação atualizando saldo
- US3: Dois tenants isolados com marcas diferentes
- US4: Usuário operador não pode editar produtos
- US5: Alerta gerado quando estoque < mínimo
- US6: Campo customizado aparece apenas para tenant que ativou

**Suggested MVP Scope**: User Stories 1, 2, 3 (Tasks T001-T115) = Sistema funcional em 4-6 semanas

---

**Pronto para começar! Execute as tarefas em ordem, seguindo o princípio TDD. Boa sorte! 🚀**
