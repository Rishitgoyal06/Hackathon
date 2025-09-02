import cv2
import face_recognition
import pickle
import os
import sqlite3
import numpy as np

# Step 1: Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Step 2: Go up one folder (to Backend)
PARENT_DIR = os.path.dirname(BASE_DIR)

# Step 3: Point to Database/school_portal.db
db_path = os.path.join(PARENT_DIR, "Database", "school_portal.db")

print("Using database path:", db_path)

# Importing student images
folderPath = os.path.join(BASE_DIR, "Images")
pathList = os.listdir(folderPath)
print("Images found:", pathList)

imgList = []
studentIds = []

# Load images and extract student IDs
for path in pathList:
    img = cv2.imread(os.path.join(folderPath, path))
    if img is not None:
        imgList.append(img)
        # Use filename without extension as student ID
        studentIds.append(os.path.splitext(path)[0])
    else:
        print(f"Image {path} could not be loaded.")

print("Student IDs:", studentIds)


# Function to find encodings
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Find face locations
        faceLoc = face_recognition.face_locations(img_rgb)

        if len(faceLoc) == 0:
            print("No faces found in this image.")
            continue

        encode = face_recognition.face_encodings(img_rgb, faceLoc)

        if len(encode) > 0:
            encodeList.append(encode[0])
        else:
            print("No face encoding found for this image.")

    return encodeList


print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)

if len(encodeListKnown) == 0:
    print("No valid encodings found. Exiting...")
else:
    print("Encoding Complete")

    # Save encodings to a file (backup)
    with open("EncodeFile.p", 'wb') as file:
        pickle.dump([encodeListKnown, studentIds], file)
    print("File Saved (EncodeFile.p)")

    # Save encodings to DB
    def save_encoding_to_db(student_id, encoding):
        """Save face encoding for a student into DB"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Convert numpy array → bytes
        encoding_bytes = encoding.astype(np.float64).tobytes()

        cursor.execute("INSERT OR REPLACE INTO face_encodings (id, encoding) VALUES (?, ?)",
                       (student_id, encoding_bytes))

        conn.commit()
        conn.close()

    # Loop over each student and save encoding
    for student_id, encoding in zip(studentIds, encodeListKnown):
        save_encoding_to_db(student_id, encoding)
        print(f"Saved encoding for {student_id} to DB")