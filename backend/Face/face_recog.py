# recognize_attendance.py
import cv2
import os
import datetime
import numpy as np
import pickle

DATA_DIR = "data"
MODEL_FILE = "lbph_model.yml"
FACE_SIZE = (200, 200)

# Load label map
with open("label_map.pkl", "rb") as f:
    label_map = pickle.load(f)

# ---------------------------
# Recognize Students
# ---------------------------
def recognize_students():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_FILE)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    attendance = set()
    cap = cv2.VideoCapture(0)

    print("Starting recognition. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100,100))

        for (x,y,w,h) in faces:
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, FACE_SIZE)
            label, confidence = recognizer.predict(face_img)
            student_folder = label_map.get(label, "Unknown")
            name = student_folder.split("_")[1] if student_folder != "Unknown" else "Unknown"

            if confidence < 80:
                attendance.add(name)

            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(frame, f"{name} ({int(confidence)})", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        cv2.imshow("Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    print("\n✅ Attendance:")
    for student in attendance:
        print(student, "-", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


# ---------------------------
# Main Menu
# ---------------------------
def main():
    while True:
        print("\n===== Recognition & Attendance =====")
        print("1. Recognize Students / Mark Attendance")
        print("2. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            recognize_students()
        elif choice == "2":
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
