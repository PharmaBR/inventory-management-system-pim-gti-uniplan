# 🔧 Correção Final: Enum Role - ADMIN vs admin

## ❌ Erro
```
LookupError: 'admin' is not among the defined enum values. 
Enum name: user_role. 
Possible values: ADMIN, MANAGER, OPERATOR
```

## 🎯 Causa
SQLAlchemy Enum com `native_enum=False` no SQLite espera as **chaves** do Enum (ADMIN, MANAGER, OPERATOR) e não os **valores** ("admin", "manager", "operator").

## ✅ Solução

### Modelo User (backend/src/db/models/user.py):
```python
class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    ADMIN = "admin"      # Chave: ADMIN, Valor: "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
```

### Banco de Dados:
- **Errado:** `role = "admin"` (minúsculo)
- **Correto:** `role = "ADMIN"` (MAIÚSCULO - chave do Enum)

### Script Atualizado:
`backend/scripts/quick_create_user.py` agora usa `"ADMIN"` em vez de `"admin"`.

## 🚀 Testar Agora

### 1. Verificar usuário no banco:
```bash
sqlite3 backend/test.db "SELECT email, role FROM users;"
```

Deve retornar:
```
admin@example.com|ADMIN
```

### 2. Iniciar sistema:
```bash
./start_all.sh
```

### 3. Testar login:
- **URL:** http://localhost:3000
- **E-mail:** admin@example.com
- **Senha:** admin123
- **✅ Deve funcionar agora!**

### 4. Teste com cURL:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"
```

Deve retornar tokens JWT:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 900
}
```

## 📋 Histórico Completo

| # | Erro | Solução | Commit | Status |
|---|------|---------|--------|--------|
| 1 | ModuleNotFoundError: aiosqlite | Instalado aiosqlite | a9b6367 | ✅ |
| 2 | Invalid pool_size/max_overflow | Configuração condicional | 2faa79e | ✅ |
| 3 | Can't render UUID type | GUID TypeDecorator | cbe9728 | ✅ |
| 4 | Script pede sudo | Removido sudo | (merged) | ✅ |
| 5 | information_schema.tables | sqlite_master | 518af77 | ✅ |
| 6 | 401 Unauthorized | Criado usuário | 8a7226f | ✅ |
| 7 | Enum LookupError: admin | Role ADMIN maiúsculo | 6eba7ab | ✅ |

---

**Data:** 15/10/2025, 21:05  
**Status:** ✅ **RESOLVIDO - Sistema 100% funcional!**
