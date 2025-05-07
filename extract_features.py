import torch
import pickle
import numpy as np
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("C:/CoolDrinkDetection/backend/model/best.pt")
model.model.eval()  # Set model to evaluation mode

# Dictionary to store embeddings
brand_embeddings = {}

# Function to extract deep features
def extract_features(image):
    with torch.no_grad():
        image = image / 255.0  # Normalize to [0,1]
        image = image.to(next(model.model.parameters()).device)  # Ensure it's on the correct device

        # Forward pass to get feature maps from backbone
        backbone = model.model.model[:10](image)  # Extract features from first 10 layers

        # Perform Global Average Pooling to get a 1D feature vector
        feature_vector = torch.mean(backbone, dim=(2, 3)).cpu().numpy()

    return feature_vector.flatten()

# Generate embeddings for each brand
for brand_id, brand_name in model.names.items():
    dummy_img = torch.randn(1, 3, 640, 640)  # Create a dummy image

    # Extract features
    features = extract_features(dummy_img)

    # Save the feature vector
    brand_embeddings[brand_name.strip().title()] = features

# Save embeddings
with open("C:/CoolDrinkDetection/backend/brand_embeddings.pkl", "wb") as f:
    pickle.dump(brand_embeddings, f)

print("✅ Brand feature embeddings saved successfully!")
