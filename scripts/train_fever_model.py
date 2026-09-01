import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import os
import glob
import sys
from sklearn.model_selection import train_test_split

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import AROGYA AI_DATASET, CNN_MODEL_PTH
from utils.models import FeverCNN

# --- CONFIG ---
DATA_DIR = AROGYA AI_DATASET
BATCH_SIZE = 4
EPOCHS = 30
LR = 0.001

class FeverDataset(Dataset):
    def __init__(self, file_list, labels):
        self.files = file_list
        self.labels = labels

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        try:
            # Load .npy file
            frame = np.load(self.files[idx])
            # Normalize: Thermal values are roughly 20-40C. 
            # Deep learning works best in -1 to 1 or 0 to 1 range.
            frame = (frame - 20) / 25.0 
            frame = torch.FloatTensor(frame).unsqueeze(0) # Add channel dim (1, 24, 32)
            label = torch.tensor(self.labels[idx], dtype=torch.long)
            return frame, label
        except Exception as e:
            print(f"Error loading {self.files[idx]}: {e}")
            return torch.zeros((1, 24, 32)), torch.tensor(0)


def train():
    # Gather Files
    normal_files = glob.glob(os.path.join(DATA_DIR, "Normal", "*.npy"))
    fever_files = glob.glob(os.path.join(DATA_DIR, "Fever", "*.npy"))
    
    if not normal_files or not fever_files:
        print("Missing dataset files. Check SmartASHA_Dataset directory.")
        return

    files = normal_files + fever_files
    labels = [0] * len(normal_files) + [1] * len(fever_files)
    
    # Split
    train_files, val_files, train_labels, val_labels = train_test_split(
        files, labels, test_size=0.2, random_state=42
    )
    
    train_ds = FeverDataset(train_files, train_labels)
    val_ds = FeverDataset(val_files, val_labels)
    
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)

    model = FeverCNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LR)

    print(f"Training on {len(train_ds)} samples, validating on {len(val_ds)} samples...")

    history = []
    for epoch in range(EPOCHS):
        model.train()
        total_loss = 0
        for frames, targets in train_loader:
            optimizer.zero_grad()
            outputs = model(frames)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        # Simple validation
        model.eval()
        correct = 0
        with torch.no_grad():
            for frames, targets in val_loader:
                outputs = model(frames)
                _, predicted = torch.max(outputs, 1)
                correct += (predicted == targets).sum().item()
        
        acc = correct / len(val_ds) if len(val_ds) > 0 else 0
        avg_loss = total_loss / len(train_loader)
        history.append({"Epoch": epoch + 1, "Loss": avg_loss, "Val_Acc": acc})
        
        if (epoch+1) % 5 == 0:
            print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {avg_loss:.4f} | Val Acc: {acc:.2f}")

    # Save the model
    torch.save(model.state_dict(), CNN_MODEL_PTH)
    print(f"\nModel saved as {CNN_MODEL_PTH}")
    
    # Save training history
    import pandas as pd
    history_df = pd.DataFrame(history)
    history_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "visualizations", "training_history.csv")
    os.makedirs(os.path.dirname(history_path), exist_ok=True)
    history_df.to_csv(history_path, index=False)
    print(f"Training history saved to {history_path}")

if __name__ == "__main__":
    train()
