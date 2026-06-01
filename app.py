from flask import Flask, jsonify, request
from threading import Lock

app = Flask(__name__)

# In-memory storage for Stage 1 (no database yet)
tasks = []
next_id = 1
tasks_lock = Lock()

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Welcome to the Tasks API. Use /tasks to view data.'})

@app.route('/tasks', methods=['GET'])
def get_tasks():
    with tasks_lock:
        return jsonify(tasks)

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    with tasks_lock:
        task = _find_task(task_id)
        if task is None:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(task)

@app.route('/tasks', methods=['POST'])
def add_task():
    global next_id
    data = request.get_json()
    if not data or 'title' not in data or not data['title'].strip():
        return jsonify({'error': 'Valid title is required'}), 400
    
    with tasks_lock:
        task = {
            'id': next_id,
            'title': data['title'],
            'done': False
        }
        tasks.append(task)
        next_id += 1
    return jsonify(task), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request body'}), 400

    with tasks_lock:
        task = _find_task(task_id)
        if task is None:
            return jsonify({'error': 'Task not found'}), 404
        
        if 'title' in data:
            if not data['title'].strip():
                return jsonify({'error': 'Title cannot be empty'}), 400
            task['title'] = data['title']
            
        if 'done' in data:
            if not isinstance(data['done'], bool):
                return jsonify({'error': 'Done must be a boolean'}), 400
            task['done'] = data['done']
            
        return jsonify(task)

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    with tasks_lock:
        task = _find_task(task_id)
        if task is None:
            return jsonify({'error': 'Task not found'}), 404
        tasks.remove(task)
        return jsonify({'message': 'Task deleted'}), 200

def _find_task(task_id):
    """Helper to find a task by ID within the tasks list."""
    return next((t for t in tasks if t['id'] == task_id), None)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
