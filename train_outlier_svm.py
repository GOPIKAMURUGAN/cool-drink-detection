import cv2
import numpy as np
import pickle
from ultralytics import YOLO
from sklearn.svm import OneClassSVM
import os

# ✅ Load YOLOv8 Model
model = YOLO("C:/CoolDrinkDetection/backend/model/best.pt")

def extract_features(image_path):
    """Extracts YOLO feature embeddings from an image."""
    image = cv2.imread(image_path)

    if image is None:
        print(f"❌ Error: Could not read image - {image_path}")
        return None

    results = model(image, save=False, verbose=False)

    # ✅ Debugging: Print detected objects
    if results and len(results[0].boxes) > 0:
        print(f"✅ Detected {len(results[0].boxes)} objects in {image_path}")
        return results[0].boxes.xywhn.cpu().numpy().flatten()
   
    print(f"⚠️ Warning: No objects detected in {image_path}")
    return None

# ✅ Paths for all dataset image folders
dataset_folders = [
    "C:/CoolDrinkDetection/dataset/train/images",
    "C:/CoolDrinkDetection/dataset/test/images",
    "C:/CoolDrinkDetection/dataset/valid/images"
]

# Collect feature embeddings
features = []
feature_size = None  # Stores the expected size of each feature vector

# Supported image formats
valid_extensions = (".jpg", ".jpeg", ".png", ".bmp")

for folder in dataset_folders:
    if not os.path.exists(folder):
        print(f"⚠️ Warning: Folder not found - {folder}")
        continue
   
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)

        if not os.path.isfile(img_path) or not filename.lower().endswith(valid_extensions):
            continue  # Skip non-image files

        feature = extract_features(img_path)

        if feature is not None:
            if feature_size is None:
                feature_size = len(feature)  # Set the expected feature size

            if len(feature) == feature_size:  # Ensure all feature vectors have the same size
                features.append(feature)
            else:
                print(f"⚠️ Skipping {filename}: Feature size mismatch ({len(feature)} instead of {feature_size})")

# ✅ Convert features to NumPy array
if len(features) == 0:
    print("❌ Error: No valid features extracted. Check your dataset and YOLO model.")
    exit()

features = np.array(features, dtype=np.float32)

# ✅ Ensure features array is 2D
if len(features.shape) == 1:
    features = features.reshape(1, -1)  # Convert to 2D array if it's 1D
elif len(features.shape) > 2:
    features = features.reshape(features.shape[0], -1)  # Flatten if more than 2D

# ✅ Train One-Class SVM (Detects Outliers)
svm = OneClassSVM(kernel='rbf', gamma='auto').fit(features)

# ✅ Save trained SVM model
with open("C:/CoolDrinkDetection/backend/outlier_detector.pkl", "wb") as f:
    pickle.dump(svm, f)

print("✅ Outlier detection model trained and saved!")