
from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import openai

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        return 'Invalid credentials'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        new_user = User(username=request.form['username'], password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return f"Welcome to ShellCoach, user ID: {session['user_id']}"


@app.route('/execute', methods=['POST'])
def execute():
    import subprocess, json
    cmd = request.get_json().get('command')
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=3).decode()
    except subprocess.CalledProcessError as e:
        result = e.output.decode()
    except Exception as ex:
        result = str(ex)

    # AI Explanation using OpenAI API
    explanation = ""
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful Linux tutor."},
                {"role": "user", "content": f"What does the following command do in Linux?

{cmd}"}
            ]
        )
        explanation = response['choices'][0]['message']['content']
    except Exception as e:
        explanation = "AI explanation not available."

    return json.dumps({'result': result, 'explanation': explanation})
def execute():
    import subprocess, json
    cmd = request.get_json().get('command')
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=3).decode()
    except subprocess.CalledProcessError as e:
        result = e.output.decode()
    except Exception as ex:
        result = str(ex)
    return json.dumps({'result': result})

if __name__ == '__main__':

    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=10000)
