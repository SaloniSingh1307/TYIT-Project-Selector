from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pyodbc
import pandas as pd
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

def get_connection():
    return pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=HP\\SQLEXPRESS02;"
        "Database=TYIT_Project_Selector;"
        "Trusted_Connection=yes;"
    )

sessions = {}

def get_token_session():
    auth = request.headers.get("Authorization")
    if not auth:
        return None
    token = auth.split(" ")[1] if " " in auth else auth
    return sessions.get(token)

# ================= REGISTER =================
@app.route("/register", methods=["POST"])
def register():
    conn = get_connection()
    cursor = conn.cursor()

    data = request.json
    rollno = data["rollno"]
    username = data["username"]
    password = data["password"]

    cursor.execute("SELECT * FROM Users WHERE rollno=?", (rollno,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "User already registered"}), 400

    cursor.execute("""
        INSERT INTO Users (rollno,username,password,role,attempt_count,is_locked)
        VALUES (?,?,?,'student',0,0)
    """,(rollno,username,password))

    conn.commit()
    conn.close()

    return jsonify({"message":"Registered"})


#Forgot Password
@app.route("/forgot-password", methods=["POST"])
def forgot_password():

    conn = get_connection()
    cursor = conn.cursor()

    data = request.json
    username = data["username"]
    password = data["password"]

    cursor.execute("SELECT * FROM Users WHERE username=?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({"error": "User not found"}), 404

    cursor.execute("UPDATE Users SET password=? WHERE username=?", (password, username))

    conn.commit()
    conn.close()

    return jsonify({"message": "Password updated"})

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    conn = get_connection()
    cursor = conn.cursor()

    data=request.json

    cursor.execute("""
        SELECT user_id,role,rollno
        FROM Users
        WHERE username=? AND password=? AND role=?
    """,(data["username"],data["password"],data["role"]))

    user=cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error":"Invalid credentials"}),401

    token=str(uuid.uuid4())

    sessions[token]={
        "user_id":user[0],
        "role":user[1],
        "rollno":user[2]
    }

    return jsonify({
        "token":token,
        "role":user[1]
    })

# ================= SUBMIT PROJECT =================
@app.route("/projects", methods=["POST"])
def submit_projects():
    conn = get_connection()
    cursor = conn.cursor()

    session=get_token_session()

    if not session or session["role"]!="student":
        return jsonify({"error":"Unauthorized"}),401

    rollno=session["rollno"]

    cursor.execute("SELECT is_locked FROM Users WHERE rollno=?", (rollno,))
    user=cursor.fetchone()

    if user[0]:
        return jsonify({"error":"Project already finalized"}),400

    projects=request.json["projects"]

    # ✅ Validation
    for p in projects:
        if len(p["title"].strip()) < 5 or len(p["description"].strip()) < 10:
            return jsonify({"error":"Invalid project data"}),400

    for p in projects:
        cursor.execute("""
            INSERT INTO Projects
            (rollno,title,description,status,is_ai_generated,submission_no,created_at)
            VALUES (?,?,?,?,?,?,?)
        """,(rollno,p["title"],p["description"],"Under Review",0,0,datetime.now()))

    conn.commit()
    conn.close()

    return jsonify({"message":"Submitted"})

# ================= STUDENT VIEW =================
@app.route("/student/projects", methods=["GET"])
def student_projects():
    conn = get_connection()
    cursor = conn.cursor()

    session=get_token_session()

    if not session or session["role"]!="student":
        return jsonify({"error":"Unauthorized"}),401

    rollno=session["rollno"]

    cursor.execute("""
        SELECT project_id,title,description,status,is_ai_generated,created_at
        FROM Projects
        WHERE rollno=?
        ORDER BY created_at
    """,(rollno,))

    rows=cursor.fetchall()

    projects=[]
    rejected_count = 0

    for r in rows:
        if r[3] == "Rejected":
            rejected_count += 1

        projects.append({
            "project_id":r[0],
            "title":r[1],
            "description":r[2],
            "status":r[3],
            "is_ai_generated":r[4],
            "created_at":str(r[5])
        })

    conn.close()

    return jsonify({
        "projects":projects,
        "all_rejected": len(projects) > 0 and rejected_count == len(projects)
    })

# ================= AI =================
@app.route("/ai/recommend", methods=["POST"])
def ai_recommend():
    conn = get_connection()
    cursor = conn.cursor()

    session=get_token_session()

    if not session or session["role"]!="student":
        return jsonify({"error":"Unauthorized"}),401

    rollno=session["rollno"]

    # ✅ Check all rejected
    cursor.execute("SELECT status FROM Projects WHERE rollno=?", (rollno,))
    rows = cursor.fetchall()

    if not rows:
        return jsonify({"error":"No projects submitted"}),400

    for r in rows:
        if r[0] != "Rejected":
            return jsonify({"error":"AI allowed only after all rejected"}),400

    cursor.execute("SELECT TOP 1 title,description FROM AI_Projects ORDER BY NEWID()")
    ai = cursor.fetchone()

    if not ai:
        return jsonify({"error":"No AI projects available"}),500

    cursor.execute("""
        INSERT INTO Projects
        (rollno,title,description,status,is_ai_generated,submission_no,created_at)
        VALUES (?,?,?,?,?,?,?)
    """,(rollno,ai[0],ai[1],"AI Recommended",1,0,datetime.now()))

    cursor.execute("UPDATE Users SET is_locked=1 WHERE rollno=?", (rollno,))

    conn.commit()
    conn.close()

    return jsonify({"message":"AI assigned"})

# ================= ADMIN =================
@app.route("/admin/projects", methods=["GET"])
def admin_projects():
    conn = get_connection()
    cursor = conn.cursor()

    session=get_token_session()

    if not session or session["role"]!="admin":
        return jsonify({"error":"Unauthorized"}),401

    cursor.execute("""
        SELECT project_id,rollno,title,description,status,created_at,is_ai_generated
        FROM Projects
        ORDER BY created_at DESC
    """)

    rows=cursor.fetchall()

    result=[]

    for r in rows:
        result.append({
            "project_id":r[0],
            "rollno":r[1],
            "title":r[2],
            "description":r[3],
            "status":r[4],
            "created_at":str(r[5]),
            "is_ai_generated":r[6]
        })

    conn.close()

    return jsonify(result)

# ================= APPROVE =================
@app.route("/admin/approve/<int:project_id>", methods=["POST"])
def approve(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    session=get_token_session()

    if not session or session["role"]!="admin":
        return jsonify({"error":"Unauthorized"}),401

    cursor.execute("SELECT rollno FROM Projects WHERE project_id=?", (project_id,))
    row = cursor.fetchone()

    if not row:
        return jsonify({"error":"Project not found"}),404

    rollno = row[0]

    cursor.execute("UPDATE Projects SET status='Approved' WHERE project_id=?", (project_id,))
    cursor.execute("UPDATE Projects SET status='Rejected' WHERE rollno=? AND project_id!=?", (rollno,project_id))
    cursor.execute("UPDATE Users SET is_locked=1 WHERE rollno=?", (rollno,))

    conn.commit()
    conn.close()

    return jsonify({"message":"Approved"})

# ================= REJECT =================
@app.route("/admin/reject/<int:project_id>", methods=["POST"])
def reject(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    session=get_token_session()

    if not session or session["role"]!="admin":
        return jsonify({"error":"Unauthorized"}),401

    cursor.execute("UPDATE Projects SET status='Rejected' WHERE project_id=?", (project_id,))

    conn.commit()
    conn.close()

    return jsonify({"message":"Rejected"})

# ================= CSV =================
@app.route("/admin/download")
def download():
    conn = get_connection()

    df=pd.read_sql("SELECT * FROM Projects",conn)
    df.to_csv("projects.csv",index=False)

    conn.close()

    return send_file("projects.csv",as_attachment=True)

if __name__=="__main__":
    app.run(debug=True)