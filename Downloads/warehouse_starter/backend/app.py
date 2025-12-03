from flask import Flask, jsonify, request
from datetime import datetime
import json
from pathlib import Path

from log_parser import parse_log
from simulation import Simulation

app = Flask(__name__)

BASE_DIR = Path(__file__).parent
LOG_PATH = BASE_DIR / "logs" / "warehouse.log"
LAYOUT_PATH = BASE_DIR / "layout.json"

LOG_PATH.parent.mkdir(exist_ok=True)
# create dummy log
if not LOG_PATH.exists():
    with open(LOG_PATH, "w") as f:
        f.write("2025-12-01T10:00:00,PALLET_MOVED,P1,IN_01,CONV_01,CONV_01\n")

events = parse_log(str(LOG_PATH))
sim = Simulation(events)

with open(LAYOUT_PATH, "r") as f:
    layout = json.load(f)

def parse_sim_time(param: str):
    if not param:
        return sim.end_time
    return datetime.fromisoformat(param)

@app.get("/api/layout")
def get_layout():
    return jsonify(layout)

@app.get("/api/state")
def get_state():
    t_param = request.args.get("time")
    t = parse_sim_time(t_param)
    state = sim.compute_state_at(t)
    return jsonify({
        "simTime": t.isoformat(),
        "pallets": list(state["pallets"].values()),
        "equipment": [
            {"id": eq_id, **eq_data}
            for eq_id, eq_data in state["equipment"].items()
        ],
    })

@app.get("/api/pallet/<pallet_id>/history")
def pallet_history(pallet_id):
    history = sim.pallet_history(pallet_id)
    return jsonify({"palletId": pallet_id, "events": history})

if __name__ == "__main__":
    app.run(debug=True)
