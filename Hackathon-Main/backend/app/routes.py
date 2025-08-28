from flask import Blueprint, request, jsonify
from app.database import query_db, modify_db,get_db
# Add this new import at the top of routes.py for password hashing
import hashlib
from datetime import datetime
import sqlite3

# Create a Blueprint to organize our routes
bp = Blueprint('api', __name__)

@bp.route('/')
def home():
    return "<h1>My School Attendance Backend is Running!</h1><p>Try visiting <a href='/api/test'>/api/test</a></p>"

# Add a simple JSON API test route
@bp.route('/api/test')
def test_api():
    return jsonify({"status": "success", "message": "The API is working correctly!"})

# Example API: Get all users
@bp.route('/api/users', methods=['GET'])
def get_users():
    users = query_db('SELECT * FROM users')
    # Convert sqlite3.Row objects to dictionaries for JSON response
    users_list = [dict(user) for user in users]
    return jsonify(users_list)

#Register
# You will add more APIs here for:
@bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    gender = data['gender']
    dob = data['dob']
    role = data['role']
    plain_text_password = data['password']

    # First, hash the password for security
    hashed_password = hashlib.sha256(plain_text_password.encode()).hexdigest()

    # We will attempt to insert the user without the sha1_id first.
    # We'll generate the sha1_id based on the new database row's unique ID.
    try:
        # First, insert the user to get a unique database ID
        db = get_db()
        cur = db.execute(
            'INSERT INTO users (name, gender, dob, role, password) VALUES (?, ?, ?, ?, ?)',
            (name, gender, dob, role, hashed_password)
        )
        db.commit()
        # Get the auto-incremented ID of the newly inserted user
        new_user_id = cur.lastrowid

        # NOW, generate a unique sha1_id using the new unique database ID
        unique_string = f"{name}{gender}{dob}{role}{new_user_id}"
        full_hash = hashlib.sha1(unique_string.encode()).hexdigest()
        all_digits = ''.join(char for char in full_hash if char.isdigit())
        sha1_id = (all_digits + '0' * 10)[:10]

        # Update the user record with the generated sha1_id
        db.execute(
            'UPDATE users SET sha1_id = ? WHERE id = ?',
            (sha1_id, new_user_id)
        )
        db.commit()

        return jsonify({
            "status": "success",
            "message": "User registered successfully",
            "sha1_id": sha1_id
        }), 201

    except sqlite3.IntegrityError:
        # This might still happen if there's a miraculous hash collision, but it's extremely unlikely.
        return jsonify({"status": "error", "message": "Registration failed. Please try again."}), 400
# - Login
# NEW API: User Login (Uses sha1_id)
@bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    # Frontend now only sends sha1_id and password
    sha1_id = data.get('sha1_id')
    password_attempt = data.get('password') # This is still plain text

    # 1. Find the user by their unique sha1_id
    user = query_db('SELECT * FROM users WHERE sha1_id = ?', (sha1_id,), one=True)

    # 2. Check if user exists
    if user is None:
        return jsonify({"status": "error", "message": "User not found"}), 401

    # 3. Hash the attempted password using the same method (sha256)
    hashed_attempt = hashlib.sha256(password_attempt.encode()).hexdigest()

    # 4. Compare the new hash with the stored hash
    if hashed_attempt != user['password']:
        return jsonify({"status": "error", "message": "Wrong password"}), 401

    # 5. If everything is correct, return success
    return jsonify({
        "status": "success",
        "message": "Login successful",
        "user": {
            "sha1_id": user['sha1_id'],
            "name": user['name'],
            "role": user['role']
            # Don't send back sensitive data like password or DOB
        }
    })
# - Taking attendance

