import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, models, transforms
from torch.utils.data import DataLoader
import os
import numpy as np
from PIL import Image

# --- Config ---
TEMPLATE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
MODEL_SAVE_PATH = "./resnet_template.pth"
EMBEDDINGS_SAVE_PATH = "./template_embeddings.npy"
BATCH_SIZE = 16
NUM_EPOCHS = 5
LEARNING_RATE = 1e-4
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- Data transforms ---
data_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# --- Custom dataset for one-class (no subfolders needed) ---
class OneClassImageDataset(torch.utils.data.Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.images = [os.path.join(root_dir, f) for f in os.listdir(root_dir)
                       if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image_path = self.images[idx]
        image = Image.open(image_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        label = 1  # All are genuine
        return image, label

# --- Dataset and Dataloader ---
dataset = OneClassImageDataset(TEMPLATE_DIR, transform=data_transforms)
data_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

# --- Model Setup ---
model = models.resnet50(pretrained=True)
num_ftrs = model.fc.in_features
model.fc = nn.Linear(num_ftrs, 1)  # One output for binary classification
model = model.to(DEVICE)

criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# --- Training Loop ---
for epoch in range(NUM_EPOCHS):
    model.train()
    running_loss = 0.0
    for inputs, _ in data_loader:
        labels = torch.ones(inputs.size(0), 1).to(DEVICE)  # All labels = 1
        inputs = inputs.to(DEVICE)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * inputs.size(0)

    epoch_loss = running_loss / len(data_loader.dataset)
    print(f"Epoch {epoch+1}/{NUM_EPOCHS} - Loss: {epoch_loss:.4f}")

# --- Save Trained Model ---
torch.save(model.state_dict(), MODEL_SAVE_PATH)
print(f"\nModel saved to {MODEL_SAVE_PATH}")

# --- Embedding Extraction ---
model.eval()
embeddings = []

with torch.no_grad():
    for inputs, _ in data_loader:
        inputs = inputs.to(DEVICE)
        x = model.conv1(inputs)
        x = model.bn1(x)
        x = model.relu(x)
        x = model.maxpool(x)
        x = model.layer1(x)
        x = model.layer2(x)
        x = model.layer3(x)
        x = model.layer4(x)
        x = model.avgpool(x)
        emb = torch.flatten(x, 1).cpu().numpy()
        embeddings.extend(emb)

embeddings = np.array(embeddings)
np.save(EMBEDDINGS_SAVE_PATH, embeddings)
print(f" Saved {len(embeddings)} template embeddings to {EMBEDDINGS_SAVE_PATH}")
