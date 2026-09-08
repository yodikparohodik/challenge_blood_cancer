"""
SelfLearn - Student models for learning tasks
"""
import os
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from PIL import Image


class Task:
    """Represents a single learning task."""
    
    def __init__(
        self,
        image: Image.Image,
        label: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.image = image
        self.label = label
        self.metadata = metadata or {}


class TaskDataset(Dataset):
    """PyTorch Dataset for tasks."""
    
    def __init__(self, tasks: List[Task], transform=None):
        self.tasks = tasks
        self.transform = transform
    
    def __len__(self):
        return len(self.tasks)
    
    def __getitem__(self, idx):
        task = self.tasks[idx]
        image = np.array(task.image).astype(np.float32)
        
        # Convert to CHW format and normalize
        if len(image.shape) == 2:
            image = np.stack([image] * 3, axis=-1)
        
        image = image.transpose(2, 0, 1) / 255.0
        
        # Normalize with mean and std
        mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
        image_tensor = torch.from_numpy(image)
        image_tensor = (image_tensor - mean) / std
        
        return image_tensor, task.label


class StudentBase(ABC):
    """Abstract base class for student models."""
    
    @abstractmethod
    def train(self, tasks: List[Task], epochs: int, batch_size: int) -> Dict[str, Any]:
        """Train the model on tasks."""
        pass
    
    @abstractmethod
    def predict(self, images: List[Image.Image]) -> List[int]:
        """Predict labels for images."""
        pass
    
    @abstractmethod
    def save(self, path: str) -> None:
        """Save model weights."""
        pass
    
    @abstractmethod
    def load(self, path: str) -> None:
        """Load model weights."""
        pass


class SimpleCNN(nn.Module, StudentBase):
    """Simple CNN model for digit/shape classification."""
    
    def __init__(self, num_classes: int = 10, input_size: int = 64):
        nn.Module.__init__(self)
        StudentBase.__init__(self)
        
        self.num_classes = num_classes
        self.input_size = input_size
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        
        # Pooling
        self.pool = nn.MaxPool2d(2, 2)
        
        # Fully connected layers
        # After two pooling operations: 64 -> 32 -> 16
        fc_input = 64 * 16 * 16
        self.fc1 = nn.Linear(fc_input, 128)
        self.fc2 = nn.Linear(128, num_classes)
        
        # Dropout
        self.dropout = nn.Dropout(0.5)
        
        # Activation
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(-1, 64 * 16 * 16)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.fc2(x)
        return x
    
    def train_model(
        self,
        tasks: List[Task],
        epochs: int = 10,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        device: Optional[str] = None
    ) -> Dict[str, Any]:
        """Train the model."""
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        dataset = TaskDataset(tasks)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        self.to(device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        
        history = {
            'loss': [],
            'accuracy': []
        }
        
        # Set to training mode
        super().train()
        for epoch in range(epochs):
            running_loss = 0.0
            correct = 0
            total = 0
            
            for images, labels in dataloader:
                images = images.to(device)
                labels = labels.to(device)
                
                optimizer.zero_grad()
                outputs = self(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                
                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
            
            avg_loss = running_loss / len(dataloader)
            accuracy = correct / total
            
            history['loss'].append(avg_loss)
            history['accuracy'].append(accuracy)
        
        return history
    
    def train_method(self, tasks: List[Task], epochs: int, batch_size: int) -> Dict[str, Any]:
        """Train the model (renamed to avoid conflict with nn.Module.train)."""
        return self.train_model(tasks, epochs, batch_size)
    
    def predict(
        self,
        images: List[Image.Image],
        device: Optional[str] = None
    ) -> List[int]:
        """Predict labels for images."""
        if device is None:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        self.eval()
        self.to(device)
        
        predictions = []
        
        with torch.no_grad():
            for image in images:
                img_array = np.array(image).astype(np.float32)
                
                if len(img_array.shape) == 2:
                    img_array = np.stack([img_array] * 3, axis=-1)
                
                img_array = img_array.transpose(2, 0, 1) / 255.0
                
                mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
                std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
                img_tensor = torch.from_numpy(img_array).unsqueeze(0).float()
                img_tensor = (img_tensor - mean) / std
                img_tensor = img_tensor.to(device)
                
                outputs = self(img_tensor)
                _, predicted = torch.max(outputs.data, 1)
                predictions.append(predicted.item())
        
        return predictions
    
    def save(self, path: str) -> None:
        """Save model weights."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            'model_state_dict': self.state_dict(),
            'num_classes': self.num_classes,
            'input_size': self.input_size
        }, path)
    
    def load(self, path: str) -> None:
        """Load model weights."""
        checkpoint = torch.load(path, map_location='cpu')
        self.load_state_dict(checkpoint['model_state_dict'])
    
    def eval(self):
        """Set model to evaluation mode."""
        super().eval()
        return self


class MiniCNN(SimpleCNN):
    """Smaller CNN model for faster training."""
    
    def __init__(self, num_classes: int = 10, input_size: int = 64):
        nn.Module.__init__(self)
        StudentBase.__init__(self)
        
        self.num_classes = num_classes
        self.input_size = input_size
        
        # Smaller architecture
        self.conv1 = nn.Conv2d(3, 16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        
        # After pooling: 64 -> 32
        fc_input = 16 * 32 * 32
        self.fc1 = nn.Linear(fc_input, 64)
        self.fc2 = nn.Linear(64, num_classes)
        
        self.relu = nn.ReLU()
    
    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = x.view(-1, 16 * 32 * 32)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def get_model(model_type: str = 'SimpleCNN', num_classes: int = 10, input_size: int = 64) -> StudentBase:
    """Factory function to create models."""
    models = {
        'SimpleCNN': SimpleCNN,
        'MiniCNN': MiniCNN
    }
    
    if model_type not in models:
        raise ValueError(f"Unknown model type: {model_type}. Available: {list(models.keys())}")
    
    return models[model_type](num_classes=num_classes, input_size=input_size)
