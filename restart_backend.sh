#!/bin/bash
# Script para reiniciar apenas o backend com configurações corrigidas

echo "🔄 Reiniciando Backend com SQLite..."

# Ir para o diretório do backend
cd "$(dirname "$0")/backend"

# Verificar se o venv existe
if [ ! -d "../.venv" ]; then
    echo "❌ Ambiente virtual não encontrado em ../.venv"
    echo "Execute: python3 -m venv ../.venv"
    exit 1
fi

# Ativar ambiente virtual e configurar PYTHONPATH
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo "✅ Ambiente configurado"
echo "📦 Usando SQLite em: test.db"
echo "🚀 Iniciando servidor..."
echo ""

# Executar uvicorn
exec ../venv/bin/python -m uvicorn src.api.main:app --reload --port 8000
