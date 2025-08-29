import os
import pickle
import numpy as np
import cv2
import dlib
from scipy.spatial import distance as dist
import face_recognition
from collections import deque
import sqlite3

# Step 1: Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Step 2: Go up one folder (to Backend)
PARENT_DIR = os.path.dirname(BASE_DIR)

# Step 3: Point to Database/school_portal.db
db_path = os.path.join(PARENT_DIR, "Database", "school_portal.db")

print("Using database path:", db_path)


from datetime import datetime
import sqlite3

def mark_attendance(student_id):
    """Mark attendance: update if exists, insert if not, increment days_present once per day."""
    try:
        print("Marking attendance...")
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Get current date
        today = datetime.now().date()

        # Check if student exists
        cursor.execute("SELECT days_present, date_time FROM attendance WHERE id = ?", (student_id,))
        row = cursor.fetchone()

        if row:
            last_date_time = row[1]
            last_date = datetime.fromisoformat(last_date_time).date() if last_date_time else None

            # Increment days_present only if last attendance is not today
            if last_date != today:
                cursor.execute("""
                    UPDATE attendance
                    SET status = 'present',
                        days_present = days_present + 1,
                        date_time = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), student_id))
        else:
            # Insert new student
            cursor.execute("""
                INSERT INTO attendance (id, status, days_present, date_time)
                VALUES (?, 'present', 1, ?)
            """, (student_id, datetime.now().isoformat()))

        connection.commit()
        print(f"Attendance marked/updated for ID: {student_id}")

    except Exception as e:
        print(f"Error updating attendance: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()

def get_student_details(student_id):
    """Fetch student id and name from users table."""
    try:
        print("In the get")
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        cursor.execute("SELECT id, name FROM users WHERE id = ?", (student_id,))
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

# Constants
EAR_THRESHOLD = 0.26  # Lowered for more sensitivity
CONSEC_FRAMES = 1  # Reduced for faster detection
FRAME_BUFFER_SIZE = 4
MIN_EAR_CHANGE = 0.08  # Adjusted for quicker detection
STABILITY_THRESHOLD = 20  # Further relaxed for less stability checks
LEFT_EYE_IDX = range(42, 48)
RIGHT_EYE_IDX = range(36, 42)


def load_encodings(file_name):
    # Get directory of this script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, file_name)

    with open(file_path, 'rb') as file:
        encode_list_known, student_ids = pickle.load(file)
    return encode_list_known, student_ids

def calculate_EAR(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

def initialize_dlib():
    detector = dlib.get_frontal_face_detector()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    predictor_path = os.path.join(BASE_DIR, "shape_predictor_68_face_landmarks.dat")

    predictor = dlib.shape_predictor(predictor_path)

    return detector, predictor

def initialize_camera(width=640, height=480):
    cap = cv2.VideoCapture(0)
    cap.set(3, width)
    cap.set(4, height)
    return cap

def is_face_stable(face, face_position_buffer):
    """Check if the face bounding box is stable across frames."""
    x, y, w, h = face.left(), face.top(), face.width(), face.height()
    face_position_buffer.append((x, y, w, h))
    if len(face_position_buffer) < FRAME_BUFFER_SIZE:
        return True  # Not enough data yet

    # Calculate movement
    deltas = [np.linalg.norm(np.array(face_position_buffer[i]) - np.array(face_position_buffer[i - 1]))
              for i in range(1, len(face_position_buffer))]
    return max(deltas) < STABILITY_THRESHOLD

def enhanced_blink_detection(avg_ear, blink_counter, consecutive_blinks, ear_buffer):
    """Enhanced blink detection with stability checks."""
    ear_buffer.append(avg_ear)
    if len(ear_buffer) < FRAME_BUFFER_SIZE:
        return blink_counter, consecutive_blinks  # Not enough data yet

    # Check EAR change
    ear_drop = ear_buffer[-1] < EAR_THRESHOLD and (ear_buffer[0] - ear_buffer[-1]) > MIN_EAR_CHANGE
    if ear_drop:
        blink_counter += 1
    else:
        if blink_counter >= CONSEC_FRAMES:
            consecutive_blinks += 1
            print(f"Blink {consecutive_blinks} confirmed!")
        blink_counter = 0

    return blink_counter, consecutive_blinks

def process_face_recognition(frame, face, encode_list_known, student_ids):
    face_img = frame[max(0, face.top()):min(face.bottom(), frame.shape[0]),
               max(0, face.left()):min(face.right(), frame.shape[1])]
    face_img_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    encode_cur_frame = face_recognition.face_encodings(face_img_rgb)

    if encode_cur_frame:
        encode_face = encode_cur_frame[0]
        matches = face_recognition.compare_faces(encode_list_known, encode_face)
        face_dis = face_recognition.face_distance(encode_list_known, encode_face)
        match_index = np.argmin(face_dis)

        if matches[match_index]:
            student_id = student_ids[match_index]
            student = get_student_details(student_id)
            if student:
                print(f"Liveness confirmed: {student['id']} - {student['name']}")
                return student
    return None

def run_face_attendance():
    encode_list_known, student_ids = load_encodings('EncodeFile.p')
    detector, predictor = initialize_dlib()
    cap = initialize_camera()

    blink_counter = 0
    consecutive_blinks = 0
    process_live_face = False
    ear_buffer = deque(maxlen=FRAME_BUFFER_SIZE)
    face_position_buffer = deque(maxlen=FRAME_BUFFER_SIZE)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Camera not capturing frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            # Ensure face is stable
            if not is_face_stable(face, face_position_buffer):
                continue

            landmarks = predictor(gray, face)
            landmarks_points = np.array([[p.x, p.y] for p in landmarks.parts()])

            left_eye = landmarks_points[LEFT_EYE_IDX]
            right_eye = landmarks_points[RIGHT_EYE_IDX]

            left_ear = calculate_EAR(left_eye)
            right_ear = calculate_EAR(right_eye)
            avg_ear = (left_ear + right_ear) / 2.0

            blink_counter, consecutive_blinks = enhanced_blink_detection(avg_ear, blink_counter, consecutive_blinks,
                                                                         ear_buffer)

            if consecutive_blinks == 2:
                process_live_face = True

            if process_live_face:
                student = process_face_recognition(frame, face, encode_list_known, student_ids)
                if student:
                    cv2.putText(frame, f"{student['name']} ({student['id']})", (50, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    mark_attendance(student['id'])
                    consecutive_blinks = 0
                    process_live_face = False

        cv2.imshow("Live Face Detection", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_face_attendance()