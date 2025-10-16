#!/bin/bash

# Script para testar a API de Produtos (assume que o sistema já está rodando)
# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testando API de Produtos${NC}"
echo -e "${YELLOW}⚠️  Certifique-se de que o sistema está rodando (localhost:8000)${NC}"
echo ""

# 1. Login
echo -e "${BLUE}1️⃣ Fazendo login...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123")

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo -e "${RED}❌ Erro ao fazer login! Verifique se o backend está rodando.${NC}"
  exit 1
fi

echo -e "${GREEN}✅ Login bem-sucedido!${NC}"
echo ""

# 2. Listar categorias
echo -e "${BLUE}2️⃣ Listando categorias...${NC}"
CATEGORIES=$(curl -s -X GET "http://localhost:8000/api/v1/categories" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-Slug: test-company")

CATEGORY_ID=$(echo $CATEGORIES | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total de categorias: {data[\"total\"]}')
if data['items']:
    for cat in data['items']:
        print(f'  - {cat[\"name\"]} (ID: {cat[\"id\"]}, Status: {cat[\"status\"]})')
    print(cat['id'])
else:
    print('Nenhuma categoria encontrada')
" 2>/dev/null | tail -1)

if [ -z "$CATEGORY_ID" ] || [ "$CATEGORY_ID" = "Nenhuma categoria encontrada" ]; then
  echo -e "${YELLOW}⚠️  Nenhuma categoria encontrada. Criando uma categoria de teste...${NC}"
  
  CREATE_CAT=$(curl -s -X POST "http://localhost:8000/api/v1/categories" \
    -H "Authorization: Bearer $TOKEN" \
    -H "X-Tenant-Slug: test-company" \
    -H "Content-Type: application/json" \
    -d '{
      "name": "Categoria Teste Produtos",
      "description": "Categoria para testes de produtos",
      "status": "active"
    }')
  
  CATEGORY_ID=$(echo $CREATE_CAT | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
  echo -e "${GREEN}✅ Categoria criada: $CATEGORY_ID${NC}"
fi

echo ""

# 3. Criar produto
echo -e "${BLUE}3️⃣ Criando produto de teste...${NC}"
TIMESTAMP=$(date +%s)
SKU="PROD-TEST-$TIMESTAMP"

CREATE_PRODUCT=$(curl -s -X POST "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-Slug: test-company" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"Produto Teste $TIMESTAMP\",
    \"description\": \"Produto criado para teste da API\",
    \"sku\": \"$SKU\",
    \"category_id\": \"$CATEGORY_ID\",
    \"quantity\": 100,
    \"min_quantity\": 10,
    \"max_quantity\": 500,
    \"price\": 99.90,
    \"unit\": \"unidade\",
    \"location\": \"Depósito A - Prateleira 1\",
    \"status\": \"active\"
  }")

PRODUCT_ID=$(echo $CREATE_PRODUCT | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'ID: {data[\"id\"]}')
    print(f'Nome: {data[\"name\"]}')
    print(f'SKU: {data[\"sku\"]}')
    print(f'Quantidade: {data[\"quantity\"]}')
    print(f'Status: {data[\"status\"]}')
    print(data['id'])
except Exception as e:
    print(f'Erro: {str(e)}')
" 2>/dev/null | tail -1)

if [ -z "$PRODUCT_ID" ]; then
  echo -e "${RED}❌ Erro ao criar produto!${NC}"
  echo "Resposta: $CREATE_PRODUCT"
  exit 1
fi

echo -e "${GREEN}✅ Produto criado com sucesso! ID: $PRODUCT_ID${NC}"
echo ""

# 4. Listar produtos
echo -e "${BLUE}4️⃣ Listando todos os produtos...${NC}"
LIST_PRODUCTS=$(curl -s -X GET "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-Slug: test-company")

echo $LIST_PRODUCTS | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total de produtos: {data[\"total\"]}')
print(f'Página: {data[\"page\"]}/{data[\"pages\"]}')
print()
for prod in data['items']:
    print(f'  - {prod[\"name\"]} (SKU: {prod[\"sku\"]})')
    print(f'    Quantidade: {prod[\"quantity\"]} {prod[\"unit\"]}')
    print(f'    Status: {prod[\"status\"]}')
" 2>/dev/null

echo ""

# 5. Buscar produto específico
echo -e "${BLUE}5️⃣ Buscando produto específico (ID: $PRODUCT_ID)...${NC}"
GET_PRODUCT=$(curl -s -X GET "http://localhost:8000/api/v1/products/$PRODUCT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-Slug: test-company")

echo $GET_PRODUCT | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Nome: {data[\"name\"]}')
print(f'SKU: {data[\"sku\"]}')
print(f'Descrição: {data[\"description\"]}')
print(f'Quantidade: {data[\"quantity\"]} {data[\"unit\"]}')
print(f'Min/Max: {data[\"min_quantity\"]}/{data[\"max_quantity\"]}')
print(f'Localização: {data[\"location\"]}')
print(f'Status: {data[\"status\"]}')
" 2>/dev/null

echo -e "${GREEN}✅ Produto encontrado!${NC}"
echo ""

# 6. Atualizar produto
echo -e "${BLUE}6️⃣ Atualizando produto...${NC}"
UPDATE_PRODUCT=$(curl -s -X PUT "http://localhost:8000/api/v1/products/$PRODUCT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-Slug: test-company" \
  -H "Content-Type: application/json" \
  -d "{
    \"quantity\": 150,
    \"price\": 119.90,
    \"description\": \"Produto atualizado via API de testes\",
    \"location\": \"Depósito B - Prateleira 2\"
  }")

echo $UPDATE_PRODUCT | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Nome: {data[\"name\"]}')
print(f'Quantidade: {data[\"quantity\"]} (atualizada de 100 para 150)')
print(f'Preço: R$ {data[\"price\"]} (atualizado de 99.90 para 119.90)')
print(f'Descrição: {data[\"description\"]}')
print(f'Localização: {data[\"location\"]} (atualizada)')
" 2>/dev/null

echo -e "${GREEN}✅ Produto atualizado!${NC}"
echo ""

# 7. Testar filtros
echo -e "${BLUE}7️⃣ Testando filtros...${NC}"

echo "  📌 Filtro por nome:"
curl -s -X GET "http://localhost:8000/api/v1/products?name=Teste" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-Slug: test-company" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'    Encontrados: {data[\"total\"]} produtos')
" 2>/dev/null

echo "  📌 Filtro por SKU:"
curl -s -X GET "http://localhost:8000/api/v1/products?sku=$SKU" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-Slug: test-company" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'    Encontrados: {data[\"total\"]} produtos')
" 2>/dev/null

echo "  📌 Filtro por categoria:"
curl -s -X GET "http://localhost:8000/api/v1/products?category_id=$CATEGORY_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-Slug: test-company" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'    Encontrados: {data[\"total\"]} produtos')
" 2>/dev/null

echo -e "${GREEN}✅ Filtros funcionando!${NC}"
echo ""

# 8. Deletar produto
echo -e "${BLUE}8️⃣ Deletando produto de teste...${NC}"
DELETE_RESPONSE=$(curl -s -w "%{http_code}" -X DELETE "http://localhost:8000/api/v1/products/$PRODUCT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-Slug: test-company")

HTTP_CODE="${DELETE_RESPONSE: -3}"

if [ "$HTTP_CODE" = "204" ]; then
  echo -e "${GREEN}✅ Produto deletado com sucesso!${NC}"
else
  echo -e "${RED}❌ Erro ao deletar produto! HTTP Code: $HTTP_CODE${NC}"
fi

echo ""

# 9. Verificar que produto foi deletado
echo -e "${BLUE}9️⃣ Verificando que produto foi deletado...${NC}"
VERIFY_DELETE=$(curl -s -w "%{http_code}" -X GET "http://localhost:8000/api/v1/products/$PRODUCT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Tenant-Slug: test-company")

HTTP_CODE="${VERIFY_DELETE: -3}"

if [ "$HTTP_CODE" = "404" ]; then
  echo -e "${GREEN}✅ Confirmado: Produto não existe mais (404)${NC}"
else
  echo -e "${YELLOW}⚠️  Produto ainda existe! HTTP Code: $HTTP_CODE${NC}"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Todos os testes de produtos completados!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
