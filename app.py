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
                 first_name TEXT,
                 last_name TEXT,
                 year INTEGER,
                 created_at TEXT DEFAULT CURRENT_TIMESTAMP
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS allergies (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 member_id INTEGER NOT NULL,
                 allergy_text TEXT NOT NULL,
                 severity TEXT,
                 created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY(member_id) REFERENCES members(id) ON DELETE CASCADE
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS projects (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 title TEXT,
                 github_repo TEXT,
                 demo_link TEXT,
                 shipped_to TEXT,
                 payout_received TEXT,
                 payout_amount REAL,
                 created_at TEXT DEFAULT CURRENT_TIMESTAMP
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS project_members (
                 project_id INTEGER NOT NULL,
                 member_id INTEGER NOT NULL,
                 PRIMARY KEY (project_id, member_id),
                 FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                 FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance_days (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 day_date TEXT UNIQUE NOT NULL,
                 created_at TEXT DEFAULT CURRENT_TIMESTAMP
                 )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance_records (
                 day_id INTEGER NOT NULL,
                 member_id INTEGER NOT NULL,
                 present INTEGER NOT NULL DEFAULT 1,
                 notes TEXT,
                 PRIMARY KEY (day_id, member_id),
                 FOREIGN KEY (day_id) REFERENCES attendance_days(id) ON DELETE CASCADE,
                 FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
                 )''')

    conn.commit()
    conn.close()

# define routes

@app.route('/')
def home():
    user = "Club Leader"
    return render_template("signin.html", user=user)

@app.route('/dashboard')
def dashboard():
    user = "Club Leader"
    club_name = "Ashford School Hack Club"
    return render_template("dashboard.html", user=user, club_name=club_name)

@app.route('/dashboard/members')
def members():
    user = "Club Leader"
    club_name = "Ashford School Hack Club"
    return render_template("members.html", user=user, club_name=club_name)

@app.route('/dashboard/allergies')
def allergies():
    user = "Club Leader"
    club_name = "Ashford School Hack Club"
    return render_template("allergies.html", user=user, club_name=club_name)

@app.route('/dashboard/projects')
def projects():
    user = "Club Leader"
    club_name = "Ashford School Hack Club"
    return render_template("projects.html", user=user, club_name=club_name)

@app.route('/dashboard/attendance')
def attendance():
    user = "Club Leader"
    club_name = "Ashford School Hack Club"
    return render_template("attendance.html", user=user, club_name=club_name)

# run the app :D

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0",port=4500, debug=True)