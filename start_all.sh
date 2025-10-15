#!/bin/bash

# 🚀 Script de Início Rápido - Sistema com Autenticação
# Inicia backend e frontend simultaneamente

set -e

echo "🚀 Iniciando Sistema de Gestão de Estoque..."
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se estamos no diretório correto
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Erro: Execute este script do diretório raiz do projeto"
    exit 1
fi

# Função para cleanup
cleanup() {
    echo ""
    echo "🛑 Encerrando servidores..."
    kill 0
}

trap cleanup EXIT

# Iniciar backend
echo -e "${BLUE}📦 Iniciando Backend (FastAPI)...${NC}"
cd backend

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment não encontrado. Criando...${NC}"
    python3 -m venv venv
fi

# Ativar venv e instalar dependências
source venv/bin/activate
pip install -q -r requirements/development.txt

# Iniciar uvicorn em background
echo -e "${GREEN}✅ Backend iniciado em http://localhost:8000${NC}"
uvicorn src.api.main:app --reload --port 8000 &

# Aguardar backend iniciar
sleep 3

# Voltar para raiz
cd ..

# Iniciar frontend
echo -e "${BLUE}⚛️  Iniciando Frontend (React + Vite)...${NC}"
cd frontend

# Instalar dependências se necessário
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules não encontrado. Instalando...${NC}"
    npm install
fi

# Iniciar Vite dev server
echo -e "${GREEN}✅ Frontend iniciado em http://localhost:3001${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Sistema pronto!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "Backend:  ${BLUE}http://localhost:8000${NC}"
echo -e "Frontend: ${BLUE}http://localhost:3001${NC}"
echo -e "Docs API: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo -e "Credenciais de teste:"
echo -e "  E-mail: ${YELLOW}admin@example.com${NC}"
echo -e "  Senha:  ${YELLOW}admin123${NC}"
echo ""
echo -e "Pressione ${YELLOW}Ctrl+C${NC} para encerrar ambos os servidores"
echo ""

npm run dev

# Aguardar
wait
