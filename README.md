# 🏥 Sistema Hospitalar

Repositório com dois módulos complementares para gestão de estoque hospitalar, desenvolvidos como projeto prático durante a graduação em Análise e Desenvolvimento de Sistemas (UNISUAM).

Projeto baseado em 6 anos de experiência no Hospital Geral de Itaguaí.

---

## 📦 Módulos

### 1. `estoque/` — Back-end CLI (Python + MySQL)
Sistema de linha de comando para controle completo do inventário:
- Cadastro de produtos com categoria e estoque mínimo
- Registro de entradas e saídas com histórico
- Gestão de lotes com controle de validade
- Filtros: vencidos / próximos 7 dias / próximos 30 dias
- Alertas automáticos de estoque crítico
- Exportação de relatórios em CSV

**Tecnologias:** Python 3.10+, MySQL 8.0, mysql-connector-python, python-dotenv

### 2. `dashboard/` — Front-end Web (HTML + CSS + JS)
Interface visual para acompanhamento dos indicadores em tempo real:
- Cards de KPIs (total de itens, críticos, entradas/saídas)
- Gráfico de movimentações dos últimos 7 dias
- Gráfico de distribuição por categoria
- Tabela de itens em estado crítico com badges de status

**Tecnologias:** HTML5, CSS3, JavaScript ES6+, Chart.js 4

---

## 🚀 Como rodar

### Back-end (estoque)
```bash
cd estoque
pip install -r requirements.txt
cp .env.example .env   # preencha com suas credenciais MySQL
python main.py
```

### Front-end (dashboard)
```bash
cd dashboard
# Abra index.html no navegador, ou:
npx serve .
```

---

## Estrutura completa

```
sistema-hospitalar/
├── estoque/
│   ├── main.py
│   ├── database.py
│   ├── produtos.py
│   ├── validade.py
│   ├── relatorios.py
│   ├── menus.py
│   ├── requirements.txt
│   └── .env.example
├── dashboard/
│   └── index.html
└── README.md
```
