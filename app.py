import json
import sqlite3
import subprocess
import sys
import os
import time

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_file
from flask_cors import CORS
from Backend.FaceRecognition.FaceMain import run_face_attendance
from Backend.Database.NewDataFile import check_database_status
from translations import translations

app = Flask(__name__)
CORS(app)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 🔑 Required for session
app.secret_key = "supersecretkey123"

db_path = "Backend/Database/school_portal.db"

def get_text(key, lang='en'):
    return translations.get(lang, {}).get(key, translations['en'].get(key, key))

@app.context_processor
def inject_language():
    lang = session.get('language', 'en')
    return dict(get_text=lambda key: get_text(key, lang), current_lang=lang)

@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in ['en', 'hi', 'gu']:
        session['language'] = lang
    return redirect(request.referrer or url_for('first'))


def verify_user(table, user_id, password, role):
    try:
        if role == "student":
            id = "StudentID"
        elif role == "teacher":
            id = "TeacherID"
        else:
            id = "AdminID"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(f"SELECT Password FROM {table} WHERE {id} = ?", (user_id,))
        row = cursor.fetchone()

        if row:
            stored_password = row[0]
            # ⚠️ In production, store hashed passwords and use check_password_hash
            if stored_password == password:
                return True
        return False
    finally:
        conn.close()


@app.route("/")
def first():
    # If already logged in → redirect to their dashboard
    if session.get("logged_in"):
        if session["role"] == "student":
            return redirect(url_for("student"))
        elif session["role"] == "teacher":
            return redirect(url_for("teacher"))
        elif session["role"] == "admin":
            return redirect(url_for("admin"))
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    user_id = request.form.get("userId")
    password = request.form.get("password")
    role = request.form.get("role")  # student / teacher / admin

    table_map = {
        "student": "Students",
        "teacher": "ClassTeachers",
        "admin": "Admin"
    }

    table = table_map[role]

    if verify_user(table, user_id, password, role):
        # ✅ Store session data
        session["logged_in"] = True
        session["user_id"] = user_id
        session["role"] = role

        if role == "student":
            return redirect(url_for("student"))
        elif role == "teacher":
            return redirect(url_for("teacher"))
        elif role == "admin":
            return redirect(url_for("admin"))
    else:
        return render_template("login.html", error=True)


@app.route("/logout")
def logout():
    session.clear()  # ❌ clear session on logout
    return redirect(url_for("first"))


@app.route('/teacher')
def teacher():
    if not session.get("logged_in") or session.get("role") != "teacher":
        return redirect(url_for("first"))

    user_id = session.get("user_id")

    # Initialize teacher_data to avoid UnboundLocalError
    teacher_data = None

    # Fetch teacher details from DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT Name, TeacherID, Class FROM ClassTeachers WHERE TeacherID = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        teacher_data = {
            "name": row[0],
            "id": row[1],
            "class": row[2]
        }

    return render_template("teacher.html", teacher=teacher_data)

@app.route('/admin')
def admin():
    if not session.get("logged_in") or session.get("role") != "admin":
        return redirect(url_for("first"))
    user_id = session.get("user_id")

    # Fetch admin details including school
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT Name, School FROM Admin WHERE AdminID = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        admin_data = {
            "name": row[0],
            "school": row[1]
        }
        # Store school in session for filtering
        session["admin_school"] = row[1]
    return render_template("admin.html", admin=admin_data)


