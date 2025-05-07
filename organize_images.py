import os
import shutil

# Paths
train_path = "C:/CoolDrinkDetection/dataset/train"  # Folder with all images
dest_path = "C:/CoolDrinkDetection/dataset_embeddings"  # Destination folder

# List of brand names (same as YOLO class names)
brands = ["Fanta", "Appy Fizz", "Sprite", "Pepsi", "Frooti", "Coca-Cola", "Mirinda", "Limca", "Sting"]

# Create folders for each brand
for brand in brands:
    os.makedirs(os.path.join(dest_path, brand), exist_ok=True)

# Move images to brand folders
for img_file in os.listdir(train_path):
    img_path = os.path.join(train_path, img_file)

    if os.path.isfile(img_path):  # Ensure it's a file, not a folder
        for brand in brands:
            if brand.lower().replace(" ", "_") in img_file.lower().replace(" ", "_"):  # Check if filename contains brand name
                dst = os.path.join(dest_path, brand, img_file)
                shutil.copy(img_path, dst)  # Copy instead of move
                print(f"✅ Copied {img_file} to {brand}/")
                break  # Stop checking after first match

print("\n✅ Image organization completed successfully!")
