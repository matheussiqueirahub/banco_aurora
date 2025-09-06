from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict, List

from .exceptions import CurrencyMismatch, InsufficientFunds, NegativeAmount


@dataclass
class Transaction:
    kind: str  # 'deposit', 'withdraw', 'transfer_in', 'transfer_out', 'fee', 'yield', 'interest'
    amount: float
    balance_after: float
    timestamp: datetime
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d


@dataclass
class Account(ABC):
    id: str
    owner_id: str
    currency: str = "BRL"
    balance: float = 0.0
    _ledger: List[Transaction] = field(default_factory=list, init=False, repr=False)

    def _assert_positive(self, amount: float):
        if amount <= 0:
            raise NegativeAmount("Amount must be positive.")

    def _assert_currency(self, other: "Account"):
        if self.currency != other.currency:
            raise CurrencyMismatch(f"Currency mismatch: {self.currency} vs {other.currency}")

    def _record(self, kind: str, amount: float, note: str = ""):
        self._ledger.append(
            Transaction(
                kind,
                round(amount, 2),
                round(self.balance, 2),
                datetime.now(UTC),
                note,
            )
        )

    @property
    def ledger(self) -> List[Transaction]:
        return list(self._ledger)

    def deposit(self, amount: float, note: str = "") -> None:
        self._assert_positive(amount)
        self.balance += amount
        self._record("deposit", amount, note or "deposit")

    def withdraw(self, amount: float, note: str = "") -> None:
        self._assert_positive(amount)
        if amount > self.balance:
            raise InsufficientFunds("Insufficient funds.")
        self.balance -= amount
        self._record("withdraw", amount, note or "withdraw")

    def transfer_to(self, other: "Account", amount: float, note: str = "") -> None:
        self._assert_currency(other)
        self.withdraw(amount, note or f"transfer to {other.id}")
        other.deposit(amount, note or f"transfer from {self.id}")
        self._record("transfer_out", amount, note or f"to {other.id}")
        other._record("transfer_in", amount, note or f"from {self.id}")

    @abstractmethod
    def end_of_day(self) -> None:
        """Domain hook: each account type applies its own rules daily (fees, interest, yields)."""
        ...

    def snapshot(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "currency": self.currency,
            "balance": round(self.balance, 2),
            "type": self.__class__.__name__,
            "ledger": [t.to_dict() for t in self._ledger],
        }


@dataclass
class CheckingAccount(Account):
    maintenance_fee: float = 3.90
    minimum_balance: float = 50.0

    def end_of_day(self) -> None:
        # Apply maintenance only if balance below threshold
        if self.balance < self.minimum_balance and self.maintenance_fee > 0:
            fee = min(self.maintenance_fee, self.balance) if self.balance > 0 else 0.0
            if fee > 0:
                self.balance -= fee
                self._record("fee", fee, f"maintenance (< {self.minimum_balance} {self.currency})")


@dataclass
class SavingsAccount(Account):
    daily_interest_rate: float = 0.0005  # ~0.05% per day ~ 1.5%/mo simplified

    def end_of_day(self) -> None:
        if self.balance > 0 and self.daily_interest_rate > 0:
            interest = self.balance * self.daily_interest_rate
            self.balance += interest
            self._record("interest", interest, f"{self.daily_interest_rate*100:.4f}% daily")


@dataclass
class InvestmentAccount(Account):
    risk_level: int = 3  # 1..5
    management_fee_daily: float = 0.0001  # 0.01% per day

    def end_of_day(self) -> None:
        # Simple stochastic-like yield: deterministic pseudo-variance by risk_level
        # (No randomness to keep tests deterministic)
        base_yield = 0.0003 + (self.risk_level - 3) * 0.00015  # [-0.0003 .. 0.0006] around 0.0003
        gross = self.balance * base_yield if self.balance > 0 else 0.0
        fee = self.balance * self.management_fee_daily if self.balance > 0 else 0.0
        delta = gross - fee
        if delta != 0:
            self.balance += delta
            if gross:
                self._record("yield", gross, f"base_yield {base_yield*100:.4f}%")
            if fee:
                self._record("fee", fee, f"mgmt {self.management_fee_daily*100:.4f}%")
