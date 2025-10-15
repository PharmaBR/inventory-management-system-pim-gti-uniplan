#!/bin/bash

# 🚀 Script de Início Rápido - Sistema com Autenticação
# Inicia backend e frontend simultaneamente - SEM SUDO!

set -e

echo "🚀 Iniciando Sistema de Gestão de Estoque..."

# Ir para diretório do script
cd "$(dirname "$0")"

# Verificar se estamos no lugar certo
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Erro: Diretórios backend/frontend não encontrados"
    exit 1
fi

# Verificar/criar venv na raiz do projeto
if [ ! -d ".venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv .venv
    echo "📥 Instalando dependências do backend..."
    .venv/bin/pip install -q -r backend/requirements/dev.txt
fi

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "🛑 Encerrando servidores..."
    jobs -p | xargs kill 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Iniciar Backend
echo ""
echo "📦 Iniciando Backend (FastAPI)..."
cd backend
export PYTHONPATH="$(pwd):$PYTHONPATH"
../.venv/bin/python -m uvicorn src.api.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Aguardar backend iniciar
echo "⏳ Aguardando backend inicializar..."
sleep 3

# Verificar se backend está rodando
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Erro: Backend falhou ao iniciar"
    exit 1
fi

echo "✅ Backend iniciado em http://localhost:8000"

# Iniciar Frontend
echo ""
echo "⚛️  Iniciando Frontend (React + Vite)..."
cd frontend

# Verificar node_modules
if [ ! -d "node_modules" ]; then
    echo "📥 Instalando dependências do frontend..."
    npm install
fi

echo "✅ Frontend iniciando..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Sistema Pronto!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: (será mostrado pelo Vite abaixo)"
echo "Docs API: http://localhost:8000/docs"
echo ""
echo "Credenciais:"
echo "  E-mail: admin@example.com"
echo "  Senha:  admin123"
echo ""
echo "Pressione Ctrl+C para encerrar"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Executar npm (este ficará em foreground)
npm run dev

# Se npm terminar, matar backend
kill $BACKEND_PID 2>/dev/null || true

# Aguardar
wait
