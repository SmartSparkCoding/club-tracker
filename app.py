from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(Path(__file__).parent / '.env')

app = Flask(__name__)
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k, v)

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
    # ensure `email` column exists (safe ALTER without UNIQUE)
    cols = [r[1] for r in c.execute("PRAGMA table_info(members)").fetchall()]
    if 'email' not in cols:
        c.execute("ALTER TABLE members ADD COLUMN email TEXT")

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
    club_name = fetch_club_name_from_api()
    hcb = getHCBData()
    return render_template("dashboard.html", user=user, club_name=club_name, hcb=hcb)

@app.route('/dashboard/members')
def members():
    conn = sqlite3.connect('club_tracker.db')
    c = conn.cursor()
    c.execute("SELECT id, first_name, last_name, created_at FROM members ORDER BY last_name, first_name")
    rows = c.fetchall()
    conn.close()
    user = "Club Leader"
    club_name = fetch_club_name_from_api()
    return render_template("members.html", user=user, club_name=club_name, members=rows)

@app.route('/dashboard/allergies')
def allergies():
    conn = sqlite3.connect('club_tracker.db'); c = conn.cursor()
    c.execute("""SELECT a.id, m.first_name, m.last_name, a.allergy_text, a.severity
                 FROM allergies a JOIN members m ON a.member_id=m.id
                 ORDER BY CASE a.severity WHEN 'Severe' THEN 1 WHEN 'Moderate' THEN 2 ELSE 3 END, m.last_name""")
    rows = c.fetchall(); conn.close()
    user = "Club Leader"
    club_name = fetch_club_name_from_api()
    return render_template('allergies.html', user=user, club_name=club_name, allergies=rows)

@app.route('/dashboard/projects')
def projects():
    user = "Club Leader"
    club_name = fetch_club_name_from_api()
    return render_template("projects.html", user=user, club_name=club_name)

@app.route('/dashboard/attendance')
def attendance():
    user = "Club Leader"
    club_name = fetch_club_name_from_api()
    return render_template("attendance.html", user=user, club_name=club_name)

@app.route('/dashboard/members/<int:id>/edit', methods=['POST'])
def edit_member(id):
    # accept optional fields (email, first_name, last_name)
    club_name = fetch_club_name_from_api()
    first = request.form.get('first_name')
    last = request.form.get('last_name')
    email = request.form.get('email')
    conn = sqlite3.connect('club_tracker.db'); c = conn.cursor()
    updates = []
    params = []
    if first is not None:
        updates.append('first_name = ?'); params.append(first)
    if last is not None:
        updates.append('last_name = ?'); params.append(last)
    if email is not None:
        updates.append('email = ?'); params.append(email)
    if updates:
        sql = 'UPDATE members SET ' + ', '.join(updates) + ' WHERE id = ?'
        params.append(id)
        c.execute(sql, params)
        conn.commit()
    conn.close()
    return redirect(url_for('member_detail', id=id))

@app.route('/dashboard/members/<int:id>')
def member_detail(id):
    conn = sqlite3.connect('club_tracker.db')
    club_name = fetch_club_name_from_api()
    c = conn.cursor()
    c.execute("SELECT first_name,last_name,year,created_at,email FROM members WHERE id=?", (id,))
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

@app.route('/dashboard/allergies/<int:id>/delete', methods=['POST'])
def delete_allergy(id):
    conn = sqlite3.connect('club_tracker.db'); c = conn.cursor()
    c.execute("DELETE FROM allergies WHERE id=?", (id,))
    conn.commit(); conn.close()
    return redirect(url_for('allergies'))

@app.route('/dashboard/members/<int:id>/allergies/add', methods=['POST'])
def add_allergy(id):
    allergy_text = request.form.get('allergy_text')
    club_name = fetch_club_name_from_api()
    severity = request.form.get('severity')
    conn = sqlite3.connect('club_tracker.db'); c = conn.cursor()
    c.execute("INSERT INTO allergies(member_id, allergy_text, severity) VALUES (?,?,?)", (id, allergy_text, severity))
    conn.commit(); conn.close()
    return redirect(url_for('member_detail', id=id))


@app.route('/dashboard/projects/<int:project_id>/add_member', methods=['POST'])
def add_project_member(project_id):
    club_name = fetch_club_name_from_api()
    member_id = int(request.form['member_id'])
    conn = sqlite3.connect('club_tracker.db'); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO project_members(project_id, member_id) VALUES (?,?)", (project_id, member_id))
    conn.commit(); conn.close()
    return redirect(url_for('member_detail', id=member_id))


@app.route('/dashboard/attendance/record', methods=['POST'])
def record_attendance():
    day = request.form['day_date']  # YYYY-MM-DD
    member_id = int(request.form['member_id'])
    club_name = fetch_club_name_from_api()
    conn = sqlite3.connect('club_tracker.db'); c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO attendance_days(day_date) VALUES (?)", (day,))
    c.execute("SELECT id FROM attendance_days WHERE day_date=?", (day,))
    day_id = c.fetchone()[0]
    c.execute("INSERT OR REPLACE INTO attendance_records(day_id, member_id, present) VALUES (?,?,1)", (day_id, member_id))
    conn.commit(); conn.close()
    return redirect(url_for('member_detail', id=member_id))

