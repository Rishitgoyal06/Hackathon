# Backend API Documentation - Automated Attendance System

## 📋 Overview
This is the backend API for the **Automated Attendance System for Rural Schools** project. It provides RESTful APIs for user management, attendance tracking, and data management.

## 🚀 Base URL
```
http://localhost:5001/api
```

## 📊 Database Schema
The system uses SQLite with the following main tables:
- `users` - Student/Teacher/Admin information
- `student_attendance` - Attendance records
- `messages` - Chatbot conversations
- `teacher_classes` - Teacher-class assignments
- `face_encodings` - NOT USED YET !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

## 🔐 Authentication
Uses `sha1_id` + password authentication with SHA-256 hashing for security.

## 📱 API Endpoints

### 👥 User Management

#### 1. Register User
**POST** `/register`
```json
// Request
{
  "name": "Student Name",
  "gender": "Male",
  "dob": "2010-05-15",
  "role": "Student",
  "password": "password123"
}

// Response
{
  "status": "success",
  "message": "User registered successfully",
  "sha1_id": "5426899746"
}
```

#### 2. User Login
**POST** `/login`
```json
// Request
{
  "sha1_id": "5426899746",
  "password": "password123"
}

// Response
{
  "status": "success",
  "message": "Login successful",
  "user": {
    "sha1_id": "5426899746",
    "name": "Student Name",
    "role": "Student"
  }
}
```

### 📊 Attendance Management

#### 1. Mark Attendance
**POST** `/attendance`
```json
// Request
{
  "sha1_id": "5426899746",
  "class": "5B"
}

// Response
{
  "status": "success",
  "message": "Attendance marked successfully",
  "attendance_id": 15
}
```

#### 2. Get Student Attendance
**GET** `/attendance/{sha1_id}`
```json
// Example: GET /attendance/5426899746

// Response
{
  "status": "success",
  "student_info": {
    "sha1_id": "5426899746",
    "name": "Ravi Kumar",
    "current_class": "5B"
  },
  "attendance_summary": {
    "total_classes_held": 15,
    "classes_attended": 12,
    "attendance_percentage": 80.0
  },
  "attendance_records": [
    {
      "id": 15,
      "sha1_id": "5426899746",
      "class": "5B",
      "attendance_time": "2025-08-28 22:45:30"
    }
  ]
}
```

### 📊 Data Management

#### 1. Get All Students
**GET** `/students`
```json
// Response
{
  "status": "success",
  "students": [
    {
      "sha1_id": "5426899746",
      "name": "Ravi Kumar",
      "gender": "Male",
      "dob": "2010-05-15",
      "role": "Student"
    }
  ]
}
```

#### 2. Get Class Students
**GET** `/class/{class_name}/students`
```json
// Example: GET /class/5B/students

// Response
{
  "status": "success",
  "class": "5B",
  "students": [
    {
      "sha1_id": "5426899746",
      "name": "Ravi Kumar",
      "gender": "Male"
    }
  ]
}
```

#### 3. Get Available Classes
**GET** `/classes`
```json
// Response
{
  "status": "success",
  "classes": ["5A", "5B", "6A", "6B"]
}
```

## 🛠 Setup Instructions

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
1. Navigate to backend directory:
   ```bash
   cd your-project-backend
   ```

2. Create virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate    # Windows
   ```

3. Install dependencies:
   ```bash
   pip install flask
   ```

4. Initialize database:
   ```bash
   python
   >>> from app import create_app
   >>> from app.database import init_db
   >>> app = create_app()
   >>> with app.app_context():
   ...     init_db()
   ...
   Database initialized!
   >>> exit()
   ```

5. Run the server:
   ```bash
   python run.py
   ```

6. Server starts at: `http://localhost:5001`

## 🧪 Testing the APIs

### Step-by-Step Testing:

1. **First, register a user:**
   ```bash
   POST http://localhost:5001/api/register
   {
     "name": "Test Student",
     "gender": "Male",
     "dob": "2010-01-01",
     "role": "Student",
     "password": "test123"
   }
   ```

2. **Copy the `sha1_id` from the response**

3. **Login with the credentials:**
   ```bash
   POST http://localhost:5001/api/login
   {
     "sha1_id": "COPY_SHA1_ID_HERE",
     "password": "test123"
   }
   ```

4. **Mark attendance:**
   ```bash
   POST http://localhost:5001/api/attendance
   {
     "sha1_id": "COPY_SHA1_ID_HERE",
     "class": "5B"
   }
   ```

5. **Check attendance:**
   ```bash
   GET http://localhost:5001/api/attendance/COPY_SHA1_ID_HERE
   ```

### Using curl commands:
```bash
# Health check
curl http://localhost:5001/

# Get all students
curl http://localhost:5001/api/students

# Get available classes
curl http://localhost:5001/api/classes
```

