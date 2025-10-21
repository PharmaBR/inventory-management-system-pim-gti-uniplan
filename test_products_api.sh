#!/bin/bash

# Script para testar a API de Produtos
# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testando API de Produtos${NC}"
echo ""

# 1. Login
echo -e "${BLUE}1️⃣ Fazendo login...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123")

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
  echo -e "${RED}❌ Erro ao fazer login!${NC}"
  exit 1
fi

echo -e "${GREEN}✅ Login bem-sucedido!${NC}"
echo ""

# 2. Listar categorias
echo -e "${BLUE}2️⃣ Listando categorias...${NC}"
CATEGORIES=$(curl -s -X GET "http://localhost:8000/api/v1/categories" \
  -H "Authorization: Bearer $TOKEN")

echo $CATEGORIES | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Total de categorias: {data['total']}\")
if data['items']:
    for cat in data['items']:
        print(f\"  - {cat['name']} (ID: {cat['id']}, Status: {cat['status']})\")
" 

# Pegar ID da primeira categoria
CATEGORY_ID=$(echo $CATEGORIES | python3 -c "import sys, json; items = json.load(sys.stdin).get('items', []); print(items[0]['id'] if items else '')")

if [ -z "$CATEGORY_ID" ]; then
  echo -e "${RED}⚠️  Nenhuma categoria encontrada. Criando uma...${NC}"
  
  CREATE_CAT=$(curl -s -X POST "http://localhost:8000/api/v1/categories" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Eletrônicos",
      "description": "Categoria para produtos eletrônicos",
      "status": "active"
    }')
  
  CATEGORY_ID=$(echo $CREATE_CAT | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
  echo -e "${GREEN}✅ Categoria criada! ID: $CATEGORY_ID${NC}"
fi

echo ""

# 3. Criar produto
echo -e "${BLUE}3️⃣ Criando produto...${NC}"
CREATE_PRODUCT=$(curl -s -X POST "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Notebook Dell Inspiron 15\",
    \"description\": \"Notebook com 16GB RAM, 512GB SSD, Intel i7\",
    \"sku\": \"DELL-INSP-15-$(date +%s)\",
    \"category_id\": \"$CATEGORY_ID\",
    \"unit_price\": 4500.00,
    \"quantity\": 10,
    \"min_stock\": 2,
    \"max_stock\": 50,
    \"unit_of_measure\": \"UN\",
    \"location\": \"Estoque A - Prateleira 3\",
    \"status\": \"active\"
  }")

PRODUCT_ID=$(echo $CREATE_PRODUCT | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('id', 'ERROR'))" 2>/dev/null)

if [ "$PRODUCT_ID" = "ERROR" ] || [ -z "$PRODUCT_ID" ]; then
  echo -e "${RED}❌ Erro ao criar produto!${NC}"
  echo $CREATE_PRODUCT | python3 -m json.tool 2>/dev/null || echo $CREATE_PRODUCT
  exit 1
fi

echo -e "${GREEN}✅ Produto criado com sucesso!${NC}"
echo $CREATE_PRODUCT | python3 -m json.tool
echo ""

# 4. Listar produtos
echo -e "${BLUE}4️⃣ Listando produtos...${NC}"
PRODUCTS=$(curl -s -X GET "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer $TOKEN")

echo $PRODUCTS | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Total de produtos: {data['total']}\")
print(f\"Página: {data['page']} | Tamanho: {data['page_size']}\")
print(\"\nProdutos:\")
for prod in data['items']:
    print(f\"  - {prod['name']}\")
    print(f\"    SKU: {prod['sku']}\")
    print(f\"    Preço: R$ {prod['unit_price']:.2f}\")
    print(f\"    Quantidade: {prod['quantity']}\")
    print(f\"    Status: {prod['status']}\")
    print()
"
echo ""

# 5. Obter produto específico
echo -e "${BLUE}5️⃣ Obtendo detalhes do produto criado...${NC}"
PRODUCT_DETAIL=$(curl -s -X GET "http://localhost:8000/api/v1/products/$PRODUCT_ID" \
  -H "Authorization: Bearer $TOKEN")

echo $PRODUCT_DETAIL | python3 -m json.tool
echo ""

# 6. Atualizar produto
echo -e "${BLUE}6️⃣ Atualizando quantidade do produto...${NC}"
UPDATE_PRODUCT=$(curl -s -X PUT "http://localhost:8000/api/v1/products/$PRODUCT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 15,
    "description": "Notebook com 16GB RAM, 512GB SSD, Intel i7 - ATUALIZADO"
  }')

echo $UPDATE_PRODUCT | python3 -m json.tool
echo ""

# 7. Deletar produto
echo -e "${BLUE}7️⃣ Deletando produto de teste...${NC}"
DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "http://localhost:8000/api/v1/products/$PRODUCT_ID" \
  -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "204" ]; then
  echo -e "${GREEN}✅ Produto deletado com sucesso!${NC}"
else
  echo -e "${RED}❌ Erro ao deletar produto. HTTP Code: $HTTP_CODE${NC}"
fi

echo ""
echo -e "${GREEN}🎉 Teste completo!${NC}"
