# File: frontend.py
from flask import Flask, render_template, redirect, url_for, request, jsonify
import requests
import os
import json
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# API endpoints (service.py) base URL
API_URL = 'http://localhost:5000'

# Helper to fetch projects
def fetch_projects():
    resp = requests.get(f"{API_URL}/projects")
    resp.raise_for_status()
    return resp.json()

@app.route('/')
def index():
    projects = fetch_projects()
    return render_template('index.html', projects=projects)

@app.route('/start/<int:proj_id>')
def start(proj_id):
    # Register start time in session file (simple JSON)
    session_file = 'running.json'
    data = {'project_id': proj_id, 'start_time': datetime.now().isoformat()}
    with open(session_file, 'w') as f:
        json.dump(data, f)
    return redirect(url_for('index'))

@app.route('/stop')
def stop():
    # Read running.json
    session_file = 'running.json'
    if os.path.exists(session_file):
        with open(session_file) as f:
            data = json.load(f)
        # Compute elapsed
        start = datetime.fromisoformat(data['start_time'])
        elapsed = (datetime.now() - start).total_seconds() / 3600
        record = {
            'project_id': data['project_id'],
            'date': datetime.now().date().isoformat(),
            'hours': round(elapsed, 2),
            'revenue': 0.0
        }
        # Post to API
        requests.post(f"{API_URL}/records", json=record)
        os.remove(session_file)
    return redirect(url_for('index'))

@app.route('/timer')
def timer_fragment():
    # Return HTMX fragment showing elapsed time
    session_file = 'running.json'
    if not os.path.exists(session_file):
        return ''
    with open(session_file) as f:
        data = json.load(f)
    start = datetime.fromisoformat(data['start_time'])
    elapsed = datetime.now() - start
    mins, secs = divmod(int(elapsed.total_seconds()), 60)
    return render_template('timer.html', mins=mins, secs=secs)

if __name__ == '__main__':
    app.run(port=8000, debug=True)
