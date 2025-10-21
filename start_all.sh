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

# Preflight: garantir que a porta 8000 (backend) esteja livre
echo "\n🔎 Preflight: verificando porta 8000..."
if lsof -ti tcp:8000 >/dev/null 2>&1; then
    BUSY_PIDS=$(lsof -ti tcp:8000 | tr '\n' ' ')
    echo "⚠️  Porta 8000 em uso pelos PIDs: ${BUSY_PIDS}"
    # Tentar identificar uvicorn/python uvicorn e encerrar automaticamente
    UVICORN_PIDS=$(lsof -nP -iTCP:8000 -sTCP:LISTEN -Fp 2>/dev/null | sed 's/p//' | xargs -I{} ps -o pid=,comm=,args= -p {} 2>/dev/null | grep -E 'uvicorn|python.*uvicorn' | awk '{print $1}')
    if [ -n "$UVICORN_PIDS" ]; then
        echo "🧹 Encerrando uvicorn automático: $UVICORN_PIDS"
        kill $UVICORN_PIDS 2>/dev/null || true
        sleep 1
    else
        echo "❌ Porta 8000 em uso por outro processo que não é uvicorn."
        echo "   Finalize o processo e tente novamente."
        echo "   Dica (macOS): lsof -ti tcp:8000 | xargs kill"
        exit 1
    fi
    # Verificar novamente
    if lsof -ti tcp:8000 >/dev/null 2>&1; then
        echo "❌ Ainda há processos na porta 8000. Abortando."
        exit 1
    else
        echo "✅ Porta 8000 liberada."
    fi
else
    echo "✅ Porta 8000 livre."
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

# Preflight: garantir que a porta 3000 (frontend) esteja livre
echo "\n🔎 Preflight: verificando porta 3000..."
if lsof -ti tcp:3000 >/dev/null 2>&1; then
    BUSY_PIDS_3000=$(lsof -ti tcp:3000 | tr '\n' ' ')
    echo "⚠️  Porta 3000 em uso pelos PIDs: ${BUSY_PIDS_3000}"
    # Tentar identificar vite/node e encerrar automaticamente
    VITE_PIDS=$(lsof -nP -iTCP:3000 -sTCP:LISTEN -Fp 2>/dev/null | sed 's/p//' | xargs -I{} ps -o pid=,comm=,args= -p {} 2>/dev/null | grep -E 'vite|node.*vite' | awk '{print $1}')
    if [ -n "$VITE_PIDS" ]; then
        echo "🧹 Encerrando processos Vite/Node: $VITE_PIDS"
        kill $VITE_PIDS 2>/dev/null || true
        sleep 1
    else
        echo "❌ Porta 3000 em uso por outro processo que não é Vite/Node."
        echo "   Finalize o processo e tente novamente."
        echo "   Dica (macOS): lsof -ti tcp:3000 | xargs kill"
        exit 1
    fi
    # Verificar novamente
    if lsof -ti tcp:3000 >/dev/null 2>&1; then
        echo "❌ Ainda há processos na porta 3000. Abortando."
        exit 1
    else
        echo "✅ Porta 3000 liberada."
    fi
else
    echo "✅ Porta 3000 livre."
fi
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
