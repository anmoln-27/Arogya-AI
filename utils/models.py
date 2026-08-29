import torch
import torch.nn as nn

class FeverCNN(nn.Module):
    def __init__(self):
        super(FeverCNN, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2), # Output: 8 x 12 x 16
            nn.Conv2d(8, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2) # Output: 16 x 6 x 8
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(16 * 6 * 8, 32),
            nn.ReLU(),
            nn.Linear(32, 2)
        )

    def forward(self, x):
        x = self.conv(x)
        x = self.fc(x)
        return x

def get_model():
    return FeverCNN()
