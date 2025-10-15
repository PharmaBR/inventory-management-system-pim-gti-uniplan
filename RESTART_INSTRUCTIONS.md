# 🔄 Instruções para Reiniciar o Sistema

## Problema Identificado
O backend está tentando conectar ao **PostgreSQL**, mas devemos usar **SQLite** em desenvolvimento.

## ✅ Correção Aplicada
O arquivo `backend/.env` foi atualizado para usar SQLite:
```bash
DATABASE_URL=sqlite+aiosqlite:///test.db
```

## 🚀 Como Reiniciar

### Passo 1: Parar os Servidores
No terminal onde o `start_all.sh` está rodando, pressione:
```
Ctrl + C
```

### Passo 2: Reiniciar Tudo
```bash
./start_all.sh
```

## ✅ O que Esperar

### Backend (porta 8000)
Você **NÃO** deve mais ver o erro:
```
ERROR - Failed to initialize database: [Errno 61] Connection refused
```

Deve ver:
```
INFO - Initializing database tables...
INFO - Tables registered in Base.metadata: ['tenants', 'users', ...]
INFO - Application startup complete.
```

### Frontend (porta 3000 ou 3001 ou 3002)
```
VITE v5.4.20 ready in XXX ms
➜  Local:   http://localhost:XXXX/
```

### Login
Após reiniciar, teste o login:
- URL: http://localhost:3000 (ou a porta que o Vite mostrar)
- E-mail: `admin@example.com`
- Senha: `admin123`

## 🔍 Verificar se Funcionou

### 1. Backend Saudável
```bash
curl http://localhost:8000/docs
# Deve abrir a documentação do Swagger
```

### 2. Login Funcional
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"
```

Deve retornar:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### 3. Banco de Dados SQLite
Verifique que o arquivo foi criado:
```bash
ls -lh backend/test.db
```

Consulte os dados:
```bash
sqlite3 backend/test.db "SELECT email, full_name FROM users;"
```

Deve mostrar:
```
admin@example.com|Admin User
```

## 📝 Resumo das Mudanças

| Arquivo | Mudança | Status |
|---------|---------|--------|
| `backend/.env` | PostgreSQL → SQLite | ✅ Concluído |
| `backend/src/api/routes/auth.py` | Endpoints criados | ✅ Concluído |
| `backend/scripts/create_test_user.py` | Usuário criado | ✅ Concluído |

## 🎯 Próximos Passos

Após o login funcionar:
1. ✅ Testar criação de categorias
2. ✅ Testar edição de categorias
3. ✅ Testar exclusão de categorias
4. ✅ Verificar tokens no localStorage
5. 📋 Iniciar implementação do módulo de Produtos (Phase 6)

---

**Última atualização:** 15 de outubro de 2025, 20:20