# API: Mark Attendance (Option 3 - Simplified)
@bp.route('/api/attendance', methods=['POST'])
def mark_attendance():
    """
    Mark attendance for a student.
    Expects JSON: {"sha1_id": "1234567890", "class": "5B"}
    """
    # 1. Get data from the AI module's request
    data = request.get_json()

    # Validate that we received JSON data
    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    sha1_id = data.get('sha1_id')
    class_name = data.get('class')

    # 2. Input validation
    if not sha1_id or not class_name:
        return jsonify({"status": "error", "message": "Missing sha1_id or class"}), 400

    # 3. Verify the user exists and is a student
    try:
        user = query_db('SELECT * FROM users WHERE sha1_id = ?', (sha1_id,), one=True)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

    if user is None:
        return jsonify({"status": "error", "message": "Student not found"}), 404

    if user['role'] != 'Student':
        return jsonify({"status": "error", "message": "User is not a student"}), 400

    # 4. Check if attendance already marked today (prevent duplicates)
    try:
        today = datetime.now().date()
        existing_attendance = query_db(
            'SELECT * FROM student_attendance WHERE sha1_id = ? AND DATE(attendance_time) = ? AND class = ?',
            (sha1_id, today, class_name), one=True
        )
    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500

    if existing_attendance:
        return jsonify({
            "status": "success",
            "message": "Attendance already marked today for this class",
            "attendance_id": existing_attendance['id']
        }), 200

    # 5. Insert new attendance record (JUST the facts - no percentage calculation)
    try:
        # Insert the attendance record
        new_id = modify_db(
            'INSERT INTO student_attendance (sha1_id, class) VALUES (?, ?)',
            (sha1_id, class_name)
        )

        # Get the complete record to return to the client
        new_record = query_db(
            'SELECT * FROM student_attendance WHERE id = ?',
            (new_id,), one=True
        )

        return jsonify({
            "status": "success",
            "message": "Attendance marked successfully",
            "attendance_id": new_id,
            "attendance_record": dict(new_record) if new_record else None
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to save attendance: {str(e)}"}), 500


# Add this helper function to your routes.py
def get_attendance_stats(sha1_id, class_name):
    """
    Helper function to calculate detailed attendance statistics for a student in a specific class.
    Returns: dictionary with attendance statistics
    """
    if not class_name:
        return {
            "total_classes_held": 0,
            "classes_attended": 0,
            "attendance_percentage": 0.0,
            "last_attendance": None
        }

    # Get total number of distinct days this class has met
    total_result = query_db(
        'SELECT COUNT(DISTINCT DATE(attendance_time)) as count FROM student_attendance WHERE class = ?',
        (class_name,), one=True
    )
    total_classes = total_result['count'] if total_result else 0

    # Get number of distinct days this student attended this class
    attended_result = query_db(
        'SELECT COUNT(DISTINCT DATE(attendance_time)) as count FROM student_attendance WHERE sha1_id = ? AND class = ?',
        (sha1_id, class_name), one=True
    )
    classes_attended = attended_result['count'] if attended_result else 0

    # Get last attendance date
    last_attendance_result = query_db(
        'SELECT DATE(attendance_time) as last_date FROM student_attendance WHERE sha1_id = ? AND class = ? ORDER BY attendance_time DESC LIMIT 1',
        (sha1_id, class_name), one=True
    )
    last_attendance = last_attendance_result['last_date'] if last_attendance_result else None

    # Calculate percentage
    attendance_percentage = (classes_attended / total_classes * 100) if total_classes > 0 else 0.0

    return {
        "total_classes_held": total_classes,
        "classes_attended": classes_attended,
        "attendance_percentage": round(attendance_percentage, 2),
        "last_attendance": last_attendance
    }

# API: Get Student Attendance (With Enhanced Statistics)
@bp.route('/api/attendance/<sha1_id>', methods=['GET'])
def get_attendance(sha1_id):
    try:
        # 1. Verify the user exists and is a student
        user = query_db('SELECT * FROM users WHERE sha1_id = ?', (sha1_id,), one=True)

        if user is None:
            return jsonify({"status": "error", "message": "Student not found"}), 404
        if user['role'] != 'Student':
            return jsonify({"status": "error", "message": "User is not a student"}), 400

        # 2. Get current class (most recent class from attendance records)
        current_class_result = query_db(
            'SELECT class FROM student_attendance WHERE sha1_id = ? ORDER BY attendance_time DESC LIMIT 1',
            (sha1_id,), one=True
        )
        current_class = current_class_result['class'] if current_class_result else None

        # 3. Calculate statistics using helper function
        stats = get_attendance_stats(sha1_id, current_class)

        # 4. Get all attendance records for detailed view
        attendance_records = query_db(
            'SELECT * FROM student_attendance WHERE sha1_id = ? ORDER BY attendance_time DESC',
            (sha1_id,)
        )

        # 5. Prepare response
        records_list = [dict(record) for record in attendance_records] if attendance_records else []

        response_data = {
            "status": "success",
            "student_info": {
                "sha1_id": user['sha1_id'],
                "name": user['name'],
                "current_class": current_class
            },
            "attendance_summary": stats,
            "attendance_records": records_list
        }

        if not attendance_records:
            response_data["message"] = "No attendance records found"

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Failed to fetch attendance: {str(e)}"}), 500
# - Extra
# Get all classes (for dropdown selection)
@bp.route('/api/classes', methods=['GET'])
def get_classes():
    classes = query_db('SELECT DISTINCT class FROM student_attendance ORDER BY class')
    return jsonify({"classes": [cls['class'] for cls in classes]})

# Get student list for a class (for teacher view)
@bp.route('/api/class/<class_name>/students', methods=['GET'])
def get_class_students(class_name):
    students = query_db('''
        SELECT u.sha1_id, u.name, u.gender 
        FROM users u
        WHERE u.role = 'Student' AND u.sha1_id IN (
            SELECT DISTINCT sha1_id FROM student_attendance WHERE class = ?
        )
    ''', (class_name,))
    return jsonify({"students": [dict(student) for student in students]})
# - Chatbot messages
# - etc.