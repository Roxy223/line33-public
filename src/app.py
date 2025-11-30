# add to src/app.py (imports at top)
import os, json
from flask import Flask, render_template, request, jsonify, abort, url_for, redirect

app = Flask(__name__)
ROUTES_FILE = os.path.join(os.path.dirname(__file__), 'routes.json')

def load_all_routes():
    if not os.path.exists(ROUTES_FILE):
        return {}
    with open(ROUTES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_all_routes(data):
    with open(ROUTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# index route must pass routes (existing)
@app.route('/')
def index():
    routes = load_all_routes()
    # convert route dicts to expected structure if needed
    return render_template('index.html', routes=routes)

# view individual route page
@app.route('/route/<route_id>')
def view_route(route_id):
    routes = load_all_routes()
    route = routes.get(route_id)
    if not route:
        abort(404)
    # ensure stops list structure
    stops = route.get('stops', [])
    # normalize fields (time string and delay int)
    for s in stops:
        s.setdefault('name', '')
        s.setdefault('time', '00:00')
        s.setdefault('delay', 0)
    return render_template('route.html', route=route, route_id=route_id, stops=stops)

# create new route (index uses this)
@app.route('/api/route', methods=['POST'])
def api_create_route():
    data = request.get_json() or {}
    title = data.get('title', 'Untitled Route')
    stops = data.get('stops', [])
    routes = load_all_routes()
    # create a new ID: use incrementing integer string
    next_id = str(max((int(k) for k in routes.keys()), default=0) + 1)
    routes[next_id] = {'title': title, 'stops': stops}
    save_all_routes(routes)
    return jsonify({'ok': True, 'id': next_id})

# update entire route (autosave)
@app.route('/api/route/<route_id>', methods=['PUT'])
def api_update_route(route_id):
    data = request.get_json() or {}
    stops = data.get('stops')
    if stops is None:
        return jsonify({'error': 'no stops provided'}), 400
    routes = load_all_routes()
    if route_id not in routes:
        return jsonify({'error': 'route not found'}), 404
    # sanitize stops: ensure fields exist and proper types
    clean = []
    for s in stops:
        name = s.get('name', '')
        time = s.get('time', '00:00')
        try:
            delay = int(s.get('delay', 0))
        except Exception:
            delay = 0
        clean.append({'name': name, 'time': time, 'delay': delay})
    routes[route_id]['stops'] = clean
    save_all_routes(routes)
    return jsonify({'ok': True})

# optional: reset route (server side) if you prefer endpoint-based reset
@app.route('/api/route/<route_id>/reset', methods=['POST'])
def api_reset_route(route_id):
    routes = load_all_routes()
    if route_id not in routes:
        return jsonify({'error': 'route not found'}), 404
    # reset delays to 0
    for s in routes[route_id].get('stops', []):
        s['delay'] = 0
    save_all_routes(routes)
    return jsonify({'ok': True})
