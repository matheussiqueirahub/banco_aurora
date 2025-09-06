from typing import Optional

import typer
from rich import print

from bank import Bank, Customer

app = typer.Typer(help="Banco Aurora — CLI")

bank = Bank("Banco Aurora")
customers = {}


@app.command()
def add_customer(name: str, document_id: str, email: Optional[str] = None):
    c = Customer(name=name, document_id=document_id, email=email)
    customers[c.id] = c
    bank.register_customer(c)
    print({"customer_id": c.id})


@app.command()
def open_account(customer_id: str, kind: str, currency: str = "BRL", balance: float = 0.0):
    acc = bank.open_account(customer_id, kind=kind, currency=currency, balance=balance)
    print(acc.snapshot())


@app.command()
def deposit(account_id: str, amount: float):
    acc = bank.get_account(account_id)
    acc.deposit(amount)
    print(acc.snapshot())


@app.command()
def withdraw(account_id: str, amount: float):
    acc = bank.get_account(account_id)
    acc.withdraw(amount)
    print(acc.snapshot())


@app.command()
def transfer(from_id: str, to_id: str, amount: float):
    a = bank.get_account(from_id)
    b = bank.get_account(to_id)
    a.transfer_to(b, amount)
    print({"from": a.snapshot(), "to": b.snapshot()})


@app.command()
def eod():
    bank.end_of_day()
    print("ok")


@app.command()
def dump():
    print(bank.dump_json())


if __name__ == "__main__":
    app()
