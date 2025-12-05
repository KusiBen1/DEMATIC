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
    equipment_id: Optional[str] = None  # we can reuse from/to for this


def parse_timestamp(date_str: str, time_str: str) -> datetime:
    """
    Log format: 08-12-25 08:25:37.725
    (day-month-year hour:minute:second.milliseconds)
    """
    combined = f"{date_str} {time_str}"
    return datetime.strptime(combined, "%d-%m-%y %H:%M:%S.%f")


def parse_log(path: str) -> List[Event]:
    events: List[Event] = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Split into: [date, time, rest-of-message...]
            parts = line.split()
            if len(parts) < 3:
                continue  # malformed line

            date_str = parts[0]         # e.g. 08-12-25
            time_str = parts[1]         # e.g. 08:25:37.725
            msg_raw = " ".join(parts[2:])  # e.g. ~WMS1PLC1...ARRIVAL..NOTIPOINT01..NOTIPOINT02....10000000...##

            try:
                ts = parse_timestamp(date_str, time_str)
            except ValueError:
                # Skip lines with bad timestamps
                continue

            # Convert "....." filler into spaces, then split into tokens
            # Example msg_raw:
            #   ~PLC1WMS1...ARRIVAL..NOTIPOINT01..NOTIPOINT02....10000000...##
            # After replace & split:
            #   ["~PLC1WMS1", "ARRIVAL", "NOTIPOINT01", "NOTIPOINT02", "10000000", "##"]
            msg_clean = msg_raw.replace(".", " ")
            tokens = msg_clean.split()
            if len(tokens) < 3:
                continue

            direction = tokens[0]       # ~WMS1PLC1 or ~PLC1WMS1 (not used yet)
            msg_type = tokens[1]        # ARRIVAL, SETDEST, DESTREQ, LOCEXIT, ...

            # The pallet ID is always just before the final "##"
            pallet_id = None
            if len(tokens) >= 3:
                # tokens[-1] should be "##"
                if tokens[-1] == "##":
                    pallet_id = tokens[-2]
                else:
                    pallet_id = tokens[-1]

            from_loc: Optional[str] = None
            to_loc: Optional[str] = None

            # For most messages, tokens[2] is a location.
            # For ARRIVAL / SETDEST, we usually have both from & to.
            if msg_type in ("ARRIVAL", "SETDEST"):
                if len(tokens) >= 5:
                    # e.g. ARRIVAL FROM TO PALLET_ID ##
                    from_loc = tokens[2]
                    to_loc = tokens[3]
                elif len(tokens) >= 4:
                    from_loc = tokens[2]

            elif msg_type in ("DESTREQ", "LOCEXIT"):
                if len(tokens) >= 4:
                    from_loc = tokens[2]  # where the request/exit happened

            # We don't have a separate equipment_id in the log, but we can
            # treat the "to" location (or from location) as the equipment.
            equipment_id = to_loc or from_loc

            events.append(Event(
                timestamp=ts,
                message_type=msg_type,
                pallet_id=pallet_id,
                from_loc=from_loc,
                to_loc=to_loc,
                equipment_id=equipment_id,
            ))

    # Make sure events are ordered by time
    events.sort(key=lambda e: e.timestamp)
    return events
