# 🚀 Guia de Início Rápido - Sistema com Autenticação

## 📋 Pré-requisitos

- Backend rodando em `http://localhost:8000`
- Conta de usuário criada no backend
- Node.js e npm instalados

## 🔧 Configuração Inicial

### 1. Configurar Backend (se ainda não estiver rodando)

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # ou venv\Scripts\activate no Windows
uvicorn src.api.main:app --reload --port 8000
```

Aguarde até ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### 2. Criar Usuário de Teste (se necessário)

**Opção A: Via Script Python**
```python
# backend/scripts/create_test_user.py
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.core.security import get_password_hash
from src.db.models import User, Tenant
from src.db.base import Base

async def create_test_user():
    engine = create_async_engine("sqlite+aiosqlite:///./test.db")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        # Criar tenant
        tenant = Tenant(
            name="Test Company",
            slug="test-company",
            is_active=True
        )
        session.add(tenant)
        await session.flush()
        
        # Criar usuário
        user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            name="Admin User",
            is_active=True,
            tenant_id=tenant.id
        )
        session.add(user)
        await session.commit()
        
        print(f"✅ Usuário criado:")
        print(f"   E-mail: admin@example.com")
        print(f"   Senha: admin123")

if __name__ == "__main__":
    asyncio.run(create_test_user())
```

Execute:
```bash
cd backend
python scripts/create_test_user.py
```

**Opção B: Via API (se endpoint de registro existir)**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123",
    "name": "Admin User"
  }'
```

### 3. Iniciar Frontend

```bash
# Terminal 2 - Frontend
cd frontend
npm run dev
```

Aguarde até ver:
```
VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:3001/
  ➜  Network: use --host to expose
```

## 🎯 Testando o Sistema

### 1. Acessar Login

Abra o navegador em: **http://localhost:3001/**

Você será automaticamente redirecionado para `/login`

### 2. Fazer Login

**Credenciais de Teste:**
- E-mail: `admin@example.com`
- Senha: `admin123`

Clique em "Entrar"

### 3. Verificar Autenticação

Após login bem-sucedido:
- ✅ Você deve ser redirecionado para `/categories`
- ✅ No header, deve aparecer seu nome/e-mail
- ✅ Botão "Sair" deve estar visível
- ✅ Navegação "Categorias" e "Produtos" deve funcionar

### 4. Testar Funcionalidades

#### Criar Categoria
1. Clique em "Nova Categoria"
2. Preencha:
   - Nome: "Eletrônicos"
   - Descrição: "Produtos eletrônicos"
   - Status: Ativo
3. Clique "Salvar"
4. ✅ Categoria deve aparecer na lista

#### Criar Subcategoria
1. Clique em "Nova Categoria"
2. Preencha:
   - Nome: "Smartphones"
   - Categoria Pai: "Eletrônicos"
   - Status: Ativo
3. Clique "Salvar"
4. ✅ Deve aparecer como filho de "Eletrônicos" na vista de árvore

#### Editar Categoria
1. Clique no ícone de editar (✏️) em uma categoria
2. Altere o nome
3. Clique "Salvar"
4. ✅ Mudanças devem ser refletidas imediatamente

#### Deletar Categoria
1. Clique no ícone de deletar (🗑️)
2. Confirme a exclusão
3. ✅ Categoria deve desaparecer da lista

#### Buscar Categoria
1. Digite no campo de busca: "Smart"
2. ✅ Apenas categorias com "Smart" no nome devem aparecer

#### Filtrar por Status
1. Selecione "Inativo" no filtro de status
2. ✅ Apenas categorias inativas devem aparecer

#### Alternar Visualização
1. Clique no botão "Lista" / "Árvore"
2. ✅ Visualização deve alternar entre lista plana e árvore hierárquica

### 5. Testar Logout

1. Clique no botão "Sair" no header
2. ✅ Você deve ser redirecionado para `/login`
3. ✅ Tentar acessar `/categories` deve redirecionar para `/login`

## 🔍 Verificações Técnicas

