import os
from flask import Flask, send_file, abort

app = Flask(__name__)

PPTX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'AeroGuard_X1_Presentation.pptx'))

@app.route('/api/drone/download-pptx')
def download_pptx():
    if not os.path.exists(PPTX_PATH):
        abort(404)
    return send_file(PPTX_PATH, as_attachment=True, download_name='AeroGuard_X1_Presentation.pptx')

