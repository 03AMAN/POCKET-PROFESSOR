from flask import Flask, render_template, request, redirect, url_for, flash, session
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Securely generates a random secret key

# Dummy user data for demonstration purposes
users = {
    "test@example.com": {
        "password": "password123",
        "name": "Test User"
    }
}

# Intro page route
@app.route('/')
def intro():
    return render_template('intro.html')

# Signup page route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']

        if email in users:
            flash('Email already registered. Please log in.', 'warning')
            return redirect(url_for('login'))  # ✅ Corrected from 'index' to 'login'

        users[email] = {"password": password, "name": name}
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))  # ✅ Corrected from 'index' to 'login'

    return render_template('Signup.html')

# Login page route
@app.route('/index', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users.get(email)
        if user and user['password'] == password:
            session['user'] = user['name']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('index.html')

# Dashboard page route
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash('Please log in to access the dashboard.', 'warning')
        return redirect(url_for('login'))

    return render_template('dashboard.html', user=session['user'])

# Logout route
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)