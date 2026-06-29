from flask import Flask, request, render_template_string, redirect, url_for, jsonify, session
import requests
import time
import threading
from datetime import datetime
import os
import uuid
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

tasks = {}
total_messages_sent = 0
logs = []

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>༒ᴍʀ ꜱatyam༒⚜️⚜️</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fbc2eb 100%);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 30px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        h1 { text-align: center; color: #ff6b6b; font-size: 28px; margin-bottom: 10px; }
        .user-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .user-id {
            font-family: monospace;
            font-size: 14px;
            background: rgba(0,0,0,0.3);
            padding: 8px 15px;
            border-radius: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 20px;
            text-align: center;
            color: white;
        }
        .stat-card .value { font-size: 32px; font-weight: bold; }
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .form-section, .tasks-section {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 20px;
        }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: bold; }
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ff9a9e;
            border-radius: 25px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            width: 100%;
        }
        .btn-stop-task {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            width: auto;
        }
        .task-card {
            background: white;
            border-left: 4px solid #00ff00;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 10px;
        }
        .task-card.stopped { border-left-color: #ff4444; }
        .log-container {
            background: #1e1e1e;
            color: #00ff00;
            border-radius: 15px;
            padding: 15px;
            height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
        }
        .log-success { color: #00ff00; }
        .log-error { color: #ff4444; }
        @media (max-width: 768px) { .main-content { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚜️༒ᴍʀ ꜱatyam༒❤️🖤⚜️</h1>
        <div class="user-section">
            <div class="user-info">
                <span>👤 YOUR USER ID:</span>
                <span class="user-id" id="userId">{{ session.get('user_id', 'Not set') }}</span>
            </div>
            <button onclick="regenerateUserId()" style="width: auto; padding: 8px 20px;">🔄 NEW ID</button>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><h3>📊 TOTAL TASKS</h3><div class="value" id="totalTasks">0</div></div>
            <div class="stat-card"><h3>✅ ACTIVE TASKS</h3><div class="value" id="activeTasks">0</div></div>
            <div class="stat-card"><h3>📨 TOTAL MESSAGES</h3><div class="value" id="totalMessages">{{ total_messages }}</div></div>
            <div class="stat-card"><h3>👥 YOUR TASKS</h3><div class="value" id="userTasks">0</div></div>
        </div>
        <div class="main-content">
            <div class="form-section">
                <h3>🚀 CREATE NEW TASK</h3>
                <form id="attackForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>🤡 GROUP UID</label>
                        <input type="text" name="threadId" required placeholder="Enter conversation ID">
                    </div>
                    <div class="form-group">
                        <label>📝 TOKEN FILE</label>
                        <input type="file" name="txtFile" accept=".txt" required>
                    </div>
                    <div class="form-group">
                        <label>💬 MESSAGE FILE</label>
                        <input type="file" name="messagesFile" accept=".txt" required>
                    </div>
                    <div class="form-group">
                        <label>🦇 TARGET NAME</label>
                        <input type="text" name="kidx" required placeholder="Enter target name">
                    </div>
                    <div class="form-group">
                        <label>⏰ SPEED (seconds)</label>
                        <input type="number" name="time" value="60" required>
                    </div>
                    <button type="submit">🚀 START TASK</button>
                </form>
            </div>
            <div class="tasks-section">
                <h3>📋 YOUR ACTIVE TASKS</h3>
                <div id="tasksList"><div class="no-tasks">No active tasks. Create one above!</div></div>
            </div>
        </div>
        <div class="log-container" id="logContainer">
            <div class="log-entry">[*] System Ready - Task System Active</div>
        </div>
    </div>
    <script>
        let userId = '{{ session.get("user_id", "") }}';
        function regenerateUserId() {
            fetch('/regenerate_user_id', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.user_id) {
                        document.getElementById('userId').innerText = data.user_id;
                        userId = data.user_id;
                        loadTasks(); loadStats();
                    }
                });
        }
        document.getElementById('attackForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const response = await fetch('/api/tasks/create', { method: 'POST', body: formData });
            const data = await response.json();
            if (data.success) {
                alert('Task created! ID: ' + data.task_id);
                e.target.reset();
                loadTasks(); loadStats();
            } else { alert('Error: ' + data.error); }
        });
        async function stopTask(taskId) {
            if (!confirm('Stop task ' + taskId + '?')) return;
            const response = await fetch('/api/tasks/' + taskId + '/stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId })
            });
            const data = await response.json();
            if (data.success) { loadTasks(); loadStats(); }
        }
        async function loadTasks() {
            const response = await fetch('/api/tasks');
            const tasks = await response.json();
            const userTasks = tasks.filter(t => t.owner_id === userId);
            document.getElementById('userTasks').innerText = userTasks.length;
            const tasksList = document.getElementById('tasksList');
            if (userTasks.length === 0) { tasksList.innerHTML = '<div class="no-tasks">No active tasks.</div>'; return; }
            tasksList.innerHTML = userTasks.map(task => `
                <div class="task-card ${task.active ? '' : 'stopped'}">
                    <div><strong>ID:</strong> ${task.task_id} | <strong>Target:</strong> ${task.target_name}</div>
                    <div><strong>Messages:</strong> ${task.messages_sent} | <strong>Status:</strong> ${task.active ? 'ACTIVE' : 'STOPPED'}</div>
                    ${task.active ? `<button class="btn-stop-task" onclick="stopTask('${task.task_id}')">STOP</button>` : ''}
                </div>
            `).join('');
        }
        async function loadStats() {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            document.getElementById('totalTasks').innerText = stats.total_tasks;
            document.getElementById('activeTasks').innerText = stats.active_tasks;
            document.getElementById('totalMessages').innerText = stats.total_messages;
        }
        function fetchLogs() {
            fetch('/logs').then(r => r.json()).then(data => {
                const logContainer = document.getElementById('logContainer');
                logContainer.innerHTML = data.logs.map(log => `<div class="log-entry ${log.type}">${log.message}</div>`).join('');
            });
        }
        setInterval(loadTasks, 3000); setInterval(loadStats, 2000); setInterval(fetchLogs, 2000);
        loadTasks(); loadStats(); fetchLogs();
    </script>
</body>
</html>
"""

def add_log(message, log_type="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    logs.append({'message': f'[{timestamp}] {message}', 'type': log_type})
    if len(logs) > 100: logs.pop(0)

def attack_worker(task_id, thread_id, mn, time_interval, access_tokens, messages, owner_id):
    global total_messages_sent
    task_info = tasks.get(task_id)
    if not task_info: return
    num_comments = len(messages)
    max_tokens = len(access_tokens)
    post_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
    message_index = 0
    add_log(f"Task {task_id} started by {owner_id}", "success")
    while task_info['active']:
        try:
            token_index = message_index % max_tokens
            access_token = access_tokens[token_index]
            message = messages[message_index % num_comments].strip()
            response = requests.post(post_url, json={'access_token': access_token, 'message': mn + ' ' + message}, headers=headers, timeout=10)
            if response.ok:
                total_messages_sent += 1
                task_info['total_messages'] += 1
                add_log(f"✅ Task {task_id} | Msg #{task_info['total_messages']}", "success")
            else:
                add_log(f"❌ Task {task_id} FAILED | Error: {response.status_code}", "error")
            message_index += 1
            time.sleep(time_interval)
        except Exception as e:
            add_log(f"Task {task_id} Error: {str(e)}", "error")
            time.sleep(30)
    add_log(f"Task {task_id} stopped", "info")

@app.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())[:8]
    return render_template_string(HTML_TEMPLATE, total_messages=total_messages_sent, session=session)

@app.route('/regenerate_user_id', methods=['POST'])
def regenerate_user_id():
    session['user_id'] = str(uuid.uuid4())[:8]
    return jsonify({'user_id': session['user_id']})

@app.route('/api/tasks/create', methods=['POST'])
def create_task():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())[:8]
    try:
        thread_id = request.form.get('threadId')
        kidx = request.form.get('kidx')
        time_interval = int(request.form.get('time', 60))
        token_file = request.files.get('txtFile')
        messages_file = request.files.get('messagesFile')
        if not thread_id or not kidx or not token_file or not messages_file:
            return jsonify({'success': False, 'error': 'Missing required fields'})
        tokens = token_file.read().decode('utf-8').splitlines()
        tokens = [t.strip() for t in tokens if t.strip()]
        messages = messages_file.read().decode('utf-8').splitlines()
        messages = [m.strip() for m in messages if m.strip()]
        if not tokens or not messages:
            return jsonify({'success': False, 'error': 'Files are empty'})
        task_id = str(uuid.uuid4())[:8]
        tasks[task_id] = {
            'task_id': task_id, 'owner_id': session['user_id'], 'thread_id': thread_id,
            'target_name': kidx, 'duration': time_interval, 'active': True, 'total_messages': 0
        }
        thread = threading.Thread(target=attack_worker, args=(task_id, thread_id, kidx, time_interval, tokens, messages, session['user_id']))
        thread.daemon = True
        thread.start()
        return jsonify({'success': True, 'task_id': task_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/tasks/<task_id>/stop', methods=['POST'])
def stop_task(task_id):
    data = request.get_json()
    user_id = data.get('user_id')
    if task_id not in tasks:
        return jsonify({'success': False, 'error': 'Task not found'})
    if tasks[task_id]['owner_id'] != user_id:
        return jsonify({'success': False, 'error': 'You can only stop your own tasks'})
    tasks[task_id]['active'] = False
    return jsonify({'success': True})

@app.route('/api/tasks')
def get_tasks():
    task_list = []
    for task_id, task in tasks.items():
        task_list.append({
            'task_id': task['task_id'], 'owner_id': task['owner_id'],
            'target_name': task['target_name'], 'messages_sent': task['total_messages'],
            'duration': task['duration'], 'active': task['active']
        })
    return jsonify(task_list)

@app.route('/api/stats')
def get_stats():
    active_tasks = sum(1 for t in tasks.values() if t['active'])
    return jsonify({'total_tasks': len(tasks), 'active_tasks': active_tasks, 'total_messages': total_messages_sent})

@app.route('/logs')
def get_logs():
    return jsonify({'logs': logs[-50:]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=20985, debug=False)