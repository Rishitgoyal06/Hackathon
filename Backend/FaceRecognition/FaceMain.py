import os
import pickle
import numpy as np
import cv2
import dlib
import face_recognition
from collections import deque
import sqlite3
from datetime import datetime, date
from scipy.spatial import distance as dist

# Step 1: Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Step 2: Go up one folder (to Backend)
PARENT_DIR = os.path.dirname(BASE_DIR)

# Step 3: Point to Database/school_portal.db
db_path = os.path.join(PARENT_DIR, "Database", "school_portal.db")

print("Using database path:", db_path)


# Performance optimization: Precompute constants
LEFT_EYE_IDX = list(range(36, 42))  # Convert to list for faster access
RIGHT_EYE_IDX = list(range(42, 48))

def mark_school_day():
    """Ensure today's date exists in SchoolDays (means school is open)."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    today = str(date.today())

    cursor.execute("SELECT 1 FROM SchoolDays WHERE Date = ?", (today,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO SchoolDays (Date) VALUES (?)", (today,))
        conn.commit()
        print(f"School open day added: {today}")
    conn.close()


def mark_attendance(student_id):
    """Mark student's attendance for today."""
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        today = str(date.today())

        # Fetch student's class
        cursor.execute("""
            SELECT Class FROM Students
            WHERE StudentID = ?
        """, (student_id,))
        result = cursor.fetchone()
        if not result:
            print(f"No student found with ID {student_id}")
            return
        student_class = result[0]

        # Ensure school day is added
        mark_school_day()

        # Check if attendance already exists
        cursor.execute("""
            SELECT 1 FROM Attendance
            WHERE StudentID = ? AND Date = ?
        """, (student_id, today))
        row = cursor.fetchone()

        if row:
            print(f"Attendance already marked for student {student_id} on {today}")
        else:
            # Insert new attendance record
            cursor.execute("""
                INSERT INTO Attendance (StudentID, Date, Status, Class)
                VALUES (?, ?, 'Present', ?)
            """, (student_id, today, student_class))
            connection.commit()
            print(f"Attendance marked for ID: {student_id} on {today}")

    except Exception as e:
        print(f"Error updating attendance: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()

def get_student_details(student_id):
    """Fetch student id and name from users table."""
    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT StudentID, Name FROM Students WHERE StudentID = ?", (student_id,))
        row = cursor.fetchone()
        if row:
            return {"id": row[0], "name": row[1]}
        return None

    except Exception as e:
        print(f"Database Error: {e}")
        return None

    finally:
        if connection:
            cursor.close()
            connection.close()


# Constants (Optimized values)
EAR_THRESHOLD = 0.25  # Slightly lower for better sensitivity
CONSEC_FRAMES = 1
FRAME_BUFFER_SIZE = 3  # Reduced buffer size for faster response
MIN_EAR_CHANGE = 0.07  # Smaller change required
STABILITY_THRESHOLD = 25  # Slightly higher for better stability


def load_encodings_from_db():
    """Load all encodings + IDs from DB"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, encoding FROM face_encodings")
    rows = cursor.fetchall()

    encode_list_known = []
    student_ids = []

    for student_id, encoding_bytes in rows:
        try:
            encoding = np.frombuffer(encoding_bytes, dtype=np.float64)
            if encoding.shape[0] == 128:
                encode_list_known.append(encoding)
                student_ids.append(student_id)
        except:
            try:
                encoding = pickle.loads(encoding_bytes)
                if isinstance(encoding, np.ndarray) and encoding.shape[0] == 128:
                    encode_list_known.append(encoding)
                    student_ids.append(student_id)
            except:
                continue

    conn.close()
    print(f"Loaded {len(encode_list_known)} encodings")
    return encode_list_known, student_ids


def initialize_dlib():
    """Initialize dlib with performance optimizations"""
    detector = dlib.get_frontal_face_detector()
    predictor_path = os.path.join(BASE_DIR, "shape_predictor_68_face_landmarks.dat")

    if not os.path.exists(predictor_path):
        print("Shape predictor file not found!")
        return None, None

    try:
        predictor = dlib.shape_predictor(predictor_path)
        return detector, predictor
    except Exception as e:
        print(f"Error loading shape predictor: {e}")
        return None, None


def calculate_EAR(eye):
    """Optimized EAR calculation"""
    # Precompute distances
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    return (A + B) / (2.0 * C)


def initialize_camera(width=640, height=480):
    """Initialize camera with optimized settings"""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    cap.set(cv2.CAP_PROP_FPS, 30)  # Set to 30 FPS
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size
    return cap


def is_face_stable(face, face_position_buffer):
    """Optimized face stability check"""
    x, y, w, h = face.left(), face.top(), face.width(), face.height()
    face_position_buffer.append((x, y, w, h))

    if len(face_position_buffer) < 2:
        return True

    # Only check last two positions for speed
    current = np.array(face_position_buffer[-1])
    previous = np.array(face_position_buffer[-2])
    movement = np.linalg.norm(current - previous)

    return movement < STABILITY_THRESHOLD


def enhanced_blink_detection(avg_ear, blink_counter, consecutive_blinks, ear_buffer):
    """Optimized blink detection"""
    ear_buffer.append(avg_ear)

    if len(ear_buffer) < 2:
        return blink_counter, consecutive_blinks

    # Check for significant EAR drop
    current_ear = ear_buffer[-1]
    previous_ear = ear_buffer[-2]

    if current_ear < EAR_THRESHOLD and (previous_ear - current_ear) > MIN_EAR_CHANGE:
        blink_counter += 1
    else:
        if blink_counter >= CONSEC_FRAMES:
            consecutive_blinks += 1
            print(f"Blink detected! Total: {consecutive_blinks}")
        blink_counter = 0

    return blink_counter, consecutive_blinks


def process_face_recognition(frame, face, encode_list_known, student_ids):
    """Optimized face recognition"""
    # Extract face region with padding
    padding = 20
    y1 = max(0, face.top() - padding)
    y2 = min(frame.shape[0], face.bottom() + padding)
    x1 = max(0, face.left() - padding)
    x2 = min(frame.shape[1], face.right() + padding)

    face_img = frame[y1:y2, x1:x2]

    if face_img.size == 0:
        return None

    # Resize for faster processing (optional)
    small_face = cv2.resize(face_img, (0, 0), fx=0.5, fy=0.5)
    face_img_rgb = cv2.cvtColor(small_face, cv2.COLOR_BGR2RGB)

    encode_cur_frame = face_recognition.face_encodings(face_img_rgb)

    if encode_cur_frame:
        encode_face = encode_cur_frame[0]
        # Use faster comparison with tolerance
        matches = face_recognition.compare_faces(encode_list_known, encode_face, tolerance=0.5)
        face_dis = face_recognition.face_distance(encode_list_known, encode_face)

        if True in matches:
            match_index = np.argmin(face_dis)
            student_id = student_ids[match_index]
            student = get_student_details(student_id)
            if student:
                print(f"Recognized: {student['name']}")
                return student
    return None


def run_face_attendance():
    """Main function with performance optimizations"""
    with open(os.path.join(BASE_DIR, "EncodingGenerator.py")) as f:
        exec(f.read())
    encode_list_known, student_ids = load_encodings_from_db()
    detector, predictor = initialize_dlib()
    cap = initialize_camera()

    blink_counter = 0
    consecutive_blinks = 0
    process_live_face = False
    ear_buffer = deque(maxlen=FRAME_BUFFER_SIZE)
    face_position_buffer = deque(maxlen=2)  # Smaller buffer for speed
    attendance_marked = False  # Flag to track if attendance was marked

    # Performance monitoring
    frame_count = 0
    start_time = datetime.now()

    print("Starting face attendance system...")
    print("Press ESC to close camera manually")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera error: Unable to read frame from camera")
            print("Please check if camera is connected and not being used by another application")
            break

        # Skip frames for better performance (process every 2nd frame)
        frame_count += 1
        if frame_count % 2 != 0:
            continue

        # Convert to grayscale for faster processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Use dlib with no upsampling for speed (0 instead of 1)
        faces = detector(gray, 0)

        for face in faces:
            if not is_face_stable(face, face_position_buffer):
                continue

            # Get landmarks
            landmarks = predictor(gray, face)
            landmarks_points = np.array([[p.x, p.y] for p in landmarks.parts()])

            left_eye = landmarks_points[LEFT_EYE_IDX]
            right_eye = landmarks_points[RIGHT_EYE_IDX]

            left_ear = calculate_EAR(left_eye)
            right_ear = calculate_EAR(right_eye)
            avg_ear = (left_ear + right_ear) / 2.0

            blink_counter, consecutive_blinks = enhanced_blink_detection(
                avg_ear, blink_counter, consecutive_blinks, ear_buffer
            )

            if consecutive_blinks >= 2:
                process_live_face = True
                consecutive_blinks = 0  # Reset immediately

            if process_live_face:
                student = process_face_recognition(frame, face, encode_list_known, student_ids)
                if student:
                    cv2.putText(frame, f"{student['name']} ({student['id']})", (30, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "Attendance Marked!", (30, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    mark_attendance(student['id'])
                    process_live_face = False
                    attendance_marked = True

        # Display instructions
        cv2.putText(frame, "Blink twice to mark attendance", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, "Press ESC when done with attendance", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Display FPS
        elapsed = (datetime.now() - start_time).total_seconds()
        fps = frame_count / elapsed if elapsed > 0 else 0
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow("Live Face Detection", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

    cap.release()
    cv2.destroyAllWindows()
    
    # Return student data if attendance was marked, None otherwise
    if attendance_marked:
        return student if 'student' in locals() else None
    return None


if __name__ == "__main__":
    run_face_attendance()