from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Username and password are required.")
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken.")
            return redirect(url_for('register'))

        try:
            hashed_pw = generate_password_hash(password, method='sha256')
            new_user = User(username=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for('login'))
        except Exception as e:
            app.logger.error(f"Registration error: {e}")
            flash("An error occurred during registration.")
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Login successful.")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return "Welcome to your dashboard!"
    else:
        flash("Please log in first.")
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