### Verificar Tokens no DevTools

1. Abra DevTools (F12)
2. Vá para Application → Local Storage → `http://localhost:3001`
3. Deve conter:
   - `auth_access_token`
   - `auth_refresh_token`
   - `auth_token_expiry`

### Verificar Requisições no Network

1. Abra DevTools (F12) → Network
2. Faça login
3. Deve ver:
   - `POST /api/v1/auth/login` → 200
   - `GET /api/v1/auth/me` → 200
4. Navegue para categorias
5. Deve ver:
   - `GET /api/v1/categories` → 200 (com header `Authorization: Bearer ...`)

### Testar Refresh Token

Para testar o refresh automático de tokens:

1. No DevTools, Application → Local Storage
2. Copie o valor de `auth_access_token`
3. Cole no [jwt.io](https://jwt.io) para ver a expiração
4. Aguarde o token expirar (ou modifique `auth_token_expiry` para uma data passada)
5. Faça uma requisição (ex: recarregue a página de categorias)
6. No Network, deve ver:
   - `GET /api/v1/categories` → 401
   - `POST /api/v1/auth/refresh` → 200
   - `GET /api/v1/categories` (retry) → 200

## 🐛 Troubleshooting

### Erro: "Missing authentication credentials"

**Causa:** Backend não recebeu token ou token inválido

**Solução:**
1. Verifique se fez login
2. Verifique Local Storage tem `auth_access_token`
3. Recarregue a página
4. Faça logout e login novamente

### Erro: "Network Error" ou "ERR_CONNECTION_REFUSED"

**Causa:** Backend não está rodando

**Solução:**
```bash
cd backend
source venv/bin/activate
uvicorn src.api.main:app --reload --port 8000
```

### Erro: "Invalid credentials" no login

**Causa:** E-mail ou senha incorretos

**Solução:**
1. Verifique as credenciais
2. Certifique-se que o usuário foi criado no banco
3. Execute novamente o script de criar usuário de teste

### Página em branco após login

**Causa:** Erro JavaScript ou rota não encontrada

**Solução:**
1. Abra DevTools → Console
2. Verifique erros
3. Certifique-se que frontend está rodando em `localhost:3001`

### Testes não passam após mudanças

**Causa:** Testes ainda usam mocks, mudanças não afetaram testes

**Solução:**
```bash
cd frontend
npm test
```

Todos os 92 testes devem passar, pois usam mocks independentes.

## 📊 Checklist de Validação

- [ ] Backend rodando em `:8000`
- [ ] Frontend rodando em `:3001`
- [ ] Usuário de teste criado
- [ ] Login funciona com credenciais corretas
- [ ] Redirecionamento para `/categories` após login
- [ ] Nome/e-mail aparece no header
- [ ] Botão "Sair" visível
- [ ] Criar categoria funciona
- [ ] Editar categoria funciona
- [ ] Deletar categoria funciona (com confirmação)
- [ ] Busca por nome funciona
- [ ] Filtro por status funciona
- [ ] Alternar Lista/Árvore funciona
- [ ] Logout redireciona para `/login`
- [ ] Tentar acessar rota protegida sem login redireciona
- [ ] Tokens visíveis no Local Storage
- [ ] Headers `Authorization` nas requisições
- [ ] Refresh token funciona automaticamente

## 🎉 Próximos Passos

Após validar tudo acima:

1. **Fase 6 - Produtos**: Replicar estrutura de categorias para produtos
2. **Fase 7 - Estoque**: Implementar movimentações de estoque
3. **Fase 8 - Alertas**: Sistema de alertas de estoque baixo
4. **Fase 9 - Relatórios**: Dashboards e relatórios

---

**Dúvidas?** Consulte:
- `docs/AUTHENTICATION_IMPLEMENTATION.md` - Documentação técnica completa
- `docs/MVP_USAGE_GUIDE.md` - Guia de uso do MVP
- `docs/MOCK_SERVICE_SOLUTION.md` - Informações sobre mocks

**Pronto para produção!** 🚀
