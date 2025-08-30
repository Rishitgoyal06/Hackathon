import sqlite3

def create_db():
    conn = sqlite3.connect("school_portal.db")
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER,
        name TEXT NOT NULL,
        role TEXT CHECK(role IN ('student','teacher')) NOT NULL,
        email TEXT,
        password TEXT NOT NULL
    )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Students (
            UniqueShaID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            RollNumber INTEGER NOT NULL,
            DOB TEXT,
            Class TEXT NOT NULL,
            Gender TEXT NOT NULL,
            Phone INTEGER
        )
    ''')
    # Create Face Encodings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS face_encodings (
        id INTEGER PRIMARY KEY,
        encoding BLOB NOT NULL
    )
    ''')
    # Create Attendance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY,
            date_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT CHECK(status IN ('present','absent')) NOT NULL,
            days_present INTEGER
        )
    ''')
    print("Database created successfully!")

if __name__ == "__main__":
    create_db()
