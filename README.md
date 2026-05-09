# ✦ LuxScent — E-commerce de Perfumes

Sistema completo de e-commerce com Flask, SQLAlchemy, autenticação, painel admin e integração WhatsApp.

---

## 🚀 Como Rodar Localmente

### 1. Pré-requisitos
- Python 3.10 ou superior
- pip

### 2. Clone / extraia o projeto
```bash
cd perfume_store
```

### 3. Crie e ative o ambiente virtual
```bash
# Linux / Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 4. Instale as dependências
```bash
pip install -r requirements.txt
```

### 5. Configure o ambiente
```bash
cp .env.example .env
# Abra o arquivo .env e edite:
#   WHATSAPP_NUMBER — seu número com DDI (ex: 5585999999999)
#   SECRET_KEY      — qualquer string longa e aleatória
#   ADMIN_PASSWORD  — sua senha de admin
```

### 6. Rode o servidor
```bash
python run.py
```

Acesse: **http://localhost:5000**

---

## 🔐 Acessos Padrão

| Área  | URL | Email | Senha |
|-------|-----|-------|-------|
| Loja  | http://localhost:5000 | — | — |
| Admin | http://localhost:5000/admin | admin@luxscent.com | Admin@123 |

> ⚠️ **Mude a senha do admin** antes de publicar online.

---

## 📁 Estrutura do Projeto

```
perfume_store/
├── run.py                  # Ponto de entrada
├── config.py               # Configurações (dev/prod)
├── requirements.txt
├── Procfile                # Deploy Render/Heroku
├── .env.example
│
├── app/
│   ├── __init__.py         # Factory da app + seed de dados
│   ├── models.py           # User, Product, Category, Order, Review
│   └── routes/
│       ├── shop.py         # Home, catálogo, produto, carrinho, checkout
│       ├── auth.py         # Login, cadastro, logout, minha conta
│       ├── admin.py        # Dashboard, CRUD produtos, pedidos
│       └── api.py          # API REST (busca AJAX)
│
├── templates/
│   ├── base.html           # Layout principal (navbar, footer, flash)
│   ├── shop/
│   │   ├── home.html       # Home com hero, promoções, destaques
│   │   ├── catalog.html    # Catálogo com filtros e busca AJAX
│   │   ├── product.html    # Detalhe do produto + avaliações
│   │   ├── cart.html       # Carrinho inteligente
│   │   ├── checkout.html   # Formulário de checkout
│   │   └── order_success.html  # Confirmação + link WhatsApp
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── account.html    # Histórico de pedidos
│   └── admin/
│       ├── base_admin.html # Layout do painel
│       ├── dashboard.html  # KPIs e pedidos recentes
│       ├── products.html   # Lista de produtos
│       ├── product_form.html # Criar / editar produto
│       ├── orders.html     # Lista de pedidos com filtro por status
│       ├── order_detail.html # Detalhes + atualizar status
│       └── categories.html
│
└── static/
    ├── css/
    │   ├── style.css       # Tema dark gold premium
    │   └── admin.css       # Painel admin
    └── js/
        ├── main.js         # Navbar, busca AJAX, cart AJAX, toasts
        └── admin.js        # Preview de imagem, confirmações
```

---

## 🛍️ Funcionalidades

### Loja
- ✅ Hero com CTA e estatísticas
- ✅ Banner de promoções com **contador regressivo**
- ✅ Grid de produtos em destaque
- ✅ Seção de mais vendidos
- ✅ Categorias por família olfativa
- ✅ Depoimentos de clientes
- ✅ Catálogo com filtros (categoria, gênero, ordenação)
- ✅ **Busca em tempo real** via AJAX (sem reload)
- ✅ Página de produto com pirâmide olfativa
- ✅ Sistema de avaliações (estrelas + comentário)
- ✅ Badge de escassez (≤ 5 unidades)
- ✅ Carrinho com **atualização dinâmica** (sem reload)
- ✅ Checkout com dados do cliente
- ✅ **Integração WhatsApp** — mensagem gerada automaticamente
- ✅ Botão flutuante WhatsApp
- ✅ Design totalmente responsivo (mobile first)

### Conta de Usuário
- ✅ Cadastro / Login / Logout
- ✅ Sessão segura com Flask-Login
- ✅ Histórico de pedidos

### Painel Admin
- ✅ Dashboard com KPIs (faturamento, pedidos, produtos, clientes)
- ✅ Alertas de estoque baixo
- ✅ CRUD completo de produtos (com upload de imagem)
- ✅ Gestão de pedidos com filtro por status
- ✅ Atualização de status do pedido (pendente → confirmado → enviado → entregue)
- ✅ Gestão de categorias
- ✅ Link WhatsApp direto para o cliente em cada pedido

---

## 📲 Integração WhatsApp

Ao finalizar o pedido, o sistema:
1. Salva o pedido no banco de dados
2. Gera uma mensagem formatada com nome, endereço, itens e total
3. Redireciona para `https://wa.me/SEU_NUMERO?text=MENSAGEM`
4. Abre o WhatsApp automaticamente após 2 segundos

Para configurar seu número, edite o arquivo `.env`:
```
WHATSAPP_NUMBER=5585999999999
```

---

## 🌐 Deploy Online

### Render.com (grátis)

1. Crie conta em [render.com](https://render.com)
2. **New → Web Service → Connect GitHub** (faça push do projeto)
3. Configurações:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn run:app`
4. **Environment Variables:**
   ```
   FLASK_ENV=production
   SECRET_KEY=sua-chave-secreta-longa
   WHATSAPP_NUMBER=5585999999999
   ```
5. Clique em **Deploy**

### VPS (Ubuntu)

```bash
# Instalar dependências
sudo apt update && sudo apt install python3-pip python3-venv nginx -y

# Configurar projeto
cd /var/www/luxscent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn

# Rodar com gunicorn
gunicorn run:app --bind 127.0.0.1:5000 --workers 2 --daemon

# Configurar Nginx (proxy reverso)
# Ver documentação do Nginx para Flask
```

---

## 💳 Integração Pix / Mercado Pago (próximos passos)

O sistema está preparado. Para adicionar pagamento online:

**Mercado Pago:**
```python
pip install mercadopago
# Adicionar rota /checkout/pagamento em shop.py
# Documentação: https://www.mercadopago.com.br/developers
```

**Pix (EFI Bank / Asaas):**
- Crie conta em Asaas ou EFI Bank
- Use a API REST deles para gerar QR Code
- Adicione webhook para atualizar status do pedido automaticamente

---

## 🔧 Trocar SQLite por PostgreSQL

1. Instale o driver: `pip install psycopg2-binary`
2. No `.env`, defina:
   ```
   DATABASE_URL=postgresql://usuario:senha@host:5432/nome_banco
   ```
3. Rode novamente: `python run.py` — as tabelas são criadas automaticamente.

---

## 📞 Suporte

Dúvidas? Abra uma issue ou entre em contato pelo WhatsApp configurado na loja.

---

*Feito com ❤️ usando Flask + SQLAlchemy — LuxScent © 2024*
