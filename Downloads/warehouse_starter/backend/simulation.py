from datetime import datetime
from typing import Dict, List, Any
from log_parser import Event

class Simulation:
    def __init__(self, events: List[Event]):
        self.events = events
        self.start_time = events[0].timestamp if events else None
        self.end_time = events[-1].timestamp if events else None

    def _empty_state(self):
        return {"pallets": {}, "equipment": {}}

    def _ensure_equipment(self, state: Dict, eq_id: str):
        if eq_id not in state["equipment"]:
            state["equipment"][eq_id] = {
                "status": "ok",
                "lastFaultStart": None,
                "totalFaultSeconds": 0.0,
            }

    def compute_state_at(self, t: datetime) -> Dict[str, Any]:
        state = self._empty_state()
        for ev in self.events:
            if ev.timestamp > t:
                break

        if ev.message_type == "PALLET_MOVED" or ev.message_type == "ARRIVAL":
            # Treat ARRIVAL as a pallet moving to ev.to_loc
            if ev.pallet_id not in state["pallets"]:
                state["pallets"][ev.pallet_id] = {
                    "id": ev.pallet_id,
                    "currentLocation": None,
                    "lastUpdate": None,
                }
            state["pallets"][ev.pallet_id]["currentLocation"] = ev.to_loc or ev.from_loc
            state["pallets"][ev.pallet_id]["lastUpdate"] = ev.timestamp.isoformat()

        elif ev.message_type == "EQUIP_FAULT":
            if ev.equipment_id:
                    self._ensure_equipment(state, ev.equipment_id)
                    eq = state["equipment"][ev.equipment_id]
                    if eq["status"] != "fault":
                        eq["status"] = "fault"
                        eq["lastFaultStart"] = ev.timestamp

        elif ev.message_type == "EQUIP_RECOVER":
                if ev.equipment_id:
                    self._ensure_equipment(state, ev.equipment_id)
                    eq = state["equipment"][ev.equipment_id]
                    if eq["status"] == "fault" and eq["lastFaultStart"]:
                        eq["totalFaultSeconds"] += (ev.timestamp - eq["lastFaultStart"]).total_seconds()
                    eq["status"] = "ok"
                    eq["lastFaultStart"] = None

        for eq in state["equipment"].values():
            if eq["status"] == "fault" and eq["lastFaultStart"]:
                eq["totalFaultSeconds"] += (t - eq["lastFaultStart"]).total_seconds()

        return state

    def pallet_history(self, pallet_id: str) -> List[dict]:
        return [
            {
                "timestamp": ev.timestamp.isoformat(),
                "messageType": ev.message_type,
                "from": ev.from_loc,
                "to": ev.to_loc,
                "equipmentId": ev.equipment_id,
            }
            for ev in self.events if ev.pallet_id == pallet_id
        ]
