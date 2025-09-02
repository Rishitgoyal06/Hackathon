import sqlite3

def create_db():
    conn = sqlite3.connect("school_portal.db")
    cursor = conn.cursor()

    # Students table
    cursor.execute('''
        CREATE TABLE Students (
            StudentID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            RollNumber INTEGER NOT NULL,
            DOB TEXT,
            Class TEXT NOT NULL,
            Gender TEXT NOT NULL,
            Phone INTEGER,
            Teacher TEXT NOT NULL,
            TeacherID INTEGER,
            Password TEXT NOT NULL,
            FOREIGN KEY (TeacherID) REFERENCES ClassTeachers(TeacherID)
        )
    ''')

    # Admin table
    cursor.execute('''
        CREATE TABLE Admin (
            AdminID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            DOB TEXT,
            School TEXT NOT NULL,
            Gender TEXT NOT NULL,
            Email TEXT UNIQUE,
            Phone INTEGER,
            Password TEXT NOT NULL
        )
    ''')

    # ClassTeachers table
    cursor.execute('''
        CREATE TABLE ClassTeachers (
            TeacherID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            DOB TEXT,
            Class TEXT NOT NULL,
            Gender TEXT NOT NULL,
            Email TEXT UNIQUE,
            Phone INTEGER,
            Password TEXT NOT NULL
        )
    ''')

    # Table to track each school day
    cursor.execute('''
        CREATE TABLE SchoolDays (
            DayID INTEGER PRIMARY KEY AUTOINCREMENT,
            Date TEXT UNIQUE NOT NULL   -- e.g. "2025-08-31"
        )
    ''')

    # Attendance table
    cursor.execute('''
        CREATE TABLE Attendance (
            AttendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
            StudentID INTEGER,
            Date TEXT NOT NULL,
            Status TEXT NOT NULL,  -- 'Present' or 'Absent'
            Class TEXT NOT NULL,
            FOREIGN KEY (StudentID) REFERENCES Students(StudentID)
        )
    ''')

    # Face Encodings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_encodings (
            id INTEGER PRIMARY KEY,
            encoding BLOB NOT NULL
        )
    ''')

    # Graph Image table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS graph (
            StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
            Graph BLOB    --Image is stored here           
        )
    ''')

    print("Database created successfully!")

def check_database_status():
    """Check database tables and contents"""
    conn = sqlite3.connect("school_portal.db")
    cursor = conn.cursor()
    
    # Show all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    
    status = {"tables": tables}
    
    # Check graph table
    if 'graph' in tables:
        cursor.execute("SELECT StudentID, length(Graph) as image_size FROM graph")
        graph_data = cursor.fetchall()
        status["graph_entries"] = len(graph_data)
        status["graph_details"] = [(row[0], row[1]) for row in graph_data]
    
    # Check face_encodings table
    if 'face_encodings' in tables:
        cursor.execute("SELECT COUNT(*) FROM face_encodings")
        encoding_count = cursor.fetchone()[0]
        status["face_encodings_count"] = encoding_count
    
    conn.close()
    return status

def show_graph_data():
    """Display graph table contents"""
    conn = sqlite3.connect("school_portal.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT StudentID, length(Graph) as image_size FROM graph")
        rows = cursor.fetchall()
        print(f"Graph table contents ({len(rows)} rows):")
        for row in rows:
            print(f"StudentID: {row[0]}, Image size: {row[1]} bytes")
    except Exception as e:
        print(f"Error reading graph table: {e}")
    
    conn.close()

if __name__ == "__main__":
    create_db()