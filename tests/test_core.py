from bank import Bank, Customer


def test_transfer_and_eod():
    bank = Bank(name="Banco Aurora")
    c = Customer(name="Matheus", document_id="000")
    bank.register_customer(c)
    a = bank.open_account(c.id, "checking", balance=100.0, currency="BRL")
    b = bank.open_account(c.id, "savings", balance=0.0, currency="BRL", daily_interest_rate=0.001)
    a.transfer_to(b, 50.0)
    bank.end_of_day()  # interest on b, possible fee on a if below threshold
    assert a.balance <= 50.0
    assert b.balance >= 50.0


def test_dump_and_load():
    bank = Bank(name="Banco Aurora")
    c = Customer(name="Matheus", document_id="000")
    bank.register_customer(c)
    bank.open_account(c.id, "savings", balance=10.0)
    s = bank.dump_json()
    bank2 = Bank.load_json(s)
    assert bank2.name == "Banco Aurora"
    assert len(bank2.accounts) == 1