## 📁 Project Structure
```
backend/
├── app/
│   ├── __init__.py      # Flask app initialization
│   ├── routes.py        # All API endpoints
│   ├── database.py      # Database connection & utilities
│   └── models.py        # Database schema
├── instance/
│   └── school_attendance.db  # Database file (auto-created)
├── run.py               # Application entry point
└── config.py           # Configuration settings
```

## 🔧 Error Handling
All APIs return standardized responses:
```json
{
  "status": "error",
  "message": "Descriptive error message"
}
```

Common HTTP Status Codes:
- `200` - Success
- `400` - Bad Request (missing parameters)
- `401` - Unauthorized (login failed)
- `404` - Not Found (student not found)
- `500` - Server Error

## 🚦 Development Workflow
1. Always start with user registration to get a `sha1_id`
2. Use the `sha1_id` for all subsequent API calls
3. Check the `/attendance/{sha1_id}` endpoint to verify attendance recording

## 📞 Support
For API issues or questions, contact the backend team.

---



---

## 🎯 Quick Start Examples

### Flask Application Example:
```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
BASE_URL = "http://localhost:5001/api"

@app.route('/test-backend', methods=['GET'])
def test_backend_apis():
    """Example function showing how to use the backend APIs from another Flask app"""
    
    try:
        # 1. Test connection to backend
        health_response = requests.get(BASE_URL)
        if health_response.status_code != 200:
            return jsonify({"error": "Backend server not available"}), 500
        
        # 2. Register a new student
        register_data = {
            "name": "Rahul Sharma",
            "gender": "Male",
            "dob": "2012-08-15",
            "role": "Student",
            "password": "rahul123"
        }
        
        register_response = requests.post(f"{BASE_URL}/register", json=register_data)
        if register_response.status_code != 201:
            return jsonify({"error": "Registration failed", "details": register_response.json()}), 400
        
        sha1_id = register_response.json()["sha1_id"]
        
        # 3. Mark attendance for the student
        attendance_data = {
            "sha1_id": sha1_id,
            "class": "5B"
        }
        
        attendance_response = requests.post(f"{BASE_URL}/attendance", json=attendance_data)
        if attendance_response.status_code != 200:
            return jsonify({"error": "Attendance marking failed", "details": attendance_response.json()}), 400
        
        # 4. Get attendance records
        attendance_records = requests.get(f"{BASE_URL}/attendance/{sha1_id}").json()
        
        return jsonify({
            "status": "success",
            "student_id": sha1_id,
            "attendance_result": attendance_response.json(),
            "attendance_records": attendance_records
        })
        
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Cannot connect to backend server"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
```

### Simple Flask Integration Example:
```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
BACKEND_URL = "http://localhost:5001/api"

@app.route('/frontend/login', methods=['POST'])
def frontend_login():
    """Frontend login endpoint that connects to our backend"""
    data = request.get_json()
    
    # Forward login request to our backend
    response = requests.post(f"{BACKEND_URL}/login", json=data)
    
    # Return the same response we got from backend
    return jsonify(response.json()), response.status_code

@app.route('/frontend/attendance', methods=['POST'])
def frontend_mark_attendance():
    """Frontend endpoint to mark attendance"""
    data = request.get_json()
    
    # Forward attendance request to our backend
    response = requests.post(f"{BACKEND_URL}/attendance", json=data)
    
    return jsonify(response.json()), response.status_code

@app.route('/frontend/attendance/<sha1_id>', methods=['GET'])
def frontend_get_attendance(sha1_id):
    """Frontend endpoint to get attendance data"""
    response = requests.get(f"{BACKEND_URL}/attendance/{sha1_id}")
    return jsonify(response.json()), response.status_code
```

### Example Usage in Flask Routes:
```python
@app.route('/student/dashboard/<sha1_id>')
def student_dashboard(sha1_id):
    """Example dashboard route that uses our backend APIs"""
    try:
        # Get student attendance data from our backend
        attendance_response = requests.get(f"http://localhost:5001/api/attendance/{sha1_id}")
        attendance_data = attendance_response.json()
        
        if attendance_data["status"] == "success":
            return f"""
            <h1>Student Dashboard</h1>
            <p>Name: {attendance_data['student_info']['name']}</p>
            <p>Class: {attendance_data['student_info']['current_class']}</p>
            <p>Attendance: {attendance_data['attendance_summary']['attendance_percentage']}%</p>
            """
        else:
            return "Error loading attendance data", 500
            
    except requests.exceptions.RequestException:
        return "Backend service unavailable", 503
```

### Testing the Backend from Flask Shell:
```bash
# Start Flask shell
flask shell

# Test the backend APIs
>>> import requests
>>> base_url = "http://localhost:5001/api"

# Test health endpoint
>>> response = requests.get(base_url)
>>> print(response.json())

# Test getting all students
>>> response = requests.get(f"{base_url}/students")
>>> print(response.json())

# Test getting classes
>>> response = requests.get(f"{base_url}/classes")
>>> print(response.json())
```
