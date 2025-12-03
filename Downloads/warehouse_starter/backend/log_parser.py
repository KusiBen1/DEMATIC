from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Event:
    timestamp: datetime
    message_type: str
    pallet_id: Optional[str] = None
    from_loc: Optional[str] = None
    to_loc: Optional[str] = None
    equipment_id: Optional[str] = None

def parse_timestamp(raw: str) -> datetime:
    return datetime.fromisoformat(raw)

def parse_log(path: str) -> List[Event]:
    events = []
    with open(path, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            if len(parts) < 2:
                continue

            ts = parse_timestamp(parts[0])
            msg = parts[1]

            pallet = parts[2] if len(parts) > 2 else None
            from_loc = parts[3] if len(parts) > 3 else None
            to_loc = parts[4] if len(parts) > 4 else None
            eq = parts[5] if len(parts) > 5 else None

            events.append(Event(ts, msg, pallet, from_loc, to_loc, eq))

    events.sort(key=lambda e: e.timestamp)
    return events
