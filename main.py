
from bank import Bank, Customer
from bank.exceptions import BankingError

def pretty_money(v, cur='BRL'):
    return f"{cur} {v:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def demo():
    bank = Bank(name="Banco Aurora")
    alice = Customer(name="Alice", document_id="111.222.333-44", email="alice@example.com")
    bob = Customer(name="Bob", document_id="555.666.777-88", email="bob@example.com")
    bank.register_customer(alice)
    bank.register_customer(bob)

    a1 = bank.open_account(alice.id, kind="checking", currency="BRL", balance=250.00)
    a2 = bank.open_account(alice.id, kind="savings", currency="BRL", balance=500.00, daily_interest_rate=0.0008)
    b1 = bank.open_account(bob.id, kind="investment", currency="BRL", balance=1000.00, risk_level=4)

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
        print(f"{t.timestamp:%Y-%m-%d %H:%M:%S} | {t.kind:<12} | {pretty_money(t.amount)} | saldo={pretty_money(t.balance_after)} | {t.note}")

    print("\n== JSON do banco ==")
    print(bank.dump_json())

if __name__ == "__main__":
    try:
        demo()
    except BankingError as e:
        print("Erro:", e)