@app.route("/add-teacher", methods=["POST"])
def add_teacher():
    if not session.get("logged_in") or session.get("role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    try:
        data = request.get_json()  # if JSON from front-end
        result = subprocess.run(["python", "Backend/Database/FetchDetailofForm.py", json.dumps(data)], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({"status": "success", "message": "Teacher added successfully!"})
        else:
            return jsonify({"status": "error", "message": "Failed to add teacher"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error: {str(e)}"}), 500


@app.route('/student')
def student():
    if not session.get("logged_in") or session.get("role") != "student":
        return redirect(url_for("first"))

    user_id = session.get("user_id")

    # Fetch student details from DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT Name, StudentID, Class, RollNumber FROM Students WHERE StudentID = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        student_data = {
            "name": row[0],
            "id": row[1],
            "class": row[2],
            "roll": row[3]
        }
    return render_template("student.html", student=student_data)


# --------------------- API endpoints -----------------------

@app.route('/submit', methods=['POST'])
def submit_form():
    data = {
        "name": request.form.get("name"),
        "rollno": request.form.get("rollno"),
        "dob": request.form.get("dob"),
        "class": request.form.get("class"),
        "gender": request.form.get("gender"),
        "phone": request.form.get("phone")
    }
    subprocess.run(["python", "Backend/Database/FetchDetailofForm.py", json.dumps(data)])
    return redirect(url_for('newUser'))


@app.route("/newUser")
def newUser():
    if not session.get("logged_in") or session.get("role") != "teacher":
        return redirect(url_for("first"))
    user_id = session.get("user_id")

    # Fetch teacher details from DB
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT Class FROM ClassTeachers WHERE TeacherID = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        teacher_data = {
            "class": row[0]
        }
    return render_template("newUser.html", teacher=teacher_data)


@app.route('/attendance-mark', methods=['GET', 'POST'])
def mark_attendance_api():
    if not session.get("logged_in") or session.get("role") != "teacher":
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    # Get teacher's class
    teacher_id = session.get("user_id")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT Class FROM ClassTeachers WHERE TeacherID = ?", (teacher_id,))
    teacher_class = cursor.fetchone()[0]
    
    student = run_face_attendance()
    if student:
        # Validate student belongs to teacher's class
        cursor.execute("SELECT Class FROM Students WHERE StudentID = ?", (student['StudentID'],))
        student_class_result = cursor.fetchone()
        
        if not student_class_result:
            conn.close()
            return jsonify({
                'status': 'fail',
                'message': "Student not found in database"
            }), 404
            
        student_class = student_class_result[0]
        
        if student_class != teacher_class:
            conn.close()
            return jsonify({
                'status': 'fail', 
                'message': f"Access denied: {student['Name']} belongs to class {student_class}, but you teach class {teacher_class}"
            }), 403
        
        conn.close()
        # Store student data in session for success page
        session['attendance_student'] = student
        return redirect(url_for('attendance_success'))
    else:
        conn.close()
        return jsonify({
            'status': 'fail',
            'message': "No student recognized"
        }), 404

@app.route('/attendance-success')
def attendance_success():
    if not session.get("logged_in") or session.get("role") != "teacher":
        return redirect(url_for("first"))
    
    student = session.pop('attendance_student', None)
    if not student:
        return redirect(url_for('teacher'))
    
    return render_template("showingAttendanceMarked.html", student=student)


@app.route('/api/reports/generate', methods=['GET'])
def generate_reports():
    return jsonify({'status': 'success', 'message': 'Generate reports endpoint - Flask integration pending'})


@app.route('/api/students/list', methods=['GET'])
def list_students():
    return jsonify({'status': 'success', 'message': 'List students endpoint - Flask integration pending'})


@app.route('/api/sync/cloud', methods=['POST'])
def sync_data():
    return jsonify({'status': 'success', 'message': 'Sync data endpoint - Flask integration pending'})

def analysis(StuID):
    import tempfile
    from PIL import Image, ImageDraw, ImageFont
    from datetime import datetime
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get attendance data
    cursor.execute("SELECT COUNT(*) FROM Attendance WHERE StudentID = ? AND Status = 'Present'", (StuID,))
    present = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT MAX(DayID) FROM SchoolDays")
    total = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT Name, Class FROM Students WHERE StudentID = ?", (StuID,))
    student_info = cursor.fetchone()
    
    conn.close()
    
    # Create professional report
    img = Image.new('RGB', (1000, 700), color='#ffffff')
    draw = ImageDraw.Draw(img)
    
    # Load fonts
    try:
        font_title = ImageFont.truetype('/System/Library/Fonts/Arial Bold.ttf', 48)
        font_large = ImageFont.truetype('/System/Library/Fonts/Arial Bold.ttf', 32)
        font_medium = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 24)
        font_small = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 18)
    except:
        font_title = font_large = font_medium = font_small = ImageFont.load_default()
    
    # Header background
    draw.rectangle([0, 0, 1000, 120], fill='#2c3e50')
    draw.text((50, 35), '📊 SMART ATTENDANCE REPORT', fill='white', font=font_title)
    
    # Student info section
    draw.rectangle([50, 150, 950, 280], fill='#ecf0f1', outline='#bdc3c7', width=2)
    draw.text((70, 170), 'STUDENT INFORMATION', fill='#2c3e50', font=font_large)
    
    if student_info:
        draw.text((70, 220), f'Name: {student_info[0]}', fill='#34495e', font=font_medium)
        draw.text((500, 220), f'Class: {student_info[1]}', fill='#34495e', font=font_medium)
    draw.text((70, 250), f'Student ID: {StuID}', fill='#34495e', font=font_medium)
    
    # Attendance stats section
    draw.rectangle([50, 320, 950, 520], fill='#f8f9fa', outline='#bdc3c7', width=2)
    draw.text((70, 340), 'ATTENDANCE STATISTICS', fill='#2c3e50', font=font_large)
    
    # Stats boxes
    absent = total - present
    percentage = (present / total * 100) if total > 0 else 0
    
    # Present days box
    draw.rectangle([70, 390, 300, 480], fill='#d5f4e6', outline='#27ae60', width=3)
    draw.text((90, 405), 'PRESENT DAYS', fill='#27ae60', font=font_medium)
    draw.text((90, 435), str(present), fill='#27ae60', font=font_large)
    
    # Absent days box
    draw.rectangle([320, 390, 550, 480], fill='#fadbd8', outline='#e74c3c', width=3)
    draw.text((340, 405), 'ABSENT DAYS', fill='#e74c3c', font=font_medium)
    draw.text((340, 435), str(absent), fill='#e74c3c', font=font_large)
    
    # Percentage box
    perc_color = '#27ae60' if percentage >= 75 else '#f39c12' if percentage >= 50 else '#e74c3c'
    draw.rectangle([570, 390, 800, 480], fill='#fff3cd' if percentage >= 50 else '#fadbd8', outline=perc_color, width=3)
    draw.text((590, 405), 'ATTENDANCE RATE', fill=perc_color, font=font_medium)
    draw.text((590, 435), f'{percentage:.1f}%', fill=perc_color, font=font_large)
    
    # Total days
    draw.text((820, 420), f'Total School Days: {total}', fill='#7f8c8d', font=font_medium)
    
    # Footer
    draw.rectangle([0, 580, 1000, 700], fill='#34495e')
    current_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    draw.text((50, 610), f'Report Generated: {current_date}', fill='white', font=font_small)
    draw.text((50, 640), 'Smart Attendance System - Automated Report', fill='#bdc3c7', font=font_small)
    
    # Performance indicator
    if percentage >= 90:
        status = '🌟 EXCELLENT'
        status_color = '#27ae60'
    elif percentage >= 75:
        status = '✅ GOOD'
        status_color = '#27ae60'
    elif percentage >= 50:
        status = '⚠️ NEEDS IMPROVEMENT'
        status_color = '#f39c12'
    else:
        status = '❌ CRITICAL'
        status_color = '#e74c3c'
    
    draw.text((500, 610), f'Performance: {status}', fill=status_color, font=font_medium)
    
    # Save to temp file
    temp_dir = tempfile.gettempdir()
    filename = os.path.join(temp_dir, f"attendance_{StuID}_{int(time.time())}.png")
    img.save(filename, quality=95)
    
    return filename

@app.route('/attendance-analysis')
def attendance_analysis():
    if not session.get("logged_in") or session.get("role") != "student":
        return redirect(url_for("first"))
    
    StuID = request.args.get('id')
    if not StuID:
        return redirect(url_for('student'))
    
    # Get attendance data for charts
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get present days
    cursor.execute("""
        SELECT COUNT(Date) FROM Attendance
        WHERE StudentID = ? AND Status = 'Present'
    """, (StuID,))
    present = cursor.fetchone()[0] or 0
    
    # Get total school days
    cursor.execute("SELECT MAX(DayID) FROM SchoolDays")
    total = cursor.fetchone()[0] or 0
    
    # Get student info
    cursor.execute("SELECT Name, Class FROM Students WHERE StudentID = ?", (StuID,))
    student_info = cursor.fetchone()
    
    conn.close()
    
    absent = total - present
    percentage = (present / total * 100) if total > 0 else 0
    
    chart_data = {
        'present': present,
        'absent': absent,
        'total': total,
        'percentage': round(percentage, 1),
        'student_name': student_info[0] if student_info else 'Unknown',
        'student_class': student_info[1] if student_info else 'Unknown',
        'student_id': StuID
    }
    
    return render_template('attendance_chart.html', data=chart_data)

@app.route('/download-report')
def download_report():
    if not session.get("logged_in") or session.get("role") != "student":
        return redirect(url_for("first"))
    
    StuID = request.args.get('id')
    if not StuID:
        return redirect(url_for('student'))
    
    # Generate report in memory without saving to disk
    import tempfile
    import os
    
    try:
        # Generate the chart and save to temporary file
        temp_file = analysis(StuID)
        
        # Send file and then clean up
        def remove_file(response):
            try:
                os.remove(temp_file)
            except Exception:
                pass
            return response
        
        return send_file(temp_file, as_attachment=True, 
                        download_name=f'Attendance_Report_{StuID}.png', 
                        mimetype='image/png')
    except Exception as e:
        return jsonify({"error": "Failed to generate report"}), 500

def attend_percentage(StudentID):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    total = c.execute("""
        SELECT MAX(DayID) FROM SchoolDays
    """).fetchone()[0]

    if not total or total == 0:
        conn.close()
        return 0

    present_days = c.execute("""
        SELECT COUNT(Date) FROM Attendance
        WHERE StudentID = ? AND Status = ?
    """, (StudentID, "Present")).fetchone()[0]

    conn.close()

    return (present_days / total) * 100

@app.route('/attendance_percentage', methods=['GET'])
def get_attendance_percentage():
    StudentID = request.args.get('StudentID')
    if not StudentID:
        return jsonify({"error": "StudentID is required"}), 400

    try:
        percentage = attend_percentage(StudentID)
        return jsonify({
            "percentage": round(percentage, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/admin/database-status')
def database_status():
    """Admin route to check database status"""
    if not session.get("logged_in") or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 401
    
    status = check_database_status()
    return jsonify(status)

@app.route('/admin/init-database')
def init_database():
    """Admin route to initialize database tables"""
    if not session.get("logged_in") or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        create_tables()
        return jsonify({"status": "success", "message": "Database initialized successfully"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/check-class-teacher', methods=['GET'])
def check_class_teacher():
    if not session.get("logged_in") or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 401
    
    class_name = request.args.get('class')
    if not class_name:
        return jsonify({"error": "Class parameter required"}), 400
    
    admin_school = session.get("admin_school")
    if not admin_school:
        return jsonify({"error": "School not found"}), 400
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ClassTeachers WHERE Class = ? AND (School = ? OR School IS NULL)", (class_name, admin_school,))
    count = cursor.fetchone()[0]
    conn.close()
    
    return jsonify({"exists": count > 0})

@app.route('/check-teacher-email', methods=['GET'])
def check_teacher_email():
    if not session.get("logged_in") or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 401
    
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email parameter required"}), 400
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ClassTeachers WHERE Email = ?", (email,))
    count = cursor.fetchone()[0]
    conn.close()
    
    return jsonify({"exists": count > 0})

@app.route('/check-teacher-phone', methods=['GET'])
def check_teacher_phone():
    if not session.get("logged_in") or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 401
    
    phone = request.args.get('phone')
    if not phone:
        return jsonify({"error": "Phone parameter required"}), 400
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ClassTeachers WHERE Phone = ?", (phone,))
    count = cursor.fetchone()[0]
    conn.close()
    
    return jsonify({"exists": count > 0})

@app.route('/validate-teacher', methods=['POST'])
def validate_teacher():
    if not session.get("logged_in") or session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    conflicts = {}
    if data.get('class'):
        cursor.execute("SELECT COUNT(*) FROM ClassTeachers WHERE Class = ?", (data['class'],))
        if cursor.fetchone()[0] > 0:
            conflicts['class'] = 'Class already has a teacher'
    
    if data.get('email'):
        cursor.execute("SELECT COUNT(*) FROM ClassTeachers WHERE Email = ?", (data['email'],))
        if cursor.fetchone()[0] > 0:
            conflicts['email'] = 'Email already registered'
    
    if data.get('phone'):
        cursor.execute("SELECT COUNT(*) FROM ClassTeachers WHERE Phone = ?", (data['phone'],))
        if cursor.fetchone()[0] > 0:
            conflicts['phone'] = 'Phone already registered'
    
    conn.close()
    return jsonify({"valid": len(conflicts) == 0, "conflicts": conflicts})

@app.route('/teacher-records')
def teacher_records():
    if not session.get("logged_in") or session.get("role") != "admin":
        return redirect(url_for("first"))
    
    admin_school = session.get("admin_school")
    if not admin_school:
        return redirect(url_for("admin"))
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TeacherID, Name, Email, Phone, Gender, DOB, Class, Password 
        FROM ClassTeachers
        WHERE School = ? OR School IS NULL
        ORDER BY Name
    """, (admin_school,))
    teachers = cursor.fetchall()
    conn.close()
    
    return render_template("teacher_records.html", teachers=teachers)

def ratio(StuID):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    present = c.execute("""
        SELECT COUNT(Date) FROM Attendance
        WHERE StudentID = ? AND Status = 'Present'
    """, (StuID,)).fetchone()[0]

    total = c.execute("""
        SELECT MAX(DayID) FROM SchoolDays
    """).fetchone()[0]

    conn.close()
    return total, present

@app.route('/api/attendance/<int:StuID>')
def api_attendance(StuID):
    total, present = ratio(StuID)
    return jsonify({
        "StudentID": StuID,
        "TotalDays": total,
        "PresentDays": present
    })

@app.route('/attendance/<int:StuID>')
def attendance_page(StuID):
    total, present = ratio(StuID)
    return render_template("attendance.html", student_id=StuID, total=total, present=present)

@app.route('/analytics')
def analytics():
    if not session.get("logged_in") or session.get("role") != "teacher":
        return redirect(url_for("first"))
    
    user_id = session.get("user_id")
    
    # Get teacher's class
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT Class FROM ClassTeachers WHERE TeacherID = ?", (user_id,))
    teacher_class = cursor.fetchone()[0]
    
    # Get all students in teacher's class with attendance data
    cursor.execute("""
        SELECT s.StudentID, s.Name, s.RollNumber,
               COUNT(CASE WHEN a.Status = 'Present' THEN 1 END) as present_days,
               COUNT(a.AttendanceID) as total_marked_days,
               (SELECT MAX(DayID) FROM SchoolDays) as total_school_days
        FROM Students s
        LEFT JOIN Attendance a ON s.StudentID = a.StudentID
        WHERE s.Class = ?
        GROUP BY s.StudentID, s.Name, s.RollNumber
        ORDER BY s.RollNumber
    """, (teacher_class,))
    
    students_data = []
    for row in cursor.fetchall():
        student_id, name, roll, present, marked, total_school = row
        percentage = (present / total_school * 100) if total_school > 0 else 0
        students_data.append({
            'id': student_id,
            'name': name,
            'roll': roll,
            'present': present,
            'total': total_school,
            'percentage': round(percentage, 1)
        })
    
    conn.close()
    
    return render_template("analytics.html", 
                         students=students_data, 
                         teacher_class=teacher_class)

@app.route('/teacher-analytics')
def teacher_analytics():
    if not session.get("logged_in") or session.get("role") != "teacher":
        return redirect(url_for("first"))
    
    user_id = session.get("user_id")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get teacher info
    cursor.execute("SELECT Name, Class FROM ClassTeachers WHERE TeacherID = ?", (user_id,))
    teacher_info = cursor.fetchone()
    teacher_class = teacher_info[1]
    
    # Get class statistics
    cursor.execute("SELECT COUNT(*) FROM Students WHERE Class = ?", (teacher_class,))
    total_students = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT MAX(DayID) FROM SchoolDays")
    total_days = cursor.fetchone()[0] or 0
    
    # Get today's attendance
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    cursor.execute("""
        SELECT COUNT(*) FROM Attendance a
        JOIN Students s ON a.StudentID = s.StudentID
        WHERE s.Class = ? AND a.Date = ? AND a.Status = 'Present'
    """, (teacher_class, today))
    present_today = cursor.fetchone()[0] or 0
    
    # Calculate overall class attendance rate
    cursor.execute("""
        SELECT COUNT(CASE WHEN a.Status = 'Present' THEN 1 END) as total_present,
               COUNT(*) as total_records
        FROM Attendance a
        JOIN Students s ON a.StudentID = s.StudentID
        WHERE s.Class = ?
    """, (teacher_class,))
    attendance_stats = cursor.fetchone()
    class_attendance_rate = (attendance_stats[0] / attendance_stats[1] * 100) if attendance_stats[1] > 0 else 0
    
    conn.close()
    
    chart_data = {
        'total_students': total_students,
        'present_today': present_today,
        'absent_today': total_students - present_today,
        'total_days': total_days,
        'class_attendance_rate': round(class_attendance_rate, 1),
        'teacher_name': teacher_info[0],
        'teacher_class': teacher_class,
        'teacher_id': user_id
    }
    
    return render_template('teacher_analytics.html', data=chart_data)

@app.route('/teacher-student-analytics/<student_id>')
def teacher_student_analytics(student_id):
    if not session.get("logged_in") or session.get("role") != "teacher":
        return redirect(url_for("first"))
    
    # Verify student belongs to teacher's class
    teacher_id = session.get("user_id")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT Class FROM ClassTeachers WHERE TeacherID = ?", (teacher_id,))
    teacher_class = cursor.fetchone()[0]
    
    cursor.execute("SELECT Class, Name FROM Students WHERE StudentID = ?", (student_id,))
    student_info = cursor.fetchone()
    
    if not student_info or student_info[0] != teacher_class:
        conn.close()
        return redirect(url_for('analytics'))
    
    # Get attendance data for charts
    cursor.execute("SELECT COUNT(*) FROM Attendance WHERE StudentID = ? AND Status = 'Present'", (student_id,))
    present = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT MAX(DayID) FROM SchoolDays")
    total = cursor.fetchone()[0] or 0
    
    conn.close()
    
    absent = total - present
    percentage = (present / total * 100) if total > 0 else 0
    
    chart_data = {
        'present': present,
        'absent': absent,
        'total': total,
        'percentage': round(percentage, 1),
        'student_name': student_info[1],
        'student_class': student_info[0],
        'student_id': student_id
    }
    
    return render_template('teacher_student_analytics.html', data=chart_data)

@app.route('/profile')
def profile():
    if not session.get("logged_in") or session.get("role") != "student":
        return redirect(url_for("first"))
    
    user_id = session.get("user_id")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT Name, StudentID, Class, RollNumber, Phone FROM Students WHERE StudentID = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        student_data = {
            "name": row[0],
            "id": row[1],
            "class": row[2],
            "roll": row[3],
            "phone": row[4]
        }
    return render_template("profile.html", student=student_data)

@app.route('/update-profile', methods=['POST'])
def update_profile():
    if not session.get("logged_in") or session.get("role") != "student":
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    user_id = session.get("user_id")
    password = request.form.get('password')
    
    if not password:
        return jsonify({"status": "error", "message": "Password is required"}), 400
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Only update password for students
        cursor.execute("""
            UPDATE Students 
            SET Password = ?
            WHERE StudentID = ?
        """, (password, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Password updated successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/teacher-profile')
def teacher_profile():
    if not session.get("logged_in") or session.get("role") != "teacher":
        return redirect(url_for("first"))
    
    user_id = session.get("user_id")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT Name, TeacherID, Class, Email, Phone FROM ClassTeachers WHERE TeacherID = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        teacher_data = {
            "name": row[0],
            "id": row[1],
            "class": row[2],
            "email": row[3],
            "phone": row[4]
        }
    return render_template("teacher_profile.html", teacher=teacher_data)

@app.route('/update-teacher-profile', methods=['POST'])
def update_teacher_profile():
    if not session.get("logged_in") or session.get("role") != "teacher":
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    user_id = session.get("user_id")
    password = request.form.get('password')
    
    if not password:
        return jsonify({"status": "error", "message": "Password is required"}), 400
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE ClassTeachers 
            SET Password = ?
            WHERE TeacherID = ?
        """, (password, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({"status": "success", "message": "Password updated successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/admin-analytics')
def admin_analytics():
    if not session.get("logged_in") or session.get("role") != "admin":
        return redirect(url_for("first"))
    
    selected_class = request.args.get('class', 'all')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all available classes
    cursor.execute("SELECT DISTINCT Class FROM Students ORDER BY Class")
    all_classes = [row[0] for row in cursor.fetchall()]
    
    # Get students based on selected class
    if selected_class == 'all':
        cursor.execute("""
            SELECT s.StudentID, s.Name, s.Class, s.RollNumber,
                   COUNT(CASE WHEN a.Status = 'Present' THEN 1 END) as present_days,
                   (SELECT MAX(DayID) FROM SchoolDays) as total_school_days
            FROM Students s
            LEFT JOIN Attendance a ON s.StudentID = a.StudentID
            GROUP BY s.StudentID, s.Name, s.Class, s.RollNumber
            ORDER BY s.Class, s.RollNumber
        """)
    else:
        cursor.execute("""
            SELECT s.StudentID, s.Name, s.Class, s.RollNumber,
                   COUNT(CASE WHEN a.Status = 'Present' THEN 1 END) as present_days,
                   (SELECT MAX(DayID) FROM SchoolDays) as total_school_days
            FROM Students s
            LEFT JOIN Attendance a ON s.StudentID = a.StudentID
            WHERE s.Class = ?
            GROUP BY s.StudentID, s.Name, s.Class, s.RollNumber
            ORDER BY s.RollNumber
        """, (selected_class,))
    
    students_data = []
    for row in cursor.fetchall():
        student_id, name, class_name, roll, present, total_school = row
        percentage = (present / total_school * 100) if total_school > 0 else 0
        students_data.append({
            'id': student_id,
            'name': name,
            'class': class_name,
            'roll': roll,
            'present': present,
            'total': total_school,
            'percentage': round(percentage, 1)
        })
    
    conn.close()
    
    return render_template("admin_analytics.html", 
                         students=students_data, 
                         all_classes=all_classes,
                         selected_class=selected_class)

@app.route('/government-reports')
def government_reports():
    if not session.get("logged_in") or session.get("role") != "admin":
        return redirect(url_for("first"))
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get total students
    cursor.execute("SELECT COUNT(*) FROM Students")
    total_students = cursor.fetchone()[0]
    
    # Get class-wise breakdown
    cursor.execute("""
        SELECT Class, COUNT(*) as student_count
        FROM Students 
        GROUP BY Class 
        ORDER BY Class
    """)
    class_breakdown = cursor.fetchall()
    
    # Get today's present students (for meal calculation)
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    
    cursor.execute("""
        SELECT COUNT(*) FROM Attendance 
        WHERE Date = ? AND Status = 'Present'
    """, (today,))
    present_today = cursor.fetchone()[0]
    
    # Calculate meal requirements (assuming 1 meal per present student)
    meals_required = present_today
    
    conn.close()
    
    return render_template("government_reports.html", 
                         total_students=total_students,
                         class_breakdown=class_breakdown,
                         present_today=present_today,
                         meals_required=meals_required,
                         report_date=today)

@app.route('/download-government-report')
def download_government_report():
    if not session.get("logged_in") or session.get("role") != "admin":
        return redirect(url_for("first"))
    
    import tempfile
    from PIL import Image, ImageDraw, ImageFont
    from datetime import datetime
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get report data
    cursor.execute("SELECT COUNT(*) FROM Students")
    total_students = cursor.fetchone()[0]
    
    cursor.execute("SELECT Class, COUNT(*) FROM Students GROUP BY Class ORDER BY Class")
    class_breakdown = cursor.fetchall()
    
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) FROM Attendance WHERE Date = ? AND Status = 'Present'", (today,))
    present_today = cursor.fetchone()[0]
    
    conn.close()
    
    # Create beautiful government report
    img = Image.new('RGB', (1400, 1000), color='#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype('/System/Library/Fonts/Arial Bold.ttf', 48)
        font_subtitle = ImageFont.truetype('/System/Library/Fonts/Arial Bold.ttf', 32)
        font_large = ImageFont.truetype('/System/Library/Fonts/Arial Bold.ttf', 28)
        font_medium = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 22)
        font_small = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 18)
    except:
        font_title = font_subtitle = font_large = font_medium = font_small = ImageFont.load_default()
    
    # Header with gradient effect
    draw.rectangle([0, 0, 1400, 120], fill='#1a365d')
    draw.rectangle([0, 120, 1400, 140], fill='#2d5a87')
    draw.text((60, 35), '🏛️ GOVERNMENT DAILY ATTENDANCE REPORT', fill='white', font=font_title)
    
    # School info section
    draw.rectangle([60, 180, 1340, 280], fill='white', outline='#e2e8f0', width=3)
    draw.rectangle([60, 180, 1340, 220], fill='#edf2f7')
    draw.text((80, 190), 'SCHOOL INFORMATION', fill='#2d3748', font=font_large)
    draw.text((80, 240), f'Report Date: {datetime.now().strftime("%B %d, %Y")}', fill='#4a5568', font=font_medium)
    draw.text((600, 240), f'Academic Session: {datetime.now().year}-{datetime.now().year + 1}', fill='#4a5568', font=font_medium)
    
    # Statistics cards
    attendance_rate = (present_today / total_students * 100) if total_students > 0 else 0
    cards = [
        {'title': 'TOTAL ENROLLMENT', 'value': str(total_students), 'color': '#3182ce', 'x': 60},
        {'title': 'PRESENT TODAY', 'value': str(present_today), 'color': '#38a169', 'x': 360},
        {'title': 'MEALS REQUIRED', 'value': str(present_today), 'color': '#d69e2e', 'x': 660},
        {'title': 'ATTENDANCE RATE', 'value': f'{attendance_rate:.1f}%', 'color': '#805ad5', 'x': 960}
    ]
    
    for card in cards:
        # Card background
        draw.rectangle([card['x'], 320, card['x'] + 280, 450], fill='white', outline='#e2e8f0', width=2)
        # Card header
        draw.rectangle([card['x'], 320, card['x'] + 280, 360], fill=card['color'])
        draw.text((card['x'] + 20, 330), card['title'], fill='white', font=font_medium)
        # Card value
        draw.text((card['x'] + 20, 380), card['value'], fill=card['color'], font=font_subtitle)
    
    # Class breakdown section
    draw.rectangle([60, 490, 1340, 800], fill='white', outline='#e2e8f0', width=3)
    draw.rectangle([60, 490, 1340, 530], fill='#edf2f7')
    draw.text((80, 500), 'CLASS-WISE ENROLLMENT BREAKDOWN', fill='#2d3748', font=font_large)
    
    # Class data in table format
    y_pos = 570
    draw.text((100, y_pos), 'CLASS', fill='#4a5568', font=font_medium)
    draw.text((300, y_pos), 'STUDENTS', fill='#4a5568', font=font_medium)
    draw.text((500, y_pos), 'PERCENTAGE', fill='#4a5568', font=font_medium)
    
    # Draw line under headers
    draw.line([(80, y_pos + 35), (1320, y_pos + 35)], fill='#cbd5e0', width=2)
    
    y_pos += 50
    for i, (class_name, count) in enumerate(class_breakdown):
        percentage = (count / total_students * 100) if total_students > 0 else 0
        
        # Alternating row colors
        if i % 2 == 0:
            draw.rectangle([80, y_pos - 10, 1320, y_pos + 25], fill='#f7fafc')
        
        draw.text((100, y_pos), f'Class {class_name}', fill='#2d3748', font=font_medium)
        draw.text((300, y_pos), str(count), fill='#2d3748', font=font_medium)
        draw.text((500, y_pos), f'{percentage:.1f}%', fill='#2d3748', font=font_medium)
        
        # Progress bar
        bar_width = int(percentage * 2)
        draw.rectangle([650, y_pos + 5, 650 + bar_width, y_pos + 15], fill='#4299e1')
        draw.rectangle([650, y_pos + 5, 850, y_pos + 15], outline='#cbd5e0', width=1)
        
        y_pos += 40
    
    # Summary box
    draw.rectangle([60, 820, 1340, 920], fill='#e6fffa', outline='#38b2ac', width=3)
    draw.text((80, 840), 'SUMMARY FOR GOVERNMENT NUTRITION PROGRAM', fill='#234e52', font=font_large)
    draw.text((80, 880), f'Total Mid-Day Meals Required: {present_today} meals for {present_today} present students', fill='#285e61', font=font_medium)
    
    # Footer
    draw.rectangle([0, 940, 1400, 1000], fill='#2d3748')
    current_time = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    draw.text((60, 955), f'Generated: {current_time}', fill='white', font=font_medium)
    draw.text((60, 975), 'Smart Attendance System - Official Government Report', fill='#a0aec0', font=font_small)
    draw.text((1000, 955), 'CONFIDENTIAL', fill='#fed7d7', font=font_medium)
    draw.text((1000, 975), 'For Official Use Only', fill='#a0aec0', font=font_small)
    
    # Save to temp file
    temp_dir = tempfile.gettempdir()
    filename = os.path.join(temp_dir, f"government_report_{int(time.time())}.png")
    img.save(filename, quality=95)
    
    return send_file(filename, as_attachment=True, 
                    download_name=f'Government_Report_{today}.png', 
                    mimetype='image/png')



if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)