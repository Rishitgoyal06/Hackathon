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

Absolutely! Here's a practical example of how your frontend teammates can integrate with your backend APIs:

---

## 🎯 Frontend Integration Example

### HTML Registration Form (register.html)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Student Registration</title>
    <style>
        .container { max-width: 500px; margin: 50px auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input, select { width: 100%; padding: 8px; border: 1px solid #ccc; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; }
        .success { color: green; margin-top: 10px; }
        .error { color: red; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Student Registration</h2>
        <form id="registrationForm">
            <div class="form-group">
                <label>Full Name:</label>
                <input type="text" id="name" required>
            </div>
            <div class="form-group">
                <label>Gender:</label>
                <select id="gender" required>
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                </select>
            </div>
            <div class="form-group">
                <label>Date of Birth:</label>
                <input type="date" id="dob" required>
            </div>
            <div class="form-group">
                <label>Class:</label>
                <input type="text" id="class" placeholder="e.g., 5B" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" id="password" required>
            </div>
            <button type="submit">Register</button>
        </form>
        
        <div id="result" class="success" style="display: none;"></div>
    </div>

    <script>
        document.getElementById('registrationForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = {
                name: document.getElementById('name').value,
                gender: document.getElementById('gender').value,
                dob: document.getElementById('dob').value,
                role: 'Student', // Fixed role for students
                password: document.getElementById('password').value
            };
            
            try {
                // Call YOUR backend API
                const response = await fetch('http://localhost:5001/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    // Show success message with Student ID
                    document.getElementById('result').innerHTML = `
                        <h3>Registration Successful!</h3>
                        <p><strong>Student Name:</strong> ${formData.name}</p>
                        <p><strong>Student ID:</strong> ${result.sha1_id}</p>
                        <p><strong>Class:</strong> ${document.getElementById('class').value}</p>
                        <p style="color: red;">Please save this Student ID for login!</p>
                    `;
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').className = 'success';
                    
                    // Clear form
                    document.getElementById('registrationForm').reset();
                    
                } else {
                    // Show error
                    document.getElementById('result').textContent = 'Error: ' + result.message;
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').className = 'error';
                }
                
            } catch (error) {
                document.getElementById('result').textContent = 'Network error: ' + error.message;
                document.getElementById('result').style.display = 'block';
                document.getElementById('result').className = 'error';
            }
        });
    </script>
</body>
</html>
```

### HTML Login Form (login.html)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Student Login</title>
    <style>/* Same styles as above */</style>
</head>
<body>
    <div class="container">
        <h2>Student Login</h2>
        <form id="loginForm">
            <div class="form-group">
                <label>Student ID:</label>
                <input type="text" id="sha1_id" placeholder="Your 10-digit Student ID" required>
            </div>
            <div class="form-group">
                <label>Password:</label>
                <input type="password" id="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
        
        <div id="result" style="display: none;"></div>
        <div id="attendanceData" style="display: none; margin-top: 20px;"></div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const loginData = {
                sha1_id: document.getElementById('sha1_id').value,
                password: document.getElementById('password').value
            };
            
            try {
                // Call YOUR login API
                const response = await fetch('http://localhost:5001/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(loginData)
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    // Show welcome message
                    document.getElementById('result').innerHTML = `
                        <h3>Welcome, ${result.user.name}!</h3>
                        <p>Role: ${result.user.role}</p>
                    `;
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').className = 'success';
                    
                    // Now fetch attendance data
                    await showAttendanceData(result.user.sha1_id);
                    
                } else {
                    document.getElementById('result').textContent = 'Login failed: ' + result.message;
                    document.getElementById('result').style.display = 'block';
                    document.getElementById('result').className = 'error';
                }
                
            } catch (error) {
                document.getElementById('result').textContent = 'Network error: ' + error.message;
                document.getElementById('result').style.display = 'block';
                document.getElementById('result').className = 'error';
            }
        });
        
        async function showAttendanceData(sha1_id) {
            try {
                // Call YOUR attendance API
                const response = await fetch(`http://localhost:5001/api/attendance/${sha1_id}`);
                const attendance = await response.json();
                
                if (attendance.status === 'success') {
                    document.getElementById('attendanceData').innerHTML = `
                        <h3>Attendance Summary</h3>
                        <p><strong>Total Classes:</strong> ${attendance.attendance_summary.total_classes_held}</p>
                        <p><strong>Classes Attended:</strong> ${attendance.attendance_summary.classes_attended}</p>
                        <p><strong>Attendance Percentage:</strong> ${attendance.attendance_summary.attendance_percentage}%</p>
                    `;
                    document.getElementById('attendanceData').style.display = 'block';
                }
            } catch (error) {
                console.error('Error fetching attendance:', error);
            }
        }
    </script>
</body>
</html>
```

### How Your Teammates Will Use Your APIs:

1. **Registration Flow:**
   - User fills form → Frontend calls `POST /api/register`
   - Your backend returns `sha1_id` → Frontend displays it to user
   - User saves this ID for future logins

2. **Login Flow:**
   - User enters `sha1_id` and password → Frontend calls `POST /api/login`
   - Your backend validates → Returns user data
   - Frontend then calls `GET /api/attendance/{sha1_id}` to show attendance

3. **Attendance Display:**
   - Frontend receives attendance data from your API
   - Displays it in a user-friendly format

### Key Points for Frontend Team:
- **Base URL:** `http://localhost:5001/api`
- **Required Headers:** `Content-Type: application/json`
- **Error Handling:** Always check `response.status` and `response.json().status`
- **Data Flow:** Register → Get `sha1_id` → Use `sha1_id` for all future requests
