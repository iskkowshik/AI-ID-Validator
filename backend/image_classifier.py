import base64
import io
from PIL import Image
import torch
from torchvision import transforms, models
import pytesseract
import re

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Define the image transform (same as training)
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# Load the model once, outside of predict function
def load_model(path='id_resnet_model.pth'):
    model = models.resnet18(pretrained=False)
    model.fc = torch.nn.Linear(model.fc.in_features, 3)  # 3 classes

    # Debug: Print sample weights before loading
    print("Before loading weights:", model.fc.weight[0][:5])

    # Load the trained weights
    state_dict = torch.load(path, map_location=device)
    model.load_state_dict(state_dict)

    # Debug: Print sample weights after loading
    print("After loading weights:", model.fc.weight[0][:5])

    model.to(device)
    model.eval()
    return model

# Load model (do this once)
model = load_model('id_resnet_model.pth')


def correct_orientation(image: Image.Image):
    osd = pytesseract.image_to_osd(image)
    rotation = int(re.search(r'Rotate: (\d+)', osd).group(1))

    if rotation != 0:
        image = image.rotate(-rotation, expand=True)

    return image

# Predict from base64 encoded image string
def predict_from_base64(image_base64: str):
    image_data = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_data)).convert('RGB')

    # Correct the image orientation before preprocessing
    image = correct_orientation(image)

    img_t = transform(image).unsqueeze(0).to(device)  # Add batch dim

    with torch.no_grad():
        outputs = model(img_t)  # raw logits
        probabilities = torch.nn.functional.softmax(outputs, dim=1)

    class_names = ['fake', 'genuine', 'non-id']  # updated here
    genuine_index = class_names.index('genuine')

    genuine_confidence = probabilities[0][1].item()

    return {
        "genuine_confidence": genuine_confidence,
        "all_probabilities": {
            class_names[i]: round(prob.item(), 4) for i, prob in enumerate(probabilities[0])
        }
    }
