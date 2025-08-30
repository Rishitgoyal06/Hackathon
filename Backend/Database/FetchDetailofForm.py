import hashlib
import sys
import json
import sqlite3
import cv2
import os

DB_PATH = "Backend/Database/school_portal.db"

def generate_unique_id(data):
    # Combine student data into a single string
    combined = f"{data['name']}{data['rollno']}{data['dob']}{data['class']}{data['gender']}{data['phone']}"
    # Generate SHA1 hash
    sha1_hash = hashlib.sha1(combined.encode()).hexdigest()
    # Convert hash to an integer and take the first 10 digits
    unique_id = str(int(sha1_hash, 16))[:10]
    return unique_id

def capture_student_photo(unique_id):
    # Path to save image
    images_dir = os.path.join("Backend", "FaceRecognition", "Images")
    os.makedirs(images_dir, exist_ok=True)
    image_path = os.path.join(images_dir, f"{unique_id}.jpg")

    cap = cv2.VideoCapture(0)
    print("📸 Camera started... Press 'c' to capture photo or 'q' to quit without saving.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to access camera.")
            break

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

def save_student(data):
    print("New Student Data Received:")
    print(f"Name: {data['name']}")
    print(f"Roll No: {data['rollno']}")
    print(f"DOB: {data['dob']}")
    print(f"Class: {data['class']}")
    print(f"Gender: {data['gender']}")
    print(f"Phone: {data['phone']}")

    unique_id = generate_unique_id(data)
    print("Generated Unique ID:", unique_id)

    # Save to database
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO Students (UniqueShaID, Name, RollNumber, DOB, Class, Gender, Phone)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        unique_id,
        data['name'],
        data['rollno'],
        data['dob'],
        data['class'],
        data['gender'],
        data['phone']
    ))

    connection.commit()
    connection.close()
    print("✅ Student saved successfully!")

    # Capture photo after saving student
    capture_student_photo(unique_id)

if __name__ == "__main__":
    raw_data = sys.argv[1]  # JSON string from Flask
    student_data = json.loads(raw_data)
    save_student(student_data)