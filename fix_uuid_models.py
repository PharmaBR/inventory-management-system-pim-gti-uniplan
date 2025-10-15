#!/usr/bin/env python3
"""
Script para substituir UUID do PostgreSQL por GUID compatível com SQLite
em todos os modelos do banco de dados.
"""
import re
from pathlib import Path

# Diretório dos modelos
models_dir = Path("backend/src/db/models")

# Arquivos a serem atualizados
model_files = [
    "user.py",
    "category.py",
    "product.py",
    "movement.py",
    "alert.py",
    "custom_field.py",
]

for filename in model_files:
    filepath = models_dir / filename
    
    if not filepath.exists():
        print(f"❌ Arquivo não encontrado: {filepath}")
        continue
    
    # Ler conteúdo
    content = filepath.read_text()
    
    # Substituir import
    content = re.sub(
        r'from sqlalchemy\.dialects\.postgresql import UUID',
        'from sqlalchemy.orm import relationship',
        content
    )
    
    # Adicionar import do GUID se ainda não existir
    if 'from src.db.models import BaseModel' in content and 'GUID' not in content:
        content = content.replace(
            'from src.db.models import BaseModel',
            'from src.db.models import BaseModel, GUID'
        )
    
    # Substituir UUID(as_uuid=True) por GUID()
    content = re.sub(
        r'UUID\(as_uuid=True\)',
        'GUID()',
        content
    )
    
    # Salvar
    filepath.write_text(content)
    print(f"✅ Atualizado: {filepath}")

print("\n🎉 Todos os modelos foram atualizados!")
