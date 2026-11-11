import json, time, threading
from flask import Flask, Response, stream_with_context
from gcs.server import SYSTEM, SYSTEM_LOCK

app = Flask(__name__)

def telemetry_stream():
    while True:
        with SYSTEM_LOCK:
            telemetry = SYSTEM.get_full_telemetry()
        payload = f"data: {json.dumps(telemetry)}\n\n"
        yield payload
        time.sleep(0.08)  # ~12.5 Hz

@app.route('/api/drone/events')
def events():
    return Response(stream_with_context(telemetry_stream()), mimetype='text/event-stream')

