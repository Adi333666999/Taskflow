from flask import Flask, jsonify, request
import psycopg2
import os

app = Flask(__name__)

# Connect to Neon cloud database
def get_db():
    conn = psycopg2.connect("postgresql://neondb_owner:npg_Sf7r9CUHInJM@ep-steep-sea-at7vqdmm-pooler.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
    return conn

# Create tasks table if not exists
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            done BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, done FROM tasks')
    rows = cursor.fetchall()
    tasks = [{'id': r[0], 'title': r[1], 'done': r[2]} for r in rows]
    cursor.close()
    conn.close()
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, done',
        (data['title'],)
    )
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'id': row[0], 'title': row[1], 'done': row[2]}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE tasks SET title=%s, done=%s WHERE id=%s RETURNING id, title, done',
        (data.get('title'), data.get('done'), task_id)
    )
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    if row is None:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify({'id': row[0], 'title': row[1], 'done': row[2]})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id=%s', (task_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Task deleted'}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
