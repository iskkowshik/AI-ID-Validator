import base64
from io import BytesIO
from PIL import Image
from torchvision import transforms
import torch
import torch.nn as nn
import numpy as np
from torchvision.models import resnet50, ResNet50_Weights
import os

# Configs
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_SAVE_PATH = os.path.join(BASE_DIR, "resnet_template.pth")
EMBEDDINGS_SAVE_PATH = os.path.join(BASE_DIR, "template_embeddings.npy")
BEST_EMB_SAVE_PATH = os.path.join(BASE_DIR, "best_matched_embedding.npy")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Image Transform
data_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

def load_model():
    # ✅ Load pre-trained weights properly
    model = resnet50(weights=ResNet50_Weights.DEFAULT)
    model.fc = nn.Identity()  # Remove final classification layer

    # ✅ Load your saved model weights safely
    state_dict = torch.load(MODEL_SAVE_PATH, map_location=DEVICE, weights_only=True)
    model.load_state_dict(state_dict, strict=False)

    model = model.to(DEVICE)
    model.eval()
    return model

def extract_embedding(model, image_tensor):
    with torch.no_grad():
        emb = model(image_tensor)  # Output: (1, 2048)
    return emb.cpu().numpy()

def is_test_image_in_templates(test_emb, template_embeddings, threshold=1e-6):
    for idx, emb in enumerate(template_embeddings):
        if np.allclose(test_emb, emb, atol=threshold):
            print(f"⚠️ Test image matches template at index {idx}")
            return True
    print("✅ Test image is NOT part of the templates.")
    return False

def cosine_similarity(a, b):
    a_norm = a / np.linalg.norm(a)
    b_norm = b / np.linalg.norm(b)
    return np.dot(a_norm, b_norm)

def validation_score_from_base64(base64_str):
    # Decode and process image
    image_data = base64.b64decode(base64_str)
    img = Image.open(BytesIO(image_data)).convert('RGB')
    img_tensor = data_transforms(img).unsqueeze(0).to(DEVICE)

    # Load model and embeddings
    model = load_model()
    embeddings = np.load(EMBEDDINGS_SAVE_PATH)

    test_emb = extract_embedding(model, img_tensor)[0]  # Shape: (2048,)

    # Check for duplicate embedding
    print(is_test_image_in_templates(test_emb, embeddings))

    # Compare with templates
    sims = [cosine_similarity(test_emb, emb) for emb in embeddings]
    best_idx = int(np.argmax(sims))
    best_score = sims[best_idx]
    best_emb = embeddings[best_idx]

    # Save best match
    np.save(BEST_EMB_SAVE_PATH, best_emb)

    # Print debug info
    print("\n🧪 Test Image Embedding:\n", test_emb)
    print("\n🏆 Best Matched Template Embedding (Index={}):\n".format(best_idx), best_emb)
    print(f"\n✅ Cosine Similarity Score: {best_score:.6f}")

    return best_score
