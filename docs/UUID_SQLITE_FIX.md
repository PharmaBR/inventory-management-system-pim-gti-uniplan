# ✅ Correção: Tipo UUID Incompatível com SQLite

## ❌ Erro Original
```
ERROR: (in table 'tenants', column 'id'): Compiler <sqlalchemy.dialects.sqlite.base.SQLiteTypeCompiler> 
can't render element of type UUID
```

## 🎯 Causa
O SQLite não possui suporte nativo para o tipo `UUID` do PostgreSQL. O código estava usando:
```python
from sqlalchemy.dialects.postgresql import UUID
id = Column(UUID(as_uuid=True), ...)
```

Isso funciona apenas no PostgreSQL, causando erro no SQLite.

## ✅ Solução Implementada

### 1. Criado GUID TypeDecorator Universal

Em `backend/src/db/models/__init__.py`:

```python
class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    
    Uses PostgreSQL's UUID type when available, otherwise uses
    CHAR(36), storing as stringified hex values.
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        # Converte UUID para string no SQLite
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        # Converte string de volta para UUID no SQLite
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return value
            return uuid.UUID(value)
```

### 2. Substituído UUID por GUID em Todos os Modelos

**Antes:**
```python
from sqlalchemy.dialects.postgresql import UUID

tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), ...)
```

**Depois:**
```python
from src.db.models import BaseModel, GUID

tenant_id = Column(GUID(), ForeignKey("tenants.id"), ...)
```

### 3. Substituído JSONB por JSON

**Antes:**
```python
from sqlalchemy.dialects.postgresql import JSONB
custom_fields = Column(JSONB, default=dict, ...)
```

**Depois:**
```python
from sqlalchemy import JSON
custom_fields = Column(JSON, default=dict, ...)
```

## 📋 Arquivos Modificados

| Arquivo | Mudanças |
|---------|----------|
| `__init__.py` | Criado classe GUID |
| `user.py` | UUID → GUID |
| `category.py` | UUID → GUID |
| `product.py` | UUID → GUID, JSONB → JSON |
| `movement.py` | UUID → GUID |
| `alert.py` | UUID → GUID |
| `custom_field.py` | UUID → GUID |
| `audit_log.py` | UUID → GUID |

## 🎯 Benefícios

✅ **Compatibilidade**: Funciona em SQLite (desenvolvimento) e PostgreSQL (produção)  
✅ **Transparência**: O código continua usando `uuid.UUID` objects  
✅ **Performance**: PostgreSQL usa tipo nativo UUID, SQLite usa CHAR(36)  
✅ **Migração Fácil**: Trocar de SQLite para PostgreSQL não requer mudanças no código

## 🚀 Próximo Teste

Execute novamente:
```bash
./start_all.sh
```

### ✅ Agora Deve Funcionar!

O backend deve iniciar com:
```
INFO: Initializing database tables...
INFO: Tables registered in Base.metadata: ['tenants', 'users', ...]
INFO: Running create_all...
INFO: Application startup complete.
```

**SEM** erros de:
- ❌ can't render element of type UUID

---

**Data:** 15/10/2025, 20:45  
**Commit:** cbe9728
