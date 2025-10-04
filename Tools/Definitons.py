import datetime
from enum import Enum,auto
from dataclasses import dataclass, field

class InvalidFileException(Exception):
    pass

class TransactionType(Enum):
    BUY      = auto()
    SELL     = auto()
    DIVIDEND = auto()

@dataclass
class Transaction():
    date: datetime.date
    type: TransactionType
    isin: str
    quantity: float              # Amount of shares held
    stockPrice:    float = None  # StockPrice at date
    stockDividend: float = None  # Dividend at date
    stockCurrency: str   = None  # Currency of the stock
    total: float         = None  # Total amount (wihoutTax)
    currency: str        = None  # Currency of the total amount
    cost: float          = 0.0   # Order costs
    profit: float        = None  # Profit when selling

    def __post_init__(self):
        if isinstance(self.date, str):
            self.date = datetime.date.fromisoformat(self.date)


@dataclass
class ParseResult():
    date = datetime.datetime.now()
    transactions: list[Transaction] = field(default_factory=list)
