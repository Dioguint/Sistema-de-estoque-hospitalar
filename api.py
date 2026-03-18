"""
api.py — REST API para o Dashboard de Estoque Hospitalar
Rodar: python api.py
Porta padrão: 5000
"""


from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_connection

app = Flask(__name__)
CORS(app)
#IDs
def produto_to_dict(row):
    return {
        "id":          row[0],
        "nome":        row[1],
        "categoria":   row[2],
        "quantidade":  row[3],
        "unidade":     row[4],
        "estoque_min": row[5],
        "status":      "crit" if row[3] <= row[5] else "ok",
    }

# ── Rotas

@app.route("/api/produtos", methods=["GET"])
def listar_produtos():
    """Lista todos os produtos."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "SELECT id, nome, categoria, quantidade, unidade, estoque_min "
        "FROM produtos ORDER BY nome"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([produto_to_dict(r) for r in rows])


@app.route("/api/criticos", methods=["GET"])
def listar_criticos():
    """Lista produtos com estoque igual ou abaixo do mínimo."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "SELECT id, nome, categoria, quantidade, unidade, estoque_min "
        "FROM produtos WHERE quantidade <= estoque_min ORDER BY quantidade ASC"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([produto_to_dict(r) for r in rows])


@app.route("/api/kpis", methods=["GET"])
def kpis():
    """Retorna KPIs gerais do estoque."""
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM produtos")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM produtos WHERE quantidade <= estoque_min")
    criticos = cur.fetchone()[0]

    cur.execute(
        "SELECT COALESCE(SUM(quantidade),0) FROM movimentacoes "
        "WHERE tipo='entrada' AND data >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
    )
    entradas = cur.fetchone()[0]

    cur.execute(
        "SELECT COALESCE(SUM(quantidade),0) FROM movimentacoes "
        "WHERE tipo='saida' AND data >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
    )
    saidas = cur.fetchone()[0]

    cur.close()
    conn.close()

    taxa = round(((total - criticos) / total * 100)) if total else 0

    return jsonify([
        {"label": "Total de Itens",    "value": total,         "sub": "produtos cadastrados",  "cls": ""},
        {"label": "Itens Críticos",    "value": criticos,      "sub": "abaixo do mínimo",      "cls": "alert" if criticos else "ok"},
        {"label": "Entradas (7 dias)", "value": int(entradas), "sub": "unidades recebidas",    "cls": ""},
        {"label": "Saídas (7 dias)",   "value": int(saidas),   "sub": "unidades distribuídas", "cls": ""},
        {"label": "Abastecimento",     "value": f"{taxa}%",    "sub": "itens no nível OK",     "cls": "ok" if taxa >= 90 else "alert"},
    ])


@app.route("/api/movimentacoes", methods=["GET"])
def movimentacoes():
    """Últimos 7 dias de movimentações agrupadas por dia."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT
            DATE_FORMAT(data, '%a') AS dia,
            SUM(CASE WHEN tipo='entrada' THEN quantidade ELSE 0 END) AS entradas,
            SUM(CASE WHEN tipo='saida'   THEN quantidade ELSE 0 END) AS saidas
        FROM movimentacoes
        WHERE data >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY DATE(data), dia
        ORDER BY DATE(data)
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify({
        "labels":   [r[0] for r in rows],
        "entradas": [int(r[1]) for r in rows],
        "saidas":   [int(r[2]) for r in rows],
    })


@app.route("/api/historico/<int:produto_id>", methods=["GET"])
def historico(produto_id):
    """Histórico de movimentações de um produto."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "SELECT tipo, quantidade, observacao, data "
        "FROM movimentacoes WHERE produto_id = %s ORDER BY data DESC LIMIT 20",
        (produto_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([
        {"tipo": r[0], "quantidade": r[1], "observacao": r[2] or "", "data": str(r[3])}
        for r in rows
    ])


@app.route("/api/entrada", methods=["POST"])
def registrar_entrada():
    """Registra reposição de estoque (entrada)."""
    body       = request.get_json()
    produto_id = body.get("produto_id")
    quantidade = body.get("quantidade")
    observacao = body.get("observacao", "Reposição via dashboard")

    if not produto_id or not quantidade or quantidade <= 0:
        return jsonify({"erro": "produto_id e quantidade são obrigatórios"}), 400

    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("SELECT quantidade, nome FROM produtos WHERE id = %s", (produto_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close()
        return jsonify({"erro": "Produto não encontrado"}), 404

    qtd_atual, nome = row
    nova_qtd = qtd_atual + quantidade

    cur.execute("UPDATE produtos SET quantidade = %s WHERE id = %s", (nova_qtd, produto_id))
    cur.execute(
        "INSERT INTO movimentacoes (produto_id, tipo, quantidade, observacao) VALUES (%s,'entrada',%s,%s)",
        (produto_id, quantidade, observacao)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "sucesso":    True,
        "produto":    nome,
        "qtd_antes":  qtd_atual,
        "qtd_depois": nova_qtd,
        "adicionado": quantidade,
    })


@app.route("/api/categorias", methods=["GET"])
def categorias():
    """Lista categorias únicas dos produtos."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT DISTINCT categoria FROM produtos ORDER BY categoria")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([r[0] for r in rows if r[0]])


if __name__ == "__main__":
    app.run(debug=True, port=5000)
