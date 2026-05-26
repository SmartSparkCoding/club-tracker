from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('club_tracker.db')
    c = conn.cursor()
    c.execute('PRAGMA foreign_keys = ON')
    c.execute('''CREATE TABLE IF NOT EXISTS members (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 email TEXT UNIQUE NOT NULL,
                 display_name TEXT,
                 created_at TEXT DEFAULT CURRENT_TIMESTAMP
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS allergies (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT UNIQUE NOT NULL,
                 description TEXT
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS member_allergies (
                 member_id INTEGER NOT NULL,
                 allergy_id INTEGER NOT NULL,
                 severity TEXT,
                 notes TEXT,
                 PRIMARY KEY (member_id, allergy_id),
                 FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
                 FOREIGN KEY (allergy_id) REFERENCES allergies(id) ON DELETE CASCADE
                 )''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    user = "Jacob Navaratne"
    return render_template("signin.html", user=user)

@app.route('/dashboard')
def dashboard():
    user = "Jacob Navaratne"
    return render_template("dashboard.html", user=user)

@app.route('/dashboard/members')
def members():
    user = "Jacob Navaratne"
    return render_template("members.html", user=user)


if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0",port=4500, debug=True)

