from flask import Flask, request, session, redirect, url_for, render_template_string, jsonify, flash, send_file
import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import qrcode
import io

app = Flask(__name__)
app.secret_key = "super-secret-change-me"
DB = "attendance2.db"

# ---------- DB setup ----------
def init_db():
    if not os.path.exists(DB):
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("""CREATE TABLE students (
                        enrollment TEXT PRIMARY KEY,
                        name TEXT,
                        password_hash TEXT
                    )""")
        c.execute("""CREATE TABLE attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        enrollment TEXT,
                        class_code TEXT,
                        date TEXT,
                        time TEXT,
                        UNIQUE(enrollment,date,class_code)
                    )""")
        conn.commit()
        conn.close()
        seed_students()

def db_execute(query, params=(), fetch=False):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(query, params)
    rows = c.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return rows

def seed_students():
    students = [("ENR2025001", "Alice"), ("ENR2025002", "Bob"), ("ENR2025003", "Charlie")]
    for enr, name in students:
        pw_hash = generate_password_hash(enr)  # password = enrollment
        db_execute("INSERT INTO students (enrollment,name,password_hash) VALUES (?,?,?)",
                   (enr, name, pw_hash))

init_db()
CLASS_CODE = "CLASSROOM-101"
QR_FILE = "classroom101.png"

def generate_qr():
    if not os.path.exists(QR_FILE):
        img = qrcode.make(CLASS_CODE)
        img.save(QR_FILE)   # <-- Save file permanently
        print(f"✅ QR code saved as {QR_FILE}")
    # Return a BytesIO buffer so we can still serve it at /qr.png
    img = qrcode.make(CLASS_CODE)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# ---------- Templates ----------
INDEX_HTML = """
<h2>College Attendance System</h2>
{% if 'enrollment' in session %}
<p>Welcome {{ session['name'] }} ({{ session['enrollment'] }})</p>
<a href="{{ url_for('scanner') }}">📷 Open QR Scanner</a> | 
<a href="{{ url_for('logout') }}">Logout</a>
{% else %}
<a href="{{ url_for('login') }}">Login</a>
{% endif %}
<p><a href="{{ url_for('view_attendance') }}">View Attendance</a></p>
<p><a href="{{ url_for('qr_code') }}">Download Classroom QR</a></p>
"""

LOGIN_HTML = """
<h2>Login</h2>
{% with messages = get_flashed_messages() %}
  {% if messages %}
    <ul>{% for m in messages %}<li>{{ m }}</li>{% endfor %}</ul>
  {% endif %}
{% endwith %}
<form method="post">
  Enrollment: <input name="enrollment"><br>
  Password: <input name="password" type="password"><br>
  <button type="submit">Login</button>
</form>
"""

SCANNER_HTML = """
<h2>QR Scanner</h2>
<p>Point your camera at the classroom QR code</p>
<div id="reader" style="width:300px"></div>
<div id="result"></div>
<a href="{{ url_for('index') }}">Home</a>

<script src="https://unpkg.com/html5-qrcode"></script>
<script>
function onScanSuccess(decodedText, decodedResult) {
    fetch("/mark", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ code: decodedText })
    }).then(res => res.json()).then(data => {
        document.getElementById("result").innerHTML = data.message;
    });
    html5QrcodeScanner.clear();
}
var html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 });
html5QrcodeScanner.render(onScanSuccess);
</script>
"""

VIEW_HTML = """
<h2>All Attendance</h2>
<table border=1 cellpadding=4>
<tr><th>Enrollment</th><th>Class Code</th><th>Date</th><th>Time</th></tr>
{% for r in rows %}
<tr><td>{{ r[0] }}</td><td>{{ r[1] }}</td><td>{{ r[2] }}</td><td>{{ r[3] }}</td></tr>
{% endfor %}
</table>
<a href="{{ url_for('index') }}">Home</a>
"""

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        enr = request.form.get("enrollment")
        pw = request.form.get("password")
        rows = db_execute("SELECT password_hash,name FROM students WHERE enrollment=?", (enr,), fetch=True)
        if rows and check_password_hash(rows[0][0], pw):
            session["enrollment"] = enr
            session["name"] = rows[0][1]
            flash("Login successful.")
            return redirect(url_for("scanner"))
        flash("Invalid credentials.")
    return render_template_string(LOGIN_HTML)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/scanner")
def scanner():
    if "enrollment" not in session:
        return redirect(url_for("login"))
    return render_template_string(SCANNER_HTML)

@app.route("/mark", methods=["POST"])
def mark():
    if "enrollment" not in session:
        return jsonify({"message": "❌ You must log in first."}), 403

    data = request.get_json()
    code = data.get("code")
    today = datetime.today().strftime("%Y-%m-%d")
    now_time = datetime.now().strftime("%H:%M:%S")

    rows = db_execute("SELECT time FROM attendance WHERE enrollment=? AND date=? AND class_code=?",
                      (session["enrollment"], today, code), fetch=True)
    if rows:
        return jsonify({"message": f"✅ Already marked for {today} at {rows[0][0]} (Class {code})"})

    db_execute("INSERT INTO attendance (enrollment,class_code,date,time) VALUES (?,?,?,?)",
               (session["enrollment"], code, today, now_time))
    return jsonify({"message": f"✅ Attendance marked at {now_time} (Class {code})"})

@app.route("/view")
def view_attendance():
    rows = db_execute("SELECT enrollment,class_code,date,time FROM attendance ORDER BY date DESC,time DESC", fetch=True)
    return render_template_string(VIEW_HTML, rows=rows)

@app.route("/qr.png")
def qr_code():
    buf = generate_qr()
    return send_file(buf, mimetype="image/png")

# ---------- Run ----------
if __name__ == "__main__":
    print("Server running on http://127.0.0.1:5000")
    print("Test logins: ENR2025001 / ENR2025001 (same for 2,3)")
    app.run(debug=True)