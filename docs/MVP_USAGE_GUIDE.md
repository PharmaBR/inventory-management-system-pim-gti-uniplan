# 🚀 MVP - Guia de Uso Rápido

**Servidor rodando em:** http://localhost:3001/

---

## 🎯 Como Testar o MVP

### 1. Navegação Principal

**Página Inicial** (`/`)
- Clique em "Gerenciar Categorias" para ir ao módulo de categorias
- Clique em "Gerenciar Produtos" (placeholder - em desenvolvimento)

### 2. Módulo de Categorias (`/categories`)

#### 2.1 Visualizações
- **Botão "Lista"**: Visualização em tabela (padrão)
- **Botão "Árvore"**: Visualização hierárquica com expand/collapse

#### 2.2 Criar Nova Categoria
1. Clique em **"Nova Categoria"** (botão azul no topo)
2. Preencha o formulário:
   - **Nome**: obrigatório
   - **Descrição**: opcional
   - **Categoria Pai**: opcional (selecione para criar subcategoria)
3. Clique em **"Criar"**
4. Verifique o toast de sucesso verde

#### 2.3 Buscar e Filtrar
**Na visualização Lista:**
- **Busca**: Digite no campo "Buscar categorias..."
- **Filtros de Status**: 
  - "Todas" - mostra todas
  - "Ativas" - apenas ativas
  - "Inativas" - apenas inativas

#### 2.4 Editar Categoria
1. Na lista/árvore, clique no botão **"Editar"** da categoria
2. Modifique os campos desejados
3. Clique em **"Salvar"**
4. Verifique o toast de sucesso

#### 2.5 Excluir Categoria
1. Clique no botão **"Excluir"** da categoria
2. Confirme na modal de confirmação
3. Verifique o toast de sucesso

#### 2.6 Visualização em Árvore
- Clique na seta **▶** para expandir categorias com filhos
- Clique na seta **▼** para recolher
- Categorias filhas aparecem indentadas

---

## ✨ Recursos Implementados

### ✅ Funcionalidades Principais:
- [x] CRUD completo (Create, Read, Update, Delete)
- [x] Busca por nome
- [x] Filtro por status (Ativo/Inativo)
- [x] Seleção de categoria pai (hierarquia)
- [x] Prevenção de referências circulares
- [x] Visualização Lista e Árvore
- [x] Confirmação antes de excluir
- [x] Notificações toast

### ✅ UX/UI:
- [x] Loading states (skeleton)
- [x] Error states (mensagens amigáveis)
- [x] Empty states ("Nenhuma categoria encontrada")
- [x] Validação de formulários
- [x] Feedback visual (toast notifications)
- [x] Responsivo (mobile, tablet, desktop)

### ✅ Navegação:
- [x] Barra de navegação persistente
- [x] Rotas limpas (`/`, `/categories`, `/products`)
- [x] Página 404 customizada
- [x] Error boundaries (captura erros graciosamente)

---

## 🧪 Cenários de Teste Sugeridos

### Teste 1: Fluxo CRUD Completo
1. ✅ Criar categoria raiz "Eletrônicos"
2. ✅ Criar subcategoria "Computadores" (pai: Eletrônicos)
3. ✅ Criar subcategoria "Notebooks" (pai: Computadores)
4. ✅ Editar "Notebooks" → "Laptops"
5. ✅ Excluir "Laptops"
6. ✅ Verificar que "Computadores" ainda existe

### Teste 2: Hierarquia e Prevenção Circular
1. ✅ Criar "A"
2. ✅ Criar "B" (pai: A)
3. ✅ Criar "C" (pai: B)
4. ✅ Tentar editar "A" e selecionar "C" como pai
5. ✅ Verificar que "C" NÃO aparece na lista (prevenção circular)

### Teste 3: Busca e Filtros
1. ✅ Criar 5 categorias (3 ativas, 2 inativas)
2. ✅ Buscar por nome específico
3. ✅ Filtrar por "Ativas"
4. ✅ Filtrar por "Inativas"
5. ✅ Limpar filtros e verificar todas aparecem

### Teste 4: Visualizações
1. ✅ Criar hierarquia: A → B → C
2. ✅ Ver em modo Lista (flat)
3. ✅ Alternar para Árvore
4. ✅ Expandir/recolher nós
5. ✅ Verificar indentação visual

### Teste 5: Validações
1. ✅ Tentar criar sem nome → erro
2. ✅ Criar com nome vazio/espaços → trim automático
3. ✅ Excluir e cancelar → não exclui
4. ✅ Excluir e confirmar → exclui

### Teste 6: Estados de Loading/Error
1. ✅ Abrir modal → verificar loading durante fetch
2. ✅ Submeter formulário → verificar botão desabilitado
3. ✅ Simular erro de rede → verificar mensagem de erro
4. ✅ Verificar skeleton durante carregamento inicial

---

## 🎨 Atalhos de Teclado

| Tecla | Ação |
|-------|------|
| `Esc` | Fechar modal |
| `Tab` | Navegar entre campos |
| `Enter` | Submeter formulário (quando em campo de input) |
| `Space` | Expandir/recolher na árvore |

---

## 🐛 Debugging

### Verificar Console do Navegador:
- `F12` ou `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
- Aba **Console**: Ver logs e erros
- Aba **Network**: Ver requisições à API
- Aba **React DevTools**: Inspecionar componentes (se instalado)

### Testar com Backend Mock:
Atualmente, o frontend está usando mocks. Para conectar ao backend real:

1. Certifique-se que o backend está rodando em `http://localhost:8000`
2. O frontend fará requisições automaticamente
3. Verifique CORS se houver erros de rede

---

## 📱 Testando Responsividade

1. **Desktop**: Largura completa (1920px+)
2. **Tablet**: Redimensione para ~768px
3. **Mobile**: Redimensione para ~375px
4. **DevTools**: Use "Toggle Device Toolbar" (Cmd+Shift+M)

---

## 🎯 Próximos Testes

Quando o backend estiver conectado:
1. Criar categoria → Verificar no backend
2. Refresh da página → Dados persistem
3. Múltiplos usuários → Isolamento por tenant
4. Paginação → Listas grandes (100+ categorias)
5. Performance → Árvores profundas (5+ níveis)

---

## 🚀 Comandos Úteis

```bash
# Parar servidor
Ctrl+C no terminal

# Reiniciar servidor
npm run dev

# Rodar testes
npm test

# Modo watch (testes)
npm run test:watch

# Build para produção
npm run build

# Preview build
npm run preview
```

---

## 📞 Suporte

Se encontrar bugs ou tiver sugestões:
1. Verifique o console do navegador
2. Verifique os logs do terminal (Vite)
3. Teste com diferentes navegadores
4. Limpe cache se necessário (`Cmd+Shift+R`)

---

**Versão:** 1.0.0 - MVP Phase 5  
**Status:** ✅ Pronto para testes  
**Testes Automatizados:** 92/92 passing  
**URL Local:** http://localhost:3001/

🎉 **Divirta-se testando!**
