import cv2
from ultralytics import YOLO

# Load YOLO Model
model = YOLO("C:/CoolDrinkDetection/backend/model/best.pt")

# Test Image
test_image = r"C:\CoolDrinkDetection\dataset\test\images\frooti-img3_jpg.rf.89f5411a438ee9ca771c5193e026d017.jpg"  # Change to an actual image in your dataset

# Load Image
image = cv2.imread(test_image)
if image is None:
    print(f"❌ Error: Could not read image - {test_image}")
    exit()

# Run YOLO Model
results = model(image, save=True, verbose=True)

# Check results
if results and len(results[0].boxes) > 0:
    print("✅ YOLO successfully detected objects!")
else:
    print("❌ YOLO did not detect anything. Check your model and dataset.")