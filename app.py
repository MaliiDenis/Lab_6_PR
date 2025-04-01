from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import sqlite3
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
socketio = SocketIO(app)  # Инициализация SocketIO

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        text TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Получение всех задач
def get_all_tasks():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = [{"id": row[0], "text": row[1]} for row in cursor.fetchall()]
    conn.close()
    return tasks

# Добавление задачи
def add_task_to_db(text):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (text) VALUES (?)", (text,))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

# Удаление задачи
def delete_task_from_db(task_id):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# Маршрут для отображения index.html
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# API: Получение всех задач
@app.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = get_all_tasks()
    return jsonify(tasks)

# API: Добавление новой задачи
@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Text is required"}), 400
    text = data["text"]
    task_id = add_task_to_db(text)
    # Отправка обновления всем клиентам через WebSocket
    socketio.emit('task_added', {"id": task_id, "text": text}, broadcast=True)
    return jsonify({"id": task_id, "text": text}), 201

# API: Удаление задачи
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    delete_task_from_db(task_id)
    # Отправка обновления всем клиентам через WebSocket
    socketio.emit('task_deleted', {"id": task_id}, broadcast=True)
    return jsonify({"message": "Task deleted"})

# API: Отправка списка задач по email (из Лаб. №4)
@app.route('/send-email', methods=['POST'])
def send_email():
    tasks = get_all_tasks()
    email_body = "Ваш список задач:\n\n"
    for task in tasks:
        email_body += f"{task['id']}. {task['text']}\n"

    sender_email = "memyselfff7@gmail.com"  # Замени на свой email
    receiver_email = request.json.get("email")
    password = "sxxdgqjkuejwxzqf"  # Замени на свой пароль приложения

    if not receiver_email:
        return jsonify({"error": "Email is required"}), 400

    msg = MIMEText(email_body)
    msg['Subject'] = 'Ваш список задач из ToDo List'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)