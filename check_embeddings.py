import pickle

with open("C:/CoolDrinkDetection/backend/brand_embeddings.pkl", "rb") as f:
    brand_embeddings = pickle.load(f)

for brand, embedding in brand_embeddings.items():
    print(f"{brand}: {embedding.shape}")  # Should be (512,)
