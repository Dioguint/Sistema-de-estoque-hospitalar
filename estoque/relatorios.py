import csv
import os
from datetime import datetime
from database import get_connection


def exportar_csv():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT p.nome, p.categoria, p.quantidade, p.unidade, p.estoque_min,
               CASE WHEN p.quantidade <= p.estoque_min THEN 'CRÍTICO' ELSE 'OK' END AS status
        FROM produtos p
        ORDER BY p.nome
    """)
    rows   = cur.fetchall()
    campos = ["Nome", "Categoria", "Quantidade", "Unidade", "Estoque Mínimo", "Status"]
    cur.close()
    conn.close()

    os.makedirs("relatorios", exist_ok=True)
    nome_arquivo = f"relatorios/estoque_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(nome_arquivo, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(campos)
        writer.writerows(rows)

    print(f"✔  Relatório exportado: {nome_arquivo}")


def resumo_movimentacoes():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT p.nome,
               SUM(CASE WHEN m.tipo='entrada' THEN m.quantidade ELSE 0 END) AS total_entradas,
               SUM(CASE WHEN m.tipo='saida'   THEN m.quantidade ELSE 0 END) AS total_saidas
        FROM movimentacoes m
        JOIN produtos p ON p.id = m.produto_id
        GROUP BY p.id, p.nome
        ORDER BY total_saidas DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print("Sem movimentações registradas.")
        return

    print(f"\n{'Produto':<30} {'Entradas':<12} {'Saídas'}")
    print("-" * 55)
    for r in rows:
        print(f"{r[0]:<30} {r[1]:<12} {r[2]}")
    print()
