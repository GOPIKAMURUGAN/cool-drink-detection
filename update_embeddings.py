import torch
import torchvision.models as models
import torchvision.transforms as transforms
import pickle
import numpy as np
import cv2
import os

# Path to dataset (Update if needed)
dataset_path = "C:/CoolDrinkDetection/backend/model/best.pt"

# Path to save embeddings
embedding_file = "C:/CoolDrinkDetection/backend/brand_embeddings.pkl"

# Load MobileNetV2 for feature extraction
mobilenet = models.mobilenet_v2(pretrained=True)
mobilenet = torch.nn.Sequential(*list(mobilenet.children())[:-1])  # Remove classification layer
mobilenet.eval()

# Image preprocessing function
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def compute_embedding(image):
    """Compute a feature embedding using MobileNetV2."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_transformed = transform(image_rgb).unsqueeze(0)

    with torch.no_grad():
        feature_map = mobilenet(image_transformed)
        feature_vector = feature_map.view(-1).numpy()

    return feature_vector / (np.linalg.norm(feature_vector) + 1e-10)

# Dictionary to store embeddings
brand_embeddings = {}

# Process each brand
for brand in os.listdir(dataset_path):
    brand_folder = os.path.join(dataset_path, brand)
    
    if os.path.isdir(brand_folder):
        print(f"Processing brand: {brand}")
        
        embeddings = []
        
        for img_name in os.listdir(brand_folder):
            img_path = os.path.join(brand_folder, img_name)
            
            try:
                image = cv2.imread(img_path)
                
                if image is not None:
                    embedding = compute_embedding(image)
                    embeddings.append(embedding)
                    
            except Exception as e:
                print(f"Skipping {img_name}: {e}")

        if embeddings:
            brand_embeddings[brand] = np.mean(embeddings, axis=0)  # Average embedding

# Save embeddings
with open(embedding_file, "wb") as f:
    pickle.dump(brand_embeddings, f)

print(f"✅ Brand embeddings updated and saved to {embedding_file}")
