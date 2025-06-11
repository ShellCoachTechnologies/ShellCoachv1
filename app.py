from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import openai
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'shellcoach_secret')
openai.api_key = os.environ.get("OPENAI_API_KEY")

COMMAND_OUTPUTS = {"cd": "Changed directory (simulated).", "ls": "file1.txt  file2.txt  dir1/", "pwd": "/home/shellcoach", "mkdir": "Directory created (simulated).", "rmdir": "Directory removed (simulated).", "touch": "File created (simulated).", "echo": "Echoed text.", "cat": "Simulated file content.", "cp": "File copied (simulated).", "mv": "File moved (simulated).", "rm": "File removed (simulated).", "whoami": "shellcoach_user", "chmod": "Permissions changed (simulated).", "chown": "Ownership changed (simulated).", "clear": "", "man": "Simulated manual entry.", "head": "First 10 lines of file (simulated).", "tail": "Last 10 lines of file (simulated).", "grep": "Search results (simulated).", "find": "./file1.txt", "locate": "/usr/bin/file1.txt", "history": "1. ls\n2. pwd\n3. echo Hello", "uname": "Linux", "df": "Filesystem usage (simulated).", "du": "Disk usage (simulated).", "top": "CPU usage (simulated).", "ps": "PID TTY TIME CMD", "kill": "Process terminated (simulated).", "nano": "Opened nano editor (simulated).", "vi": "Opened vi editor (simulated).", "date": "Tue Jun 10 12:00:00 UTC 2025", "cal": "June 2025 calendar (simulated).", "hostname": "shellcoach.local", "ping": "Pinging google.com... (simulated)", "tar": "Archive created (simulated).", "zip": "Files compressed (simulated).", "unzip": "Files extracted (simulated).", "ssh": "Connected via SSH (simulated).", "scp": "File transferred via SCP (simulated).", "wget": "Downloaded file (simulated).", "curl": "Fetched URL data (simulated).", "su": "Switched user (simulated).", "sudo": "Superuser command executed (simulated).", "ifconfig": "IP configuration (simulated).", "netstat": "Network stats (simulated).", "env": "ENV variables (simulated).", "export": "Environment variable set.", "alias": "alias ll='ls -la'", "uptime": "12:34:56 up 3 days", "sleep": "Sleeping... done (simulated).", "which": "/usr/bin/which"}

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
    raw = data.get('command', '').strip()
    parts = raw.split()
    cmd = parts[0] if parts else ""
    output = COMMAND_OUTPUTS.get(cmd, f"Command not found: {cmd}")
    return jsonify({ 'output': output })

@app.route('/explain', methods=['POST'])
def explain_command():
    data = request.get_json()
    command = data.get('command', '')
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Linux tutor."},
                {"role": "user", "content": f"Explain this Linux command: {command}"}
            ]
        )
        explanation = response.choices[0].message.content.strip()
    except Exception as e:
        explanation = f"AI explanation not available. Error: {str(e)}"
    return jsonify({ 'explanation': explanation })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
