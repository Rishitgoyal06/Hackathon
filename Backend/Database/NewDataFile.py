import sqlite3
import datetime as dt

def create_db():
    conn = sqlite3.connect("school_portal.db")
    cursor = conn.cursor()

    # Create Users table (without AUTOINCREMENT)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT CHECK(role IN ('student','teacher')) NOT NULL,
        class_no TEXT,
        email TEXT UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    # Create Face Encodings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS face_encodings (
        id INTEGER PRIMARY KEY,
        encoding BLOB NOT NULL,
        FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # Create Attendance table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        date DATE,
        status INTEGER CHECK(status IN (0,1)) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, date)
    )
    ''')
    # Simplified Day table - no total_days needed!
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS day (
        date DATE,
        class_no TEXT,
        PRIMARY KEY (date, class_no)
    )
    ''')

    # Example user data
    user_id = 6437648326
    name = "Shyam"
    role = "student"
    class_no = "2B"
    email = "harsh11@email.com"
    password = "54321"

    # Example attendance date
    cdate = dt.date.today().isoformat()

    try:
        cursor.execute('''
            INSERT INTO users (id, name, role, class_no, email, password)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, name, role, class_no, email, password))
        conn.commit()
    except sqlite3.IntegrityError:
        print("User already exists!")

    # --- Simplified Lecture logic ---
    try:
        cursor.execute('''
            INSERT INTO day (date, class_no)
            VALUES (?, ?)
        ''', (cdate, class_no))
        conn.commit()
        
        # Calculate total days for this class
        cursor.execute('SELECT COUNT(*) FROM day WHERE class_no = ?', (class_no,))
        total_days = cursor.fetchone()[0]
        
        print(f"Lecture recorded for {class_no} on {cdate}")
        print(f"Total lectures for {class_no}: {total_days}")
        
    except sqlite3.IntegrityError:
        print(f"Lecture already exists for {class_no} on {cdate}")

    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    create_db()
