from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import logging

# Import Blueprints
from modules.ai_resume_screening import ai_resume_screening_bp, ensure_upload_folder
from modules.srb import srb_bp, init_srb_db
from modules.learning import learning_bp
from modules.courses import courses_bp  # Import courses blueprint

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:AMANSequel0307aman@localhost/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'

# ✅ Ensure the uploads folder exists
ensure_upload_folder(app.config['UPLOAD_FOLDER'])

# Register Blueprints
app.register_blueprint(ai_resume_screening_bp, url_prefix='/ai')
app.register_blueprint(srb_bp, url_prefix='/smart-resume')
app.register_blueprint(learning_bp, url_prefix='/learning')
app.register_blueprint(courses_bp, url_prefix='/courses')  # Register courses blueprint

# Initialize the SRB database
init_srb_db()

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

# Create DB tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def intro():
    return render_template('intro.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"success": False, "message": "Email already exists! Please login or use another email."})

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"success": True, "message": "Signup successful! Please login."})

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            session['username'] = user.name  # Store username in session
            return jsonify({"success": True, "message": "Login successful!", "redirect": url_for('dashboard')})
        else:
            return jsonify({"success": False, "message": "Invalid email or password."})

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
