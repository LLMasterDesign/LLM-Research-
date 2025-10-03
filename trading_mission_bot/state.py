from dataclasses import dataclass, asdict
from typing import Optional, Literal
import json
import os
from datetime import date

MissionBias = Literal['long', 'short', 'neutral']


@dataclass
class MissionState:
    day: str
    bias: MissionBias
    reason: str
    rules: dict
    locked: bool


class StateStore:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def load(self) -> Optional[MissionState]:
        if not os.path.exists(self.path):
            return None
        with open(self.path, 'r') as f:
            data = json.load(f)
        return MissionState(**data)

    def save(self, state: MissionState) -> None:
        with open(self.path, 'w') as f:
            json.dump(asdict(state), f, indent=2)

    def reset_if_new_day(self) -> MissionState:
        today = date.today().isoformat()
        current = self.load()
        if current and current.day == today:
            return current
        fresh = MissionState(
            day=today,
            bias='neutral',
            reason='New day: awaiting Phames bias.',
            rules={
                'no_short_if_4h_long': True,
                'no_mission_change_midday': True
            },
            locked=False,
        )
        self.save(fresh)
        return fresh
