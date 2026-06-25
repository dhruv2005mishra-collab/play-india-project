from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_playindia_key' # Required for login sessions

def get_db_connection():
    conn = sqlite3.connect('playindia.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Added password, latitude (lat), and longitude (lng)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            lat REAL,
            lng REAL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sport TEXT NOT NULL,
            location TEXT NOT NULL,
            players_needed INTEGER NOT NULL,
            creator_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    activities = conn.execute('SELECT * FROM activities').fetchall()
    conn.close()
    return render_template('index.html', activities=activities)

@app.route('/signup', methods=('GET', 'POST'))
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password']) # Encrypt password!
        lat = request.form['lat']
        lng = request.form['lng']
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (name, email, password, lat, lng) VALUES (?, ?, ?, ?, ?)', 
                         (name, email, password, lat, lng))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Email already exists!"
        finally:
            conn.close()
        
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            return redirect(url_for('index'))
        else:
            return "Invalid email or password"
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/add_activity', methods=('GET', 'POST'))
def add_activity():
    if 'user_id' not in session:
        return redirect(url_for('login')) # Force login to post

    if request.method == 'POST':
        sport = request.form['sport']
        location = request.form['location']
        players = request.form['players_needed']
        creator_id = session['user_id']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO activities (sport, location, players_needed, creator_id) VALUES (?, ?, ?, ?)', 
                     (sport, location, players, creator_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
        
    return render_template('add_activity.html')

if __name__ == '__main__':
    app.run(debug=True)
