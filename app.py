from flask import Flask, render_template, request, jsonify, session
import openai
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'shellcoach_secret')

# Simulated Virtual File System (VFS)
vfs = {
    "welcome.txt": "Welcome to ShellCoach Technologies!",
    "info.txt": "This is your AI-powered Linux simulator."
}

@app.route('/')
def index():
    if 'username' not in session:
        session['username'] = 'student'
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.get_json()
    command = data.get('command', '')
    args = command.strip().split()
    
    if not args:
        return jsonify({'output': ''})

    cmd = args[0]
    args = args[1:]

    output = ""

    if cmd == "touch" and args:
        vfs[args[0]] = ""
        output = f"Created file: {args[0]}"
    elif cmd == "echo" and args:
        output = " ".join(args)
    elif cmd == "mkdir" and args:
        vfs[args[0] + "/"] = "<DIR>"
        output = f"Directory created: {args[0]}"
    elif cmd == "cat" and args:
        content = vfs.get(args[0], None)
        output = content if content is not None else f"No such file: {args[0]}"
    elif cmd == "rm" and args:
        if args[0] in vfs:
            del vfs[args[0]]
            output = f"Removed {args[0]}"
        else:
            output = f"No such file: {args[0]}"
    elif cmd in ["la", "ls"]:
        output = "\n".join(vfs.keys())
    elif cmd == "pwd":
        output = "/home/student"
    elif cmd == "whoami":
        output = session.get('username', 'unknown')
    else:
        output = f"Command not found: {cmd}"

    return jsonify({'output': output})

@app.route('/explain', methods=['POST'])
def explain_command():
    data = request.get_json()
    command = data.get('command', '')

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert Linux tutor."},
                {"role": "user", "content": f"Explain what this Linux command does: {command}"}
            ]
        )
        explanation = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        explanation = f"AI explanation not available. Error: {str(e)}"

    return jsonify({'explanation': explanation})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