@app.route('/dashboard/members/new')
def add_member_form():
    user = "Club Leader"
    club_name = fetch_club_name_from_api()
    return render_template("member_new.html", user=user, club_name=club_name)

@app.route('/dashboard/members/new', methods=['POST'])
def add_member():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    year = request.form['year']
    email = request.form.get('email')

    conn = sqlite3.connect('club_tracker.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO members (first_name, last_name, year, email) VALUES (?, ?, ?, ?)",
        (first_name, last_name, year, email)
    )
    member_id = c.lastrowid
    conn.commit()
    conn.close()

    club_name = fetch_club_name_from_api()

    return redirect(url_for('member_detail', id=member_id))

@app.route('/dashboard/allergies/new', methods=['POST'])
def add_allergy_global():
    member_id = int(request.form['member_id']); text = request.form['allergy_text']; severity = request.form['severity']
    conn = sqlite3.connect('club_tracker.db'); c = conn.cursor()
    c.execute("INSERT INTO allergies(member_id, allergy_text, severity) VALUES (?,?,?)", (member_id, text, severity))
    conn.commit(); conn.close()
    return redirect(url_for('allergies'))

@app.route('/dashboard/allergies/new')
def allergy_new_form():
    conn=sqlite3.connect('club_tracker.db'); c=conn.cursor()
    c.execute("SELECT id,first_name,last_name FROM members ORDER BY last_name, first_name")
    members=c.fetchall(); conn.close()
    return render_template('allergy_new.html', members=members, club_name=os.getenv('CLUB_NAME'))

# club api from HC - below is used to pull name (from env)

def fetch_club_name_from_api():
    fallback_name = "Error Loading Club Name"

    club_name = os.getenv("CLUB_NAME", fallback_name)
    token = os.getenv("CLUBAPI_TOKEN", "").strip()

    query = urlencode({"name": club_name})
    # correct public endpoint for the Club API
    url = f"https://clubapi.hackclub.com/club?{query}"

    headers = {"Accept": "application/json"}
    if token: 
        headers["Authorization"] = token

    req = Request(url, headers=headers, method="GET")

    try:
        with urlopen(req, timeout=6) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)
            api_name = data.get("club_name") or data.get("fields", {}).get("club_name")
            return api_name or club_name
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        return club_name



def getHCBData():
    slug = os.getenv("HCB_ORG_SLUG", "ashford-school-hack-club")
    url = f"https://hcb.hackclub.com/api/v3/organizations/{slug}"

    fallback = {
        "ok": False,
        "org_name": "HCB",
        "org_slug": slug,
        "manager_name": "Unknown",
        "balance_cents": 0,
        "balance_display": "$0.00",
        "fee_balance_cents": 0,
        "incoming_balance_cents": 0,
        "total_raised_cents": 0,
        "total_raised_display": "$0.00",
        "website": "",
        "hcb_url": f"https://hcb.hackclub.com/{slug}",
        "logo": "",
        "error": None, 
    }

    def cents_to_display(cents):
        return f"${(cents or 0)/100:.2f}"
    
    try:
        req = Request(url, headers={"Accept": "application/json"}, method="GET")
        with urlopen(req, timeout=10) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw)

        balances = data.get("balances") or {}
        users = data.get("users") or []

        manager_name = "Unknown"
        for u in users:
            if isinstance(u, dict) and (u.get("full_name") or u.get("name")):
                manager_name = u.get("full_name") or u.get("name")
                break
        if manager_name == "Unknown" and users:
            u0 = users[0]
            if isinstance(u0, dict):
                manager_name = u0.get("name") or u0.get("id") or "Unknown"

        # balances keys may be named slightly differently; prefer *_cents keys
        def safe_int(d, *keys):
            for k in keys:
                v = d.get(k)
                if v is None:
                    continue
                try:
                    return int(v)
                except Exception:
                    try:
                        return int(float(v))
                    except Exception:
                        continue
            return 0

        balance_cents = safe_int(balances, "balance_cents", "balance")
        fee_balance_cents = safe_int(balances, "fee_balance_cents")
        incoming_balance_cents = safe_int(balances, "incoming_balance_cents")
        total_raised_cents = safe_int(balances, "total_raised", "total_raised_cents")

        return {
            "ok": True,
            "org_name": data.get("name") or "HCB",
            "org_slug": data.get("slug") or slug,
            "manager_name": manager_name,
            "balance_cents": balance_cents,
            "balance_display": cents_to_display(balance_cents),
            "fee_balance_cents": fee_balance_cents,
            "incoming_balance_cents": incoming_balance_cents,
            "total_raised_cents": total_raised_cents,
            "total_raised_display": cents_to_display(total_raised_cents),
            "website": data.get("website") or "",
            "hcb_url": f"https://hcb.hackclub.com/{data.get('slug') or slug}",
            "logo": data.get("logo") or "",
            "error": None,
        }

    except Exception as e:
        out = fallback.copy()
        out["error"] = str(e)
        return out

# run the app :D

if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0",port=4500, debug=True)