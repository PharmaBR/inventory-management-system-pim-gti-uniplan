# 🚀 Guia: Separar Frontend em Repositório Próprio e Deploy na Vercel

## 📋 Passo a Passo Completo

### 1️⃣ Criar Novo Repositório no GitHub

1. Acesse https://github.com/new
2. Nome sugerido: `inventory-frontend` ou `teste-speckit-frontend`
3. Deixe como **público** ou **privado** (sua escolha)
4. **NÃO** inicialize com README, .gitignore ou licença
5. Clique em "Create repository"
6. Guarde a URL do repositório (ex: `https://github.com/PharmaBR/inventory-frontend.git`)

---

### 2️⃣ Preparar Pasta Frontend Localmente

No terminal, execute os comandos abaixo:

```bash
# Volte para o diretório pai do projeto atual
cd /Users/pharmabio/code/github_speckit

# Crie uma nova pasta para o frontend separado
mkdir inventory-frontend
cd inventory-frontend

# Copie todo o conteúdo da pasta frontend original
cp -r ../teste_speckit/frontend/* .
cp -r ../teste_speckit/frontend/.* . 2>/dev/null || true

# Verifique se os arquivos foram copiados
ls -la
```

Você deve ver: `package.json`, `vite.config.ts`, `src/`, `public/`, etc.

---

### 3️⃣ Inicializar Git e Fazer Primeiro Commit

```bash
# Inicialize o repositório git
git init

# Adicione todos os arquivos
git add .

# Faça o primeiro commit
git commit -m "feat: Initial commit - Frontend separado do monorepo"

# Renomeie a branch para main (se necessário)
git branch -M main

# Conecte com o repositório remoto (use a URL do passo 1)
git remote add origin https://github.com/PharmaBR/inventory-frontend.git

# Envie para o GitHub
git push -u origin main
```

---

### 4️⃣ Configurar Variáveis de Ambiente

Crie um arquivo `.env.example` na raiz do novo repositório:

```bash
cat > .env.example << 'EOF'
# URL da API Backend (será configurada na Vercel)
VITE_API_BASE_URL=http://localhost:8000/api/v1

# Tenant padrão para desenvolvimento
VITE_DEV_TENANT_SLUG=test-company
EOF
```

Commit e push:

```bash
git add .env.example
git commit -m "docs: Add .env.example for deployment"
git push
```

---

### 5️⃣ Deploy na Vercel

#### Online (Dashboard Vercel):

1. Acesse https://vercel.com
2. Faça login com GitHub
3. Clique em **"Add New..."** → **"Project"**
4. Selecione o repositório `inventory-frontend`
5. Configure:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
6. Adicione as **Environment Variables**:
   - `VITE_API_BASE_URL` = `https://seu-backend.fly.dev/api/v1` (URL do Fly.io)
   - `VITE_DEV_TENANT_SLUG` = `test-company`
7. Clique em **"Deploy"**

#### CLI (Alternativa - Mais Rápido):

```bash
# Instale a CLI da Vercel
npm i -g vercel

# No diretório do frontend, execute
vercel

# Siga o assistente:
# - Set up and deploy? Yes
# - Which scope? Escolha sua conta
# - Link to existing project? No
# - Project name? inventory-frontend
# - Directory? ./
# - Override settings? No

# Para produção
vercel --prod
```

---

### 6️⃣ Configurar CORS no Backend

No backend (arquivo `backend/src/core/config.py`), adicione a URL da Vercel aos origins permitidos:

```python
# Exemplo (ajuste conforme sua URL da Vercel)
CORS_ORIGINS = [
    "http://localhost:3000",
    "https://inventory-frontend.vercel.app",
    "https://inventory-frontend-*.vercel.app",  # Preview deployments
]
```

Commit e redeploy do backend.

---

### 7️⃣ Testar o Deploy

1. Acesse a URL fornecida pela Vercel (ex: `https://inventory-frontend.vercel.app`)
2. Teste o login com:
   - E-mail: `admin@example.com`
   - Senha: `admin123`
3. Verifique se as funcionalidades funcionam:
   - Categorias
   - Produtos
   - Movimentações

---

## 🔄 Workflow Após Deploy

### Deploy Automático
Toda vez que você fizer `git push` no repositório do frontend, a Vercel fará deploy automático:
- **Branch `main`**: Deploy em produção
- **Outras branches**: Preview deployments (URLs temporárias para testes)

### Atualizar Frontend
```bash
# Faça suas alterações
# ...

# Commit e push
git add .
git commit -m "feat: nova funcionalidade"
git push

# A Vercel deploya automaticamente em ~30 segundos
```

---

## 🐛 Troubleshooting

### Build Falha na Vercel
- Verifique os logs no dashboard da Vercel
- Certifique-se de que `npm install` e `npm run build` funcionam localmente
- Confirme que todas as dependências estão no `package.json`

### CORS Errors
- Adicione a URL da Vercel no CORS do backend
- Certifique-se de que `VITE_API_BASE_URL` está configurado corretamente

### 404 ao Acessar Rotas
Se você usar React Router e tiver erro 404 ao acessar rotas diretamente, crie um arquivo `vercel.json` na raiz:

```json
{
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

---

## 📚 Recursos Úteis

- [Vercel Documentation](https://vercel.com/docs)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [Environment Variables on Vercel](https://vercel.com/docs/concepts/projects/environment-variables)

---

## ✅ Checklist Rápido

- [ ] Criar novo repositório no GitHub
- [ ] Copiar conteúdo da pasta `frontend/`
- [ ] Inicializar git e fazer primeiro commit
- [ ] Push para GitHub
- [ ] Criar `.env.example`
- [ ] Conectar repositório na Vercel
- [ ] Configurar variáveis de ambiente
- [ ] Deploy
- [ ] Configurar CORS no backend
- [ ] Testar aplicação online

---

**Pronto!** Seu frontend está separado e deployado! 🎉
