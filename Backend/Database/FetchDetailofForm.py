import hashlib
import sys
import json
import sqlite3
import cv2
import os

DB_PATH = "Backend/Database/school_portal.db"

def generate_unique_id(data):
    """Generate unique SHA1-based ID for each student."""
    combined = f"{data['name']}{data['rollno']}{data['dob']}{data['class']}{data['gender']}{data['phone']}"
    sha1_hash = hashlib.sha1(combined.encode()).hexdigest()
    unique_id = str(int(sha1_hash, 16))[:10]
    return unique_id


def capture_student_photo(unique_id):
    """Capture and save student photo."""
    images_dir = os.path.join("Backend", "FaceRecognition", "Images")
    os.makedirs(images_dir, exist_ok=True)
    image_path = os.path.join(images_dir, f"{unique_id}.jpg")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Failed to access camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame from camera.")
            break

        # Overlay instructions on the video feed
        cv2.putText(frame, "Press 'C' to Capture or 'Q' to Quit",
                    (20, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow("Capture Student Photo", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('c'):
            cv2.imwrite(image_path, frame)
            print(f"✅ Photo saved as {image_path}")
            break
        elif key == ord('q'):
            print("❌ Capture cancelled.")
            break

    cap.release()
    cv2.destroyAllWindows()

def save_teacher(data):
    """
    Save teacher details in ClassTeachers table.
    Password will be DOB without dashes.
    TeacherID generated using SHA1 hash method.
    """
    print("📥 New Teacher Data Received:")
    print(f"Name: {data['name']}")
    print(f"DOB: {data['dob']}")
    print(f"Class: {data['class']}")
    print(f"Gender: {data['gender']}")
    print(f"Email: {data['email']}")
    print(f"Phone: {data['phone']}")

    # Generate SHA1-based unique ID for Teacher
    combined = f"{data['name']}{data['dob']}{data['class']}{data['gender']}{data['email']}{data['phone']}"
    sha1_hash = hashlib.sha1(combined.encode()).hexdigest()
    teacher_id = int(sha1_hash, 16) % (10**10)  # 10-digit numeric ID

    # Password is DOB without dashes
    password = data['dob'].replace("-", "")

    # Save to database
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute('''
            INSERT INTO ClassTeachers (TeacherID, Name, DOB, Class, Gender, Email, Phone, Password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            teacher_id,
            data['name'],
            data['dob'],
            data['class'],
            data['gender'],
            data['email'],
            data['phone'],
            password
        ))
        connection.commit()
        print(f"✅ Teacher saved successfully! TeacherID: {teacher_id}, Password: {password}")

    except sqlite3.IntegrityError as e:
        print(f"❌ Database Error: {e}")
    finally:
        connection.close()

def save_student(data):
    """Save student details in DB with Teacher foreign key."""
    print("📥 New Student Data Received:")
    print(f"Name: {data['name']}")
    print(f"Roll No: {data['rollno']}")
    print(f"DOB: {data['dob']}")
    print(f"Class: {data['class']}")
    print(f"Gender: {data['gender']}")
    print(f"Phone: {data['phone']}")

    unique_id = generate_unique_id(data)
    print("Generated Unique ID:", unique_id)

    password = data['dob'].replace("-", "")
    # Save to database
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # ✅ Fetch TeacherID from teachers table by matching class
    cursor.execute("SELECT TeacherID, Name FROM ClassTeachers WHERE Class = ?", (data['class'],))
    teacher = cursor.fetchone()
    teacher_id, teacher_name = (teacher if teacher else (None, None))
    try:
        cursor.execute('''
            INSERT INTO Students (StudentID, Name, RollNumber, DOB, Class, Gender, Phone, Teacher, TeacherID, Password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            unique_id,
            data['name'],
            data['rollno'],
            data['dob'],
            data['class'],
            data['gender'],
            data['phone'],
            teacher_name,
            teacher_id,
            password
        ))

        connection.commit()
        print("✅ Student saved successfully!")

    except sqlite3.IntegrityError as e:
        print(f"❌ Database Error: {e}")
    finally:
        connection.close()

    # Capture photo after saving student
    capture_student_photo(unique_id)


if __name__ == "__main__":
    raw_data = sys.argv[1]  # JSON string from Flask
    data = json.loads(raw_data)

    # Detect if data is for teacher or student
    if "rollno" in data:  # Student data
        save_student(data)
    elif "email" in data:  # Teacher data
        save_teacher(data)
    else:
        print("❌ Unknown data type, cannot save.")