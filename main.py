from __future__ import annotations

import argparse
import csv
import json
from typing import Dict

from bank import Bank, Customer
from bank.exceptions import BankingError


def pretty_money(v, cur="BRL"):
    return f"{cur} {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def demo_bank(return_accounts: bool = False) -> Dict[str, object] | None:
    """Demonstra o pacote bank/ (herança & polimorfismo com end_of_day)."""
    bank = Bank(name="Banco Aurora")
    alice = Customer(name="Alice", document_id="111.222.333-44", email="alice@example.com")
    bob = Customer(name="Bob", document_id="555.666.777-88", email="bob@example.com")
    bank.register_customer(alice)
    bank.register_customer(bob)

    a1 = bank.open_account(alice.id, kind="checking", currency="BRL", balance=250.00)
    a2 = bank.open_account(
        alice.id, kind="savings", currency="BRL", balance=500.00, daily_interest_rate=0.0008
    )
    b1 = bank.open_account(bob.id, kind="investment", currency="BRL", balance=1000.00, risk_level=4)

    accounts = {a1.id: a1, a2.id: a2, b1.id: b1}

    print("== Saldo inicial ==")
    for acc in (a1, a2, b1):
        print(acc.id, acc.__class__.__name__, pretty_money(acc.balance, acc.currency))

    # operações
    a1.deposit(150, "depósito em dinheiro")
    a1.transfer_to(a2, 100, "poupança do mês")
    b1.withdraw(120, "pagamento boleto")

    bank.end_of_day()  # aplica juros/fees por polimorfismo

    print("\n== Após end_of_day() ==")
    for acc in (a1, a2, b1):
        print(acc.id, acc.__class__.__name__, pretty_money(acc.balance, acc.currency))

    print("\n== Ledger conta poupança ==")
    for t in a2.ledger:
        print(
            f"{t.timestamp:%Y-%m-%d %H:%M:%S} | {t.kind:<12} | {pretty_money(t.amount)} | saldo={pretty_money(t.balance_after)} | {t.note}"
        )

    print("\n== JSON do banco ==")
    print(bank.dump_json())

    if return_accounts:
        return accounts
    return None


def print_ledger(acc):
    print(f"\n— Extrato {acc.__class__.__name__} ({acc.id}) —")
    if not acc.ledger:
        print("(sem movimentações)")
        return
    for t in acc.ledger:
        print(
            f"{t.timestamp:%Y-%m-%d %H:%M:%S} | {t.kind:<12} | {pretty_money(t.amount, acc.currency)} | saldo={pretty_money(t.balance_after, acc.currency)} | {t.note}"
        )


def export_ledger(acc, fmt: str, out_path: str):
    """Exporta o ledger da conta em CSV ou JSON."""
    if not acc.ledger:
        print("(sem movimentações)")
        return
    if fmt.lower() == "json":
        payload = [
            {
                "timestamp": t.timestamp.isoformat(),
                "kind": t.kind,
                "amount": round(t.amount, 2),
                "balance_after": round(t.balance_after, 2),
                "note": t.note,
                "currency": getattr(acc, "currency", "BRL"),
                "account_id": acc.id,
                "account_type": acc.__class__.__name__,
            }
            for t in acc.ledger
        ]
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    elif fmt.lower() == "csv":
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "timestamp",
                    "kind",
                    "amount",
                    "balance_after",
                    "note",
                    "currency",
                    "account_id",
                    "account_type",
                ]
            )
            for t in acc.ledger:
                writer.writerow(
                    [
                        t.timestamp.isoformat(),
                        t.kind,
                        f"{t.amount:.2f}",
                        f"{t.balance_after:.2f}",
                        t.note,
                        getattr(acc, "currency", "BRL"),
                        acc.id,
                        acc.__class__.__name__,
                    ]
                )
    else:
        raise ValueError("Formato inválido. Use 'csv' ou 'json'.")
    print(f"Extrato exportado para: {out_path}")


def demo_contas():
    """Demonstra as classes didáticas de contas com extrato (ContaCorrente/ContaPoupanca)."""
    # importação local para não quebrar se 'contas.py' não existir
    from contas import ContaCorrente, ContaPoupanca

    # cria contas
    cc = ContaCorrente("001", "Matheus", 1000, taxa_manutencao=15, limite=800)
    cp = ContaPoupanca("002", "Alice", 2000, taxa_juros=0.05)

    # operações CC
    cc.depositar(500, "depósito salário")
    cc.sacar(1600, "pagamento cartão")  # usa parte do limite
    cc.cobrar_manutencao()

    # operações CP
    cp.depositar(500, "aporte mensal")
    cp.adicionar_juros()

    # resumos
    print(cc.resumo())
    print(cp.resumo())

    # extratos
    print("\n— Extrato Conta Corrente —")
    cc.extrato()
    print("\n— Extrato Conta Poupança —")
    cp.extrato()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Banco Aurora — demos")
    parser.add_argument(
        "--demo",
        choices=["bank", "contas", "both"],
        default="both",
        help="Escolha qual demonstração executar",
    )
    parser.add_argument(
        "--list-accounts",
        action="store_true",
        help="Lista contas (após demo_bank) com id, tipo e saldo",
    )
    parser.add_argument(
        "--extrato",
        metavar="ACCOUNT_ID",
        help="Exibe o extrato (ledger) da conta informada (após demo_bank)",
    )
    parser.add_argument(
        "--export-extrato",
        metavar="ACCOUNT_ID",
        help="Exporta o extrato (ledger) da conta informada (após demo_bank)",
    )
    parser.add_argument(
        "--export-format",
        choices=["csv", "json"],
        default="json",
        help="Formato do arquivo de exportação (padrão: json)",
    )
    parser.add_argument(
        "--export-out",
        metavar="PATH",
        default="extrato.json",
        help="Caminho do arquivo de saída (padrão: extrato.json)",
    )
    args = parser.parse_args()

    try:
        if args.demo in ("bank", "both"):
            accounts = demo_bank(return_accounts=True) or {}
            if args.list_accounts or args.extrato:
                # listar contas
                if args.list_accounts:
                    print("\n— Contas criadas (demo_bank) —")
                    for aid, acc in accounts.items():
                        print(aid, acc.__class__.__name__, pretty_money(acc.balance, acc.currency))
                # extrato por id
                if args.extrato:
                    acc = accounts.get(args.extrato)
                    if acc is None:
                        print(
                            f"Conta '{args.extrato}' não encontrada. Use --list-accounts para ver os ids."
                        )
                    else:
                        print_ledger(acc)
            if args.export_extrato:
                acc = accounts.get(args.export_extrato)
                if acc is None:
                    print(
                        f"Conta '{args.export_extrato}' não encontrada. Use --list-accounts para ver os ids."
                    )
                else:
                    export_ledger(acc, args.export_format, args.export_out)
        if args.demo in ("contas", "both"):
            print("\n" + "=" * 32 + " DEMO CONTAS " + "=" * 32 + "\n")
            demo_contas()
    except BankingError as e:
        print("Erro (domínio bancário):", e)
    except Exception as e:
        print("Erro:", e)
