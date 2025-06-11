from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import pexpect
import openai

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "shellcoach_secret")
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/")
def index():
    if 'username' not in session:
        return redirect(url_for("login"))
    if 'cwd' not in session:
        session['cwd'] = os.getcwd()
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["username"] = request.form["username"]
        session["cwd"] = os.getcwd()
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/execute", methods=["POST"])
def execute():
    from flask import request
    cmd = request.json.get("command", "")
    cwd = session.get("cwd", os.getcwd())

    # Special handling for cd to persist it
    if cmd.startswith("cd "):
        try:
            new_dir = cmd.split(" ", 1)[1].strip()
            new_path = os.path.abspath(os.path.join(cwd, new_dir))
            if os.path.isdir(new_path):
                session["cwd"] = new_path
                return jsonify({"output": f"Changed directory to {new_dir}"})
            else:
                return jsonify({"output": f"No such directory: {new_dir}"})
        except Exception as e:
            return jsonify({"output": f"Error changing directory: {str(e)}"})

    try:
        shell = pexpect.spawn("/bin/bash", ["-c", cmd], cwd=session["cwd"], timeout=2)
        shell.expect(pexpect.EOF)
        output = shell.before.decode(errors="ignore")
    except Exception as e:
        output = f"Error: {str(e)}"

    return jsonify({"output": output})

@app.route("/explain", methods=["POST"])
def explain_command():
    data = request.get_json()
    command = data.get("command", "")
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
    return jsonify({"explanation": explanation})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
