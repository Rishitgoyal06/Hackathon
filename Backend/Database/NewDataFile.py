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

    # Example user data
    user_id = "1234567890"
    name = "Vaibhav"
    role = "student"
    email = "vaibhav@email.com"
    password = "12345"

    cursor.execute('''
        INSERT INTO users (id, name, role, email, password)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, name, role, email, password))
    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    create_db()
