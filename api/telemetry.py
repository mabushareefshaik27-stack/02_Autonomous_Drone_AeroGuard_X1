import json
from flask import Flask, Response
from gcs.server import SYSTEM, SYSTEM_LOCK

app = Flask(__name__)

@app.route("/api/drone/telemetry")
def telemetry():
    with SYSTEM_LOCK:
        data = SYSTEM.get_full_telemetry()
    return Response(json.dumps(data, indent=2), mimetype="application/json")

