import json
import subprocess
import sys

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from Backend.FaceRecognition.FaceMain import run_face_attendance
import os
app = Flask(__name__)
CORS(app)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

@app.route('/student')
def student():
    return render_template('student.html')

# API endpoints - placeholders for future implementation
@app.route('/submit', methods=['POST'])
def submit_form():
    # Form data lelo
    data = {
        "name": request.form.get("name"),
        "rollno": request.form.get("rollno"),
        "dob": request.form.get("dob"),
        "class": request.form.get("class"),
        "gender": request.form.get("gender"),
        "phone": request.form.get("phone")
    }

    # Data ko JSON me convert karke dusri python file ko bhejna
    subprocess.run(["python", "Backend/Database/FetchDetailofForm.py", json.dumps(data)])

    return redirect(url_for('newUser'))
@app.route("/newUser")
def newUser():
    return render_template("newUser.html")

@app.route('/attendance-mark', methods=['GET', 'POST'])
def mark_attendance_api():
    student = run_face_attendance()
    if student:
        return jsonify({
            'status': 'success',
            'message': f"Attendance marked for {student['name']}",
            'student': student
        })
    else:
        return jsonify({
            'status': 'fail',
            'message': "No student recognized"
        }), 404

@app.route('/api/reports/generate', methods=['GET'])
def generate_reports():
    return jsonify({'status': 'success', 'message': 'Generate reports endpoint - Flask integration pending'})

@app.route('/api/students/list', methods=['GET'])
def list_students():
    return jsonify({'status': 'success', 'message': 'List students endpoint - Flask integration pending'})

@app.route('/api/sync/cloud', methods=['POST'])
def sync_data():
    return jsonify({'status': 'success', 'message': 'Sync data endpoint - Flask integration pending'})

if __name__ == '__main__':
    import os
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Smart Attendance System Starting...")
    print("📘 Teacher Portal: http://localhost:5000/teacher")
    print("🎓 Student Portal: http://localhost:5000/student")
    
    app.run(debug=True, host='0.0.0.0', port=5000)