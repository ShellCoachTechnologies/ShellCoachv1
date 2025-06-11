from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import openai
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'shellcoach_secret')
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Simulated Virtual File System (VFS)
vfs = {
    "/": ["welcome.txt", "info.txt", "home/"],
    "/home": []
}
current_dir = {"path": "/"}

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
    command = data.get('command', '')
    args = command.strip().split()

    if not args:
        return jsonify({'output': ''})

    cmd = args[0]
    args = args[1:]
    path = current_dir["path"]
    output = ""

    if cmd == "touch" and args:
        vfs[path].append(args[0])
        output = f"Created file: {args[0]}"
    elif cmd == "mkdir" and args:
        dir_name = args[0]
        dir_path = f"{path.rstrip('/')}/{dir_name}"
        vfs[dir_path] = []
        vfs[path].append(dir_name + "/")
        output = f"Directory created: {dir_name}"
    elif cmd == "cd" and args:
        new_path = f"{path.rstrip('/')}/{args[0]}".replace("//", "/")
        if new_path in vfs:
            current_dir["path"] = new_path
            output = f"Changed directory to {args[0]}"
        else:
            output = f"No such directory: {args[0]}"
    elif cmd == "ls":
        output = "\n".join(vfs[path])
    elif cmd == "pwd":
        output = path
    elif cmd == "whoami":
        output = session.get('username', 'unknown')
    elif cmd == "echo" and args:
        output = " ".join(args)
    elif cmd == "cat" and args:
        file_name = args[0]
        if file_name in vfs[path]:
            output = f"Reading file: {file_name}"
        else:
            output = f"No such file: {file_name}"
    else:
        output = f"Command not found: {cmd}"

    return jsonify({'output': output})

@app.route('/explain', methods=['POST'])
def explain_command():
    data = request.get_json()
    command = data.get('command', '')

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful Linux tutor."},
                {"role": "user", "content": f"Explain what this Linux command does: {command}"}
            ]
        )
        explanation = response.choices[0].message.content.strip()
    except Exception as e:
        explanation = f"AI explanation not available. Error: {str(e)}"

    return jsonify({'explanation': explanation})
