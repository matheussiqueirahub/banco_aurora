
class BankingError(Exception):
    """Base domain error."""

class NegativeAmount(BankingError):
    pass

class InsufficientFunds(BankingError):
    pass

class CurrencyMismatch(BankingError):
    pass

class AccountNotFound(BankingError):
    pass
