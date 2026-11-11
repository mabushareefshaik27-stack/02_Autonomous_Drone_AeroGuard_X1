import json
from flask import Flask, Response
from drone_engine.propulsion_power import PropulsionEngine
from gcs.server import SYSTEM, SYSTEM_LOCK

app = Flask(__name__)

@app.route("/api/drone/specs")
def specs():
    with SYSTEM_LOCK:
        aero = PropulsionEngine.calculate_aerodynamics(SYSTEM.config)
    return Response(json.dumps(aero, indent=2), mimetype="application/json")

