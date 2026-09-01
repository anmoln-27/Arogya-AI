# Arogya AI Utilities Package
"""
Shared utilities for the Arogya AI project.

Modules:
    config      — Project-wide paths and directory configuration
    models      — FeverCNN model architecture definition
    asha_logger — Real-time serial data logger for ESP32 sensors
    clean_dataset — Dataset cleaning and preprocessing utilities
    parse_spectral_data — Spectral + PPG sensor data parser
"""

from .config import *
from .models import FeverCNN, get_model
