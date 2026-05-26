from flask import Flask, render_template, request, redirect, url_for
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
    conn = sqlite3.connect('club_tracker.db')
    c = conn.cursor()
    c.execute("SELECT id, first_name, last_name, created_at FROM members ORDER BY last_name, first_name")
    rows = c.fetchall()
    conn.close()
    user = "Club Leader"
    club_name = "Ashford School Hack Club"
    return render_template("members.html", user=user, club_name=club_name, members=rows)

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

@app.route('/dashboard/members/<int:id>/edit', methods=['POST'])
def edit_member(id):
    first = request.form['first_name']
    last = request.form['last_name']
    conn = sqlite3.connect('club_tracker.db'); c = conn.cursor()
    c.execute("UPDATE members SET first_name=?, last_name=? WHERE id=?", (first,last,id))
    conn.commit(); conn.close()
    return redirect(url_for('member_detail', id=id))

@app.route('/dashboard/members/<int:id>')
def member_detail(id):
    conn = sqlite3.connect('club_tracker.db')
    c = conn.cursor()
    c.execute("SELECT first_name,last_name,year,created_at FROM members WHERE id=?", (id,))
    member = c.fetchone()
    c.execute("""SELECT ad.day_date, coalesce(ar.present,0) as present
                 FROM attendance_days ad
                 LEFT JOIN attendance_records ar ON ad.id=ar.day_id AND ar.member_id=?
                 ORDER BY ad.day_date DESC LIMIT 10""", (id,))
    attendance = c.fetchall()
    c.execute("""SELECT p.* FROM projects p JOIN project_members pm ON p.id=pm.project_id WHERE pm.member_id=?""", (id,))
    projects = c.fetchall()
    c.execute("SELECT id,allergy_text,severity FROM allergies WHERE member_id=?", (id,))
    allergies = c.fetchall()
    conn.close()
    return render_template('member_detail.html', member=member, attendance=attendance, projects=projects, allergies=allergies)

@app.route('/dashboard/members')
def members():
    conn = sqlite3.connect('club_tracker.db'); c = conn.cursor()
    c.execute("SELECT id, first_name, last_name, created_at FROM members ORDER BY last_name, first_name")
    rows = c.fetchall(); conn.close()
    return render_template('members.html', members=rows)

@app.route('/dashboard/members/<int:id>')
def member_detail(id):
    c = sqlite3.connect('club_tracker.db').cursor()
    c.execute("SELECT first_name,last_name,year,created_at FROM members WHERE id=?", (id,))
    member = c.fetchone()
    # fetch attendance, projects, allergies similarly...
    return render_template('member_detail.html', member=member, attendance=..., projects=..., allergies=...)

@app.route('/dashboard/members/<int:id>/edit', methods=['POST'])
def edit_member(id):
    first = request.form['first_name']; last = request.form['last_name']
    c = sqlite3.connect('club_tracker.db').cursor(); c.execute("UPDATE members SET first_name=?, last_name=? WHERE id=?", (first,last,id))
    sqlite3.connect('club_tracker.db').commit(); return redirect(url_for('member_detail', id=id))
# run the app :D

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0",port=4500, debug=True)