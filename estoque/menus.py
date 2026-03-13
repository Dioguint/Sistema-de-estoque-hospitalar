from produtos   import cadastrar_produto, listar_produtos, registrar_movimentacao, historico_produto
from relatorios import exportar_csv, resumo_movimentacoes
from validade   import registrar_lote, listar_lotes, alertas_validade


def _menu_validade():
    opcoes = {
        "1": ("Registrar lote (com validade)",        registrar_lote),
        "2": ("Ver todos os lotes",                   lambda: listar_lotes("todos")),
        "3": ("Filtrar: vencidos",                    lambda: listar_lotes("vencidos")),
        "4": ("Filtrar: próximos 30 dias",            lambda: listar_lotes("proximos", 30)),
        "5": ("Filtrar: próximos 7 dias",             lambda: listar_lotes("proximos", 7)),
        "6": ("Filtrar: dentro do prazo (>30d)",      lambda: listar_lotes("ok")),
        "7": ("Resumo / alertas",                     alertas_validade),
        "0": ("Voltar",                               None),
    }
    while True:
        print("\n┌──────────────────────────────────┐")
        print("│     GESTÃO DE VALIDADES          │")
        print("└──────────────────────────────────┘\n")
        for k, (desc, _) in opcoes.items():
            print(f"  [{k}] {desc}")
        escolha = input("\nOpção: ").strip()
        if escolha == "0":
            break
        if escolha in opcoes:
            try:
                opcoes[escolha][1]()
            except Exception as e:
                print(f"Erro: {e}")
        else:
            print("Opção inválida.")


def menu_principal():
    opcoes = {
        "1": ("Cadastrar produto",             cadastrar_produto),
        "2": ("Listar todos os produtos",      lambda: listar_produtos()),
        "3": ("Ver produtos críticos",         lambda: listar_produtos(apenas_criticos=True)),
        "4": ("Registrar entrada",             lambda: registrar_movimentacao("entrada")),
        "5": ("Registrar saída",               lambda: registrar_movimentacao("saida")),
        "6": ("Histórico de um produto",       historico_produto),
        "7": ("Resumo de movimentações",       resumo_movimentacoes),
        "8": ("Exportar relatório CSV",        exportar_csv),
        "9": ("Gestão de Validades / Lotes",  _menu_validade),
        "0": ("Sair",                          None),
    }

    while True:
        print("\n╔══════════════════════════════════════╗")
        print("║   SISTEMA DE CONTROLE DE ESTOQUE     ║")
        print("║        Hospitalar · v2.0             ║")
        print("╚══════════════════════════════════════╝\n")

        for chave, (desc, _) in opcoes.items():
            print(f"  [{chave}] {desc}")

        escolha = input("\nEscolha uma opção: ").strip()

        if escolha == "0":
            print("Encerrando sistema. Até logo!")
            break

        if escolha in opcoes:
            print()
            try:
                opcoes[escolha][1]()
            except Exception as e:
                print(f"Erro: {e}")
        else:
            print("Opção inválida. Tente novamente.")
