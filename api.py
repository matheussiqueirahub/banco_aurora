
from flask import Flask, request, jsonify
from bank import Bank, Customer
from bank.exceptions import BankingError, AccountNotFound

app = Flask(__name__)
bank = Bank("Banco Aurora")
customers = {}

@app.errorhandler(BankingError)
def handle_domain(e):
    return jsonify({"error": str(e)}), 400

@app.post("/customers")
def create_customer():
    data = request.get_json(force=True)
    c = Customer(name=data["name"], document_id=data["document_id"], email=data.get("email"))
    customers[c.id] = c
    bank.register_customer(c)
    return jsonify({"id": c.id, "name": c.name, "document_id": c.document_id, "email": c.email}), 201

@app.post("/accounts")
def open_account():
    data = request.get_json(force=True)
    acc = bank.open_account(
        owner_id=data["owner_id"],
        kind=data["kind"],
        currency=data.get("currency", "BRL"),
        balance=float(data.get("balance", 0.0)),
        **{k: v for k, v in data.items() if k not in {"owner_id", "kind", "currency", "balance"}}
    )
    return jsonify(acc.snapshot()), 201

@app.get("/accounts/<aid>")
def get_account(aid):
    acc = bank.get_account(aid)
    return jsonify(acc.snapshot())

@app.post("/accounts/<aid>/deposit")
def deposit(aid):
    acc = bank.get_account(aid)
    amount = float(request.json["amount"])
    acc.deposit(amount, note=request.json.get("note", ""))
    return jsonify(acc.snapshot())

@app.post("/accounts/<aid>/withdraw")
def withdraw(aid):
    acc = bank.get_account(aid)
    amount = float(request.json["amount"])
    acc.withdraw(amount, note=request.json.get("note", ""))
    return jsonify(acc.snapshot())

@app.post("/transfer")
def transfer():
    data = request.get_json(force=True)
    a = bank.get_account(data["from_id"])
    b = bank.get_account(data["to_id"])
    a.transfer_to(b, float(data["amount"]), note=data.get("note", ""))
    return jsonify({"from": a.snapshot(), "to": b.snapshot()})

@app.post("/eod")
def eod():
    bank.end_of_day()
    return jsonify({"status": "ok"})

@app.get("/dump")
def dump():
    return bank.dump_json()

if __name__ == "__main__":
    app.run(debug=True)
