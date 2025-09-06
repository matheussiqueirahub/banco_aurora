from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from typing import Dict

from .accounts import Account, CheckingAccount, InvestmentAccount, SavingsAccount
from .exceptions import AccountNotFound


@dataclass
class Bank:
    name: str
    accounts: Dict[str, Account] = field(default_factory=dict)
    customers: Dict[str, dict] = field(default_factory=dict)

    def register_customer(self, customer) -> None:
        self.customers[customer.id] = asdict(customer)

    def open_account(self, owner_id: str, kind: str, **kwargs) -> Account:
        account_id = str(uuid.uuid4())[:8]
        klass = {
            "checking": CheckingAccount,
            "savings": SavingsAccount,
            "investment": InvestmentAccount,
        }
        if kind not in klass:
            raise ValueError(f"Unknown account type: {kind}")
        acc = klass[kind](id=account_id, owner_id=owner_id, **kwargs)
        self.accounts[acc.id] = acc
        return acc

    def get_account(self, account_id: str) -> Account:
        try:
            return self.accounts[account_id]
        except KeyError:
            raise AccountNotFound(account_id)

    def end_of_day(self) -> None:
        for acc in self.accounts.values():
            acc.end_of_day()

    # Persistence (simple JSON)
    def dump_json(self) -> str:
        payload = {
            "name": self.name,
            "customers": self.customers,
            "accounts": {aid: acc.snapshot() for aid, acc in self.accounts.items()},
        }
        return json.dumps(payload, indent=2)

    @classmethod
    def load_json(cls, s: str) -> "Bank":
        data = json.loads(s)
        bank = cls(name=data["name"])
        bank.customers = data.get("customers", {})
        for aid, adata in data.get("accounts", {}).items():
            kind = adata["type"].lower().replace("account", "")
            klass = {
                "checking": CheckingAccount,
                "savings": SavingsAccount,
                "investment": InvestmentAccount,
            }[kind]
            acc = klass(
                id=adata["id"],
                owner_id=adata["owner_id"],
                currency=adata["currency"],
                balance=adata["balance"],
            )
            bank.accounts[aid] = acc
        return bank
