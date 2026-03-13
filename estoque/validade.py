from datetime import date, timedelta
from database import get_connection


def _status_validade(validade: date) -> tuple[str, str]:
    hoje = date.today()
    diff = (validade - hoje).days
    if diff < 0:
        return "VENCIDO", f"venceu há {-diff}d"
    if diff == 0:
        return "VENCE HOJE", "⚠"
    if diff <= 7:
        return "CRÍTICO", f"{diff}d restantes"
    if diff <= 30:
        return "ATENÇÃO", f"{diff}d restantes"
    return "OK", f"{diff}d restantes"


def registrar_lote():
    """Cadastra um lote com número e validade vinculado a um produto."""
    from produtos import listar_produtos
    listar_produtos()

    produto_id = int(input("ID do produto: "))
    lote       = input("Número/código do lote: ").strip()
    validade   = input("Validade (DD/MM/AAAA): ").strip()

    try:
        d, m, a = validade.split("/")
        val_date = date(int(a), int(m), int(d))
    except ValueError:
        print("Data inválida. Use o formato DD/MM/AAAA.")
        return

    quantidade = int(input("Quantidade deste lote: "))

    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("SELECT nome FROM produtos WHERE id = %s", (produto_id,))
    row = cur.fetchone()
    if not row:
        print("Produto não encontrado.")
        cur.close(); conn.close(); return

    cur.execute(
        "INSERT INTO lotes (produto_id, lote, validade, quantidade) VALUES (%s,%s,%s,%s)",
        (produto_id, lote, val_date, quantidade)
    )
    cur.execute(
        "UPDATE produtos SET quantidade = quantidade + %s WHERE id = %s",
        (quantidade, produto_id)
    )
    cur.execute(
        "INSERT INTO movimentacoes (produto_id, lote_id, tipo, quantidade, observacao) "
        "VALUES (%s, LAST_INSERT_ID(), 'entrada', %s, %s)",
        (produto_id, quantidade, f"Lote {lote} — validade {validade}")
    )

    conn.commit()
    cur.close()
    conn.close()

    status, info = _status_validade(val_date)
    print(f"✔  Lote '{lote}' registrado para '{row[0]}' — {status} ({info})")


def listar_lotes(filtro: str = "todos", dias: int = 30):
    """
    filtro: 'todos' | 'vencidos' | 'proximos' | 'ok'
    dias  : janela em dias para 'proximos' (default 30)
    """
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""
        SELECT l.id, p.nome, p.categoria, l.lote, l.validade, l.quantidade, p.unidade
        FROM lotes l
        JOIN produtos p ON p.id = l.produto_id
        WHERE l.quantidade > 0
        ORDER BY l.validade ASC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    hoje  = date.today()
    limite = hoje + timedelta(days=dias)

    filtrados = []
    for r in rows:
        val = r[4]
        status, info = _status_validade(val)
        if filtro == "vencidos"  and val >= hoje:         continue
        if filtro == "proximos"  and not (hoje <= val <= limite): continue
        if filtro == "ok"        and val <= limite:        continue
        filtrados.append((*r, status, info))

    if not filtrados:
        print("Nenhum lote encontrado para este filtro.")
        return

    print(f"\n{'ID':<5} {'Produto':<28} {'Categ.':<18} {'Lote':<15} {'Validade':<12} {'Qtd':<7} {'Status':<12} {'Detalhe'}")
    print("─" * 115)
    for r in filtrados:
        val_str = r[4].strftime("%d/%m/%Y")
        print(f"{r[0]:<5} {r[1]:<28} {r[2]:<18} {r[3]:<15} {val_str:<12} {r[5]:<7} {r[7]:<12} {r[8]}")
    print()


def alertas_validade():
    """Mostra resumo de lotes vencidos e próximos do vencimento."""
    conn = get_connection()
    cur  = conn.cursor()

    hoje   = date.today()
    em_30  = hoje + timedelta(days=30)

    cur.execute("""
        SELECT COUNT(*), SUM(l.quantidade)
        FROM lotes l WHERE l.validade < %s AND l.quantidade > 0
    """, (hoje,))
    venc = cur.fetchone()

    cur.execute("""
        SELECT COUNT(*), SUM(l.quantidade)
        FROM lotes l WHERE l.validade BETWEEN %s AND %s AND l.quantidade > 0
    """, (hoje, em_30))
    prox = cur.fetchone()

    cur.close()
    conn.close()

    print("\n┌─────────────────────────────────────┐")
    print("│        RESUMO DE VALIDADES           │")
    print("├─────────────────────────────────────┤")
    print(f"│  ❌ Lotes vencidos:   {str(venc[0] or 0):<5}           │")
    print(f"│     Unidades:         {str(int(venc[1] or 0)):<5}           │")
    print(f"│  ⚠  Vencem em 30d:   {str(prox[0] or 0):<5}           │")
    print(f"│     Unidades:         {str(int(prox[1] or 0)):<5}           │")
    print("└─────────────────────────────────────┘\n")
