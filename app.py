
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os, json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'shellcoach_secret_key'

USER_DATA_DIR = 'user_data'
os.makedirs(USER_DATA_DIR, exist_ok=True)

def get_user_dir():
    if 'username' not in session:
        return None
    user_dir = os.path.join(USER_DATA_DIR, session['username'])
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def load_vfs():
    user_dir = get_user_dir()
    if not user_dir:
        return {}
    vfs_path = os.path.join(user_dir, 'vfs.json')
    if os.path.exists(vfs_path):
        with open(vfs_path) as f:
            return json.load(f)
    return {}

def save_vfs(vfs):
    user_dir = get_user_dir()
    if user_dir:
        with open(os.path.join(user_dir, 'vfs.json'), 'w') as f:
            json.dump(vfs, f)

def log_command(command):
    user_dir = get_user_dir()
    if user_dir:
        history_path = os.path.join(user_dir, 'history.json')
        history = []
        if os.path.exists(history_path):
            with open(history_path) as f:
                history = json.load(f)
        history.append({"cmd": command, "time": datetime.utcnow().isoformat()})
        with open(history_path, 'w') as f:
            json.dump(history, f)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    vfs = load_vfs()
    return render_template('dashboard.html', vfs=vfs)




import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_ai_explanation(command):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert Linux instructor. Explain Linux commands simply."},
                {"role": "user", "content": f"What does this command do? '{command}'"}
            ],
            max_tokens=100
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"⚠️ AI explanation error: {str(e)}"

@app.route('/execute', methods=['POST'])
def execute():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'})
    command = request.json.get('command')
    explain = request.json.get('explain')
    log_command(command)
    vfs = load_vfs()
    output = f"$ {command}"
    parts = command.strip().split()
    if not parts:
        return jsonify({'output': ''})
    cmd = parts[0]
    args = parts[1:]

    if cmd == "touch" and args:
        vfs[args[0]] = ""
        output = f"Created file: {args[0]}"
    elif cmd == "mkdir" and args:
        vfs[args[0] + "/"] = {}
        output = f"Created directory: {args[0]}"
    elif cmd == "rm" and args:
        removed = vfs.pop(args[0], None)
        output = f"Removed: {args[0]}" if removed is not None else f"No such file: {args[0]}"
    elif cmd == "cat" and args:
        content = vfs.get(args[0], None)
        output = content if content is not None else f"No such file: {args[0]}"
    elif cmd == "echo" and args:
        output = " ".join(args)
    elif cmd in ["la", "ls"]:
        output = "
".join(vfs.keys())
    elif cmd == "whoami":
        output = session.get('username', 'unknown')
    else:
        output = f"Command not recognized: {command}"

    save_vfs(vfs)

    if explain:
        ai_explanation = get_ai_explanation(command)
        output += f"

💡 ShellCoach AI: {ai_explanation}"

    return jsonify({'output': output})


    command = request.json.get('command')
    log_command(command)
    vfs = load_vfs()
    output = f"$ {command}"
    parts = command.strip().split()
    if not parts:
        return jsonify({'output': ''})
    cmd = parts[0]
    args = parts[1:]

    if cmd == "touch" and args:
        vfs[args[0]] = ""
        output = f"Created file: {args[0]}"
    elif cmd == "mkdir" and args:
        vfs[args[0] + "/"] = {}
        output = f"Created directory: {args[0]}"
    elif cmd == "rm" and args:
        removed = vfs.pop(args[0], None)
        output = f"Removed: {args[0]}" if removed is not None else f"No such file: {args[0]}"
    elif cmd == "cat" and args:
        content = vfs.get(args[0], None)
        output = content if content is not None else f"No such file: {args[0]}"
    else:
        output = f"Executed: {command}"

    save_vfs(vfs)
    return jsonify({'output': output})

    command = request.json.get('command')
    log_command(command)
    response = f"Executed: {command}"
    vfs = load_vfs()
    if command.startswith("touch "):
        filename = command.split()[1]
        vfs[filename] = ""
        save_vfs(vfs)
    return jsonify({'output': response})


@app.route('/instructor', methods=['GET', 'POST'])
def instructor():
    if request.method == 'POST':
        password = request.form.get('password')
        if password != 'shellcoach_admin':
            return render_template('instructor_login.html', error='Invalid password')
        session['instructor'] = True
        return redirect(url_for('instructor_dashboard'))

    return render_template('instructor_login.html')

@app.route('/instructor/dashboard')
def instructor_dashboard():
    if not session.get('instructor'):
        return redirect(url_for('instructor'))
    users = os.listdir(USER_DATA_DIR)
    data = []
    for user in users:
        user_dir = os.path.join(USER_DATA_DIR, user)
        history_file = os.path.join(user_dir, 'history.json')
        cmd_count = 0
        last_cmd_time = 'N/A'
        if os.path.exists(history_file):
            with open(history_file) as f:
                history = json.load(f)
                cmd_count = len(history)
                if history:
                    last_cmd_time = history[-1]['time']
        data.append({"user": user, "commands": cmd_count, "last_active": last_cmd_time})
    return render_template('instructor.html', data=data)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
