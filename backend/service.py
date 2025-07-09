from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import json

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
DB_PATH = os.path.join(BASE_DIR, '..', 'storage', 'projects.db')
JSON_PATH = os.path.join(BASE_DIR, '..', 'storage', 'daily_data.json')

# Ensure storage exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS project_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        date TEXT,
        hours REAL,
        revenue REAL,
        FOREIGN KEY(project_id) REFERENCES projects(id)
    )
''')
conn.commit()
conn.close()

# JSON helper
def load_temp_data():
    try:
        with open(JSON_PATH, 'r') as f:
            return json.load(f)
    except:
        return []

def save_temp_data(data):
    with open(JSON_PATH, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/projects', methods=['GET', 'POST', 'DELETE'])
def projects():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if request.method == 'GET':
        rows = c.execute('SELECT id, name FROM projects').fetchall()
        conn.close()
        return jsonify([{'id': r[0], 'name': r[1]} for r in rows])
    data = request.json
    if request.method == 'POST':
        c.execute('INSERT OR IGNORE INTO projects(name) VALUES(?)', (data['name'],))
        conn.commit()
        conn.close()
        return jsonify({'status': 'created'})
    if request.method == 'DELETE':
        c.execute('DELETE FROM projects WHERE id = ?', (data['id'],))
        conn.commit()
        conn.close()
        return jsonify({'status': 'deleted'})

@app.route('/records', methods=['GET', 'POST'])
def records():
    if request.method == 'GET':
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        rows = c.execute(
            'SELECT p.name, r.date, r.hours, r.revenue FROM project_records r '
            'JOIN projects p ON r.project_id = p.id'
        ).fetchall()
        conn.close()
        return jsonify([{'project': r[0], 'date': r[1], 'hours': r[2], 'revenue': r[3]} for r in rows])

    rec = request.json

    if all(k in rec for k in ('hours', 'minutes', 'seconds')):
        decimal_hours = round(
            rec['hours'] + rec['minutes'] / 60 + rec['seconds'] / 3600,
            6
        )
    else:
        decimal_hours = rec.get('decimal_hours', 0.0)

    record_to_store = {
        'project_id': rec['project_id'],
        'date': rec['date'],
        'hours': decimal_hours,
        'revenue': rec['revenue'],
        'raw_hours': rec.get('hours', 0),
        'raw_minutes': rec.get('minutes', 0),
        'raw_seconds': rec.get('seconds', 0)
    }

    temp = load_temp_data()
    temp.append(record_to_store)
    save_temp_data(temp)
    return jsonify({'status': 'temp_saved'})

@app.route('/commit', methods=['POST'])
def commit():
    temp = load_temp_data()
    if not temp:
        return jsonify({'migrated': 0})
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for rec in temp:
        c.execute(
            'INSERT INTO project_records (project_id, date, hours, revenue) VALUES (?, ?, ?, ?)',
            (rec['project_id'], rec['date'], rec['hours'], rec['revenue'])
        )
    conn.commit()
    conn.close()
    save_temp_data([])
    return jsonify({'migrated': len(temp)})

@app.route('/dashboard', methods=['GET'])
def dashboard():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        'SELECT p.name, r.date, r.hours, r.revenue FROM project_records r '
        'JOIN projects p ON r.project_id = p.id'
    ).fetchall()
    conn.close()

    # Committed records con h, m, s
    result = []
    for r in rows:
        total_seconds = int(r[2] * 3600)
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        result.append({
            'project': r[0],
            'date': r[1],
            'hours': h,
            'minutes': m,
            'seconds': s,
            'revenue': r[3]
        })

    temp = load_temp_data()
    # Obtener proyectos
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    proyectos = {r[0]: r[1] for r in c.execute('SELECT id, name FROM projects')}
    conn.close()

    for rec in temp:
        result.append({
            'project': proyectos.get(rec['project_id'], 'Unknown'),
            'date': rec['date'],
            'hours': rec.get('raw_hours', 0),
            'minutes': rec.get('raw_minutes', 0),
            'seconds': rec.get('raw_seconds', 0),
            'revenue': rec.get('revenue', 0.0)
        })

    return jsonify(result)

if __name__ == '__main__':
    app.run(port=5000)
