from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pyodbc
import pandas as pd
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

conn = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=HP\\SQLEXPRESS02;"
    "Database=TYIT_Project_Selector;"
    "Trusted_Connection=yes;"
)

cursor = conn.cursor()

sessions = {}

# ================= REGISTER =================
@app.route("/register", methods=["POST"])
def register():

    data = request.json
    rollno = data["rollno"]
    username = data["username"]
    password = data["password"]

    cursor.execute("SELECT * FROM Users WHERE rollno=?", (rollno,))
    if cursor.fetchone():
        return jsonify({"error": "User already registered"}), 400

    cursor.execute("""
        INSERT INTO Users (rollno,username,password,role,attempt_count,is_locked)
        VALUES (?,?,?,'student',0,0)
    """,(rollno,username,password))

    conn.commit()

    return jsonify({"message":"Registered"})


# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():

    data=request.json

    cursor.execute("""
        SELECT user_id,role,rollno
        FROM Users
        WHERE username=? AND password=? AND role=?
    """,(data["username"],data["password"],data["role"]))

    user=cursor.fetchone()

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
        "role":user[1],
        "rollno":user[2]
    })


# ================= SUBMIT PROJECT =================
@app.route("/projects", methods=["POST"])
def submit_projects():

    token=request.headers.get("Authorization")
    session=sessions.get(token)

    if not session or session["role"]!="student":
        return jsonify({"error":"Unauthorized"}),401

    rollno=session["rollno"]

    cursor.execute("SELECT attempt_count,is_locked FROM Users WHERE rollno=?",(rollno,))
    user=cursor.fetchone()

    if user[1]:
        return jsonify({"error":"Project already finalized"}),400

    if user[0]>=5:
        return jsonify({"error":"Maximum attempts reached"}),400

    projects=request.json["projects"]

    new_attempt=user[0]+1

    for p in projects:

        cursor.execute("""
            INSERT INTO Projects
            (rollno,title,description,status,is_ai_generated,submission_no,created_at)
            VALUES (?,?,?,?,?,?,?)
        """,(rollno,p["title"],p["description"],"Under Review",0,new_attempt,datetime.now()))

    cursor.execute("UPDATE Users SET attempt_count=? WHERE rollno=?",(new_attempt,rollno))

    conn.commit()

    return jsonify({"message":"Submitted"})


# ================= STUDENT VIEW =================
@app.route("/student/projects", methods=["GET"])
def student_projects():

    token=request.headers.get("Authorization")
    session=sessions.get(token)

    if not session or session["role"]!="student":
        return jsonify({"error":"Unauthorized"}),401

    rollno=session["rollno"]

    cursor.execute("SELECT attempt_count,is_locked FROM Users WHERE rollno=?",(rollno,))
    user=cursor.fetchone()

    cursor.execute("""
        SELECT project_id,title,description,status,is_ai_generated,created_at
        FROM Projects
        WHERE rollno=?
        ORDER BY created_at
    """,(rollno,))

    rows=cursor.fetchall()

    projects=[]

    for r in rows:
        projects.append({
            "project_id":r[0],
            "title":r[1],
            "description":r[2],
            "status":r[3],
            "is_ai_generated":r[4],
            "created_at":str(r[5])
        })

    return jsonify({
        "attempt_count":user[0],
        "is_locked":user[1],
        "projects":projects
    })


# ================= AI RECOMMEND =================
@app.route("/ai/recommend", methods=["POST"])
def ai_recommend():

    token=request.headers.get("Authorization")
    session=sessions.get(token)

    if not session or session["role"]!="student":
        return jsonify({"error":"Unauthorized"}),401

    rollno=session["rollno"]

    cursor.execute("SELECT attempt_count,is_locked FROM Users WHERE rollno=?",(rollno,))
    user=cursor.fetchone()

    if user[0]<5:
        return jsonify({"error":"AI allowed only after 5 attempts"}),400

    cursor.execute("""
        SELECT TOP 1 title,description
        FROM AI_Projects
        ORDER BY NEWID()
    """)

    ai=cursor.fetchone()

    title=ai[0]
    description=ai[1]

    cursor.execute("""
        INSERT INTO Projects
        (rollno,title,description,status,is_ai_generated,submission_no,created_at)
        VALUES (?,?,?,?,?,?,?)
    """,(rollno,title,description,"AI Recommended",1,user[0]+1,datetime.now()))

    cursor.execute("""
        UPDATE Users
        SET is_locked=1, attempt_count=?
        WHERE rollno=?
    """,(user[0]+1,rollno))

    conn.commit()

    return jsonify({"message":"AI project assigned","title":title})


# ================= ADMIN VIEW =================
@app.route("/admin/projects", methods=["GET"])
def admin_projects():

    token=request.headers.get("Authorization")
    session=sessions.get(token)

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

    return jsonify(result)


# ================= APPROVE =================
@app.route("/admin/approve/<int:project_id>", methods=["POST"])
def approve(project_id):

    token=request.headers.get("Authorization")
    session=sessions.get(token)

    if not session or session["role"]!="admin":
        return jsonify({"error":"Unauthorized"}),401

    cursor.execute("SELECT rollno FROM Projects WHERE project_id=?",(project_id,))
    rollno=cursor.fetchone()[0]

    cursor.execute("UPDATE Projects SET status='Approved' WHERE project_id=?",(project_id,))

    cursor.execute("""
        UPDATE Projects
        SET status='Rejected'
        WHERE rollno=? AND project_id!=?
    """,(rollno,project_id))

    cursor.execute("UPDATE Users SET is_locked=1 WHERE rollno=?",(rollno,))

    conn.commit()

    return jsonify({"message":"Approved"})


# ================= REJECT =================
@app.route("/admin/reject/<int:project_id>", methods=["POST"])
def reject(project_id):

    token=request.headers.get("Authorization")
    session=sessions.get(token)

    if not session or session["role"]!="admin":
        return jsonify({"error":"Unauthorized"}),401

    cursor.execute("UPDATE Projects SET status='Rejected' WHERE project_id=?",(project_id,))
    conn.commit()

    return jsonify({"message":"Rejected"})


# ================= CSV DOWNLOAD =================
@app.route("/admin/download")
def download():

    df=pd.read_sql("SELECT * FROM Projects",conn)
    df.to_csv("projects.csv",index=False)

    return send_file("projects.csv",as_attachment=True)


# ================= RUN SERVER =================
if __name__=="__main__":
    app.run(debug=True)