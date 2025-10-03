from dataclasses import dataclass, field
from typing import Dict
import requests

COINGECKO = 'https://api.coingecko.com/api/v3/simple/price'


@dataclass
class Holding:
    symbol: str
    amount: float


@dataclass
class Portfolio:
    holdings: Dict[str, Holding] = field(default_factory=dict)

    def set(self, symbol: str, amount: float) -> None:
        self.holdings[symbol.upper()] = Holding(symbol.upper(), amount)

    def total_value_usd(self) -> float:
        if not self.holdings:
            return 0.0
        # NOTE: This simplistic approach assumes CoinGecko ids match symbols in lowercase,
        # which is not true for many assets. Replace with proper id mapping later.
        ids = ','.join(s.lower() for s in self.holdings)
        resp = requests.get(COINGECKO, params={'ids': ids, 'vs_currencies': 'usd'}, timeout=15)
        resp.raise_for_status()
        prices = resp.json()
        total = 0.0
        for sym, holding in self.holdings.items():
            price = prices.get(sym.lower(), {}).get('usd', 0.0)
            total += holding.amount * price
        return total
