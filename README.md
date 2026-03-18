# 🏥 Sistema de Estoque Hospitalar

Plataforma completa de gestão de estoque hospitalar com dois módulos integrados: CLI em Python e dashboard web com API REST.

Projeto desenvolvido durante a graduação em **Análise e Desenvolvimento de Sistemas (UNISUAM)**, baseado em 6 anos de experiência no setor hospitalar.

---

## 📦 Módulos

### 1. `estoque/` — Back-end CLI + API REST (Python + MySQL)

- Cadastro de produtos com categoria e estoque mínimo
- Registro de entradas e saídas com histórico completo
- Gestão de lotes com controle de validade
- Alertas automáticos de estoque crítico
- Exportação de relatórios em CSV
- **API REST com Flask** para integração com o dashboard

**Tecnologias:** Python 3.10+, MySQL 8.0, Flask, flask-cors, mysql-connector-python, python-dotenv

---

### 2. `dashboard/` — Front-end Web (HTML + CSS + JS)

- **Login com autenticação** via sessionStorage
- Cards de KPIs dinâmicos (total de itens, críticos, entradas/saídas)
- Gráfico de movimentações dos últimos 7 dias
- Gráfico de distribuição por categoria
- **Busca por nome** e **filtro por categoria** na tabela de críticos
- Modal de detalhes com sugestão de reposição
- **Página de reposição de estoque** integrada à API
- Exportação de estoque crítico em CSV
- Fallback com dados de demonstração quando API está offline
- CSS e JS completamente separados — sem estilos inline

**Tecnologias:** HTML5, CSS3, JavaScript ES6+, Chart.js 4

---

## 🗂️ Estrutura

```
Sistema-de-estoque-hospitalar/
├── dashboard/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── login.js
│   │   ├── main.js
│   │   └── reposicao.js
│   ├── index.html
│   ├── login.html
│   └── reposicao.html
├── estoque/
│   ├── api.py
│   ├── database.py
│   ├── main.py
│   ├── menus.py
│   ├── produtos.py
│   ├── relatorios.py
│   ├── requirements.txt
│   ├── validade.py
│   └── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Como rodar

### Pré-requisitos

- Python 3.10+
- MySQL 8.0
- Navegador moderno

### 1. Banco de dados

```bash
mysql -u root -p
```
```sql
CREATE DATABASE estoque_hospitalar CHARACTER SET utf8mb4;
```

### 2. Configurar variáveis de ambiente

```bash
cd estoque
cp .env.example .env
```

Edite o `.env` com suas credenciais:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=estoque_hospitalar
```

### 3. Instalar dependências e subir a API

```bash
pip install -r requirements.txt
python api.py
```

A API sobe em `http://localhost:5000`

### 4. Abrir o dashboard

Abra `dashboard/login.html` no navegador.

**Credenciais de acesso:**
| Usuário | Senha |
|---------|-------|
| `admin` | `hospital@2025` |
| `estoque` | `estoque@2025` |

> Sem a API rodando, o dashboard exibe dados de demonstração automaticamente.

---

## 🔌 Endpoints da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/api/produtos` | Lista todos os produtos |
| GET | `/api/criticos` | Lista itens abaixo do mínimo |
| GET | `/api/kpis` | KPIs gerais do estoque |
| GET | `/api/movimentacoes` | Movimentações dos últimos 7 dias |
| GET | `/api/historico/<id>` | Histórico de um produto |
| POST | `/api/entrada` | Registra reposição de estoque |

---

## 👤 Autor

**Diogo Bello** — Desenvolvedor Full Stack em formação · ADS UNISUAM · Rio de Janeiro

[![LinkedIn](https://img.shields.io/badge/-LinkedIn-0e76a8?style=flat-square&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/diogo-bello/)
[![Gmail](https://img.shields.io/badge/-Gmail-FF0000?style=flat-square&logo=gmail&logoColor=white)](mailto:Bello1k99@gmail.com)
