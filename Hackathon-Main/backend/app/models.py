# app/models.py

# This is a multi-line string containing all SQL commands to set up the database.
SQL_SCHEMA = """
-- Users table (common for Admin, Teacher, Student)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sha1_id TEXT UNIQUE,                  -- Changed: Removed NOT NULL constraint
    name TEXT NOT NULL,
    gender TEXT CHECK(gender IN ('Male','Female','Other')) NOT NULL,
    dob DATE NOT NULL,
    role TEXT CHECK(role IN ('Admin','Teacher','Student')) NOT NULL,
    password TEXT NOT NULL
);

-- SIMPLIFIED: Student attendance records (now only stores raw events)
CREATE TABLE IF NOT EXISTS student_attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sha1_id TEXT NOT NULL,                -- Reference to students
    class TEXT NOT NULL,                  -- Class name (e.g., "5B")
    attendance_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Changed field name
    FOREIGN KEY (sha1_id) REFERENCES users(sha1_id)
);

-- Messages table (chat history for all users)
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sha1_id TEXT NOT NULL,                 -- user identifier
    user_message TEXT NOT NULL,            -- message from user
    bot_response TEXT NOT NULL,            -- response from bot
    session_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sha1_id) REFERENCES users(sha1_id)
);

-- Teacher-class mapping (because teacher may or may not have class)
CREATE TABLE IF NOT EXISTS teacher_classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sha1_id TEXT NOT NULL,                 -- must belong to role = 'Teacher'
    class TEXT NOT NULL,
    FOREIGN KEY (sha1_id) REFERENCES users(sha1_id)
);

-- Face Encodings Table
CREATE TABLE IF NOT EXISTS face_encodings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sha1_id TEXT NOT NULL,            -- Reference to users table
    encoding BLOB NOT NULL,           -- Store face encoding as binary (serialized numpy array)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sha1_id) REFERENCES users(sha1_id)
);
"""