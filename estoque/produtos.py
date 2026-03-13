from database import get_connection


def cadastrar_produto():
    nome      = input("Nome do produto: ").strip()
    categoria = input("Categoria (ex: medicamento, material, EPI): ").strip()
    unidade   = input("Unidade (un, cx, ml, kg...): ").strip() or "un"
    qtd       = int(input("Quantidade inicial: ") or 0)
    minimo    = int(input("Estoque mínimo para alerta: ") or 5)

    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO produtos (nome, categoria, quantidade, unidade, estoque_min) VALUES (%s,%s,%s,%s,%s)",
        (nome, categoria, qtd, unidade, minimo)
    )
    conn.commit()
    print(f"✔  Produto '{nome}' cadastrado com sucesso!")
    cur.close()
    conn.close()


def listar_produtos(apenas_criticos=False):
    conn = get_connection()
    cur  = conn.cursor()

    if apenas_criticos:
        cur.execute("SELECT id, nome, categoria, quantidade, unidade, estoque_min FROM produtos WHERE quantidade <= estoque_min ORDER BY quantidade ASC")
    else:
        cur.execute("SELECT id, nome, categoria, quantidade, unidade, estoque_min FROM produtos ORDER BY nome")

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print("Nenhum produto encontrado.")
        return

    print(f"\n{'ID':<5} {'Nome':<30} {'Categoria':<20} {'Qtd':<8} {'Un':<6} {'Mín':<6} {'Status'}")
    print("-" * 85)
    for r in rows:
        status = "⚠  CRÍTICO" if r[3] <= r[5] else "✔  OK"
        print(f"{r[0]:<5} {r[1]:<30} {r[2]:<20} {r[3]:<8} {r[4]:<6} {r[5]:<6} {status}")
    print()


def registrar_movimentacao(tipo: str):
    listar_produtos()
    produto_id = int(input(f"ID do produto para {'entrada' if tipo == 'entrada' else 'saída'}: "))
    quantidade = int(input("Quantidade: "))
    obs        = input("Observação (opcional): ").strip()

    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("SELECT quantidade, nome FROM produtos WHERE id = %s", (produto_id,))
    row = cur.fetchone()
    if not row:
        print("Produto não encontrado.")
        cur.close(); conn.close(); return

    qtd_atual, nome = row
    nova_qtd = qtd_atual + quantidade if tipo == "entrada" else qtd_atual - quantidade

    if nova_qtd < 0:
        print(f"Estoque insuficiente! Disponível: {qtd_atual}")
        cur.close(); conn.close(); return

    cur.execute("UPDATE produtos SET quantidade = %s WHERE id = %s", (nova_qtd, produto_id))
    cur.execute(
        "INSERT INTO movimentacoes (produto_id, tipo, quantidade, observacao) VALUES (%s,%s,%s,%s)",
        (produto_id, tipo, quantidade, obs)
    )
    conn.commit()
    sinal = "+" if tipo == "entrada" else "-"
    print(f"✔  {nome}: {qtd_atual} → {nova_qtd} ({sinal}{quantidade})")
    cur.close()
    conn.close()


def historico_produto():
    produto_id = int(input("ID do produto: "))
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("SELECT nome FROM produtos WHERE id = %s", (produto_id,))
    row = cur.fetchone()
    if not row:
        print("Produto não encontrado.")
        cur.close(); conn.close(); return

    print(f"\nHistórico — {row[0]}")
    cur.execute(
        "SELECT tipo, quantidade, observacao, data FROM movimentacoes WHERE produto_id = %s ORDER BY data DESC LIMIT 50",
        (produto_id,)
    )
    rows = cur.fetchall()
    print(f"{'Tipo':<10} {'Qtd':<8} {'Observação':<35} {'Data'}")
    print("-" * 75)
    for r in rows:
        print(f"{r[0]:<10} {r[1]:<8} {(r[2] or '-'):<35} {r[3]}")
    print()
    cur.close()
    conn.close()
