# register_train.py
import cv2
import os
import numpy as np
import pickle

DATA_DIR = "data"
MODEL_FILE = "lbph_model.yml"
FACE_SIZE = (200, 200)  # resize all faces to 200x200
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------
# Register Student
# ---------------------------
def register_student():
    name = input("Enter student name: ").strip()
    roll = input("Enter roll number (numeric): ").strip()
    student_dir = os.path.join(DATA_DIR, f"{roll}_{name}")
    os.makedirs(student_dir, exist_ok=True)

    # Start count from existing images to avoid overwriting
    existing_images = [f for f in os.listdir(student_dir) if f.endswith(".jpg")]
    count = len(existing_images)

    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    print("Press 'q' to capture an image. Capture at least 5 images per student.")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100,100))

        for (x,y,w,h) in faces:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

        cv2.imshow(f"Register Student: {name}", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            if len(faces) == 0:
                print("No face detected. Try again.")
                continue
            for (x,y,w,h) in faces:
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, FACE_SIZE)
                img_path = os.path.join(student_dir, f"{count}.jpg")
                cv2.imwrite(img_path, face_img)
                print(f"Saved {img_path}")
                count += 1

        if count >= 10:  # stop after 10 images
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ Student {name} registered with {count} images.")


# ---------------------------
# Train Model
# ---------------------------
def train_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    faces = []
    labels = []

    student_folders = sorted(os.listdir(DATA_DIR))  # ensure consistent label order
    label_map = {}  # maps integer label -> student folder name

    for label_id, student in enumerate(student_folders):
        student_dir = os.path.join(DATA_DIR, student)
        label_map[label_id] = student
        for img_file in os.listdir(student_dir):
            img_path = os.path.join(student_dir, img_file)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img.shape != FACE_SIZE:
                img = cv2.resize(img, FACE_SIZE)
            faces.append(img)
            labels.append(label_id)

    labels = np.array(labels)
    recognizer.train(faces, labels)
    recognizer.save(MODEL_FILE)

    # Save label map
    with open("label_map.pkl", "wb") as f:
        pickle.dump(label_map, f)

    print(f"✅ Model trained and saved as {MODEL_FILE}")
    print("✅ Label map saved as label_map.pkl")


# ---------------------------
# Main Menu
# ---------------------------
def main():
    while True:
        print("\n===== Registration & Training =====")
        print("1. Register Student")
        print("2. Train Model")
        print("3. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            register_student()
        elif choice == "2":
            train_model()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
