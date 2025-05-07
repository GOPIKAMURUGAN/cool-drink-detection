import os
import shutil

# Set the dataset path (update with your actual dataset directory)
dataset_path = "C:/CoolDrinkDetection/dataset/train"  # Change this if needed
organized_path = "C:/CoolDrinkDetection/backend/organized"  # Organized output folder

# Ensure the output directory exists
os.makedirs(organized_path, exist_ok=True)

# Define possible image file extensions
possible_extensions = [".jpg", ".png", ".jpeg"]

# Loop through all files in the dataset
for label_file in os.listdir(dataset_path):
    if label_file.endswith(".txt"):  # Only process label files
        label_path = os.path.join(dataset_path, label_file)

        # Read label file and get the first class ID (assuming YOLO format)
        with open(label_path, "r") as f:
            lines = f.readlines()
            if not lines:
                continue  # Skip empty files

            class_id = lines[0].split()[0]  # First value in YOLO label is the class ID

        # Create folder for this brand inside organized_path
        brand_folder = os.path.join(organized_path, f"Brand_{class_id}")
        os.makedirs(brand_folder, exist_ok=True)

        # Find the corresponding image file
        image_path = None
        for ext in possible_extensions:
            temp_path = os.path.join(dataset_path, label_file.replace(".txt", ext))
            if os.path.exists(temp_path):
                image_path = temp_path
                break  # Stop when the first match is found

        if image_path:  # Ensure the image exists
            # Move image and label to the brand folder
            shutil.move(image_path, os.path.join(brand_folder, os.path.basename(image_path)))
            shutil.move(label_path, os.path.join(brand_folder, os.path.basename(label_path)))
            print(f"Moved {image_path} and {label_path} to {brand_folder}")

print("✅ Image organization completed!")
