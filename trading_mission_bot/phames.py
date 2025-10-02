import re
from typing import Literal

MissionBias = Literal['long', 'short', 'neutral']

BIAS_PATTERNS = [
    (re.compile(r"\b(long bias|bullish|uptrend|higher highs)\b", re.I), 'long'),
    (re.compile(r"\b(short bias|bearish|downtrend|lower lows)\b", re.I), 'short'),
]

FOUR_HR_LONG_PAT = re.compile(r"\b(4h|4-hour|four hour).*long\b", re.I)
FOUR_HR_SHORT_PAT = re.compile(r"\b(4h|4-hour|four hour).*short\b", re.I)


def infer_bias(text: str) -> MissionBias:
    for pat, bias in BIAS_PATTERNS:
        if pat.search(text):
            return bias  # type: ignore
    return 'neutral'


def is_four_hour_long(text: str) -> bool:
    return bool(FOUR_HR_LONG_PAT.search(text))


def is_four_hour_short(text: str) -> bool:
    return bool(FOUR_HR_SHORT_PAT.search(text))
