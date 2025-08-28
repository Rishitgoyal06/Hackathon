from flask import Flask, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('teacher.html')

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

@app.route('/student')
def student():
    return render_template('student.html')

# API endpoints - placeholders for future implementation
@app.route('/api/students/add', methods=['POST'])
def add_student():
    return jsonify({'status': 'success', 'message': 'Add student endpoint - Flask integration pending'})

@app.route('/api/attendance/mark', methods=['POST'])
def mark_attendance():
    return jsonify({'status': 'success', 'message': 'Mark attendance endpoint - Flask integration pending'})

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
    
    # Copy HTML files to templates directory
    import shutil
    shutil.copy('teacher.html', 'templates/')
    shutil.copy('student.html', 'templates/')
    
    print("🚀 Smart Attendance System Starting...")
    print("📘 Teacher Portal: http://localhost:5000/teacher")
    print("🎓 Student Portal: http://localhost:5000/student")
    
    app.run(debug=True, host='0.0.0.0', port=5000)