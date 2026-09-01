import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob

def setup_style():
    sns.set_theme(style="white", context="paper")
    plt.rcParams.update({
        "font.size": 12,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "figure.titlesize": 16,
        "savefig.dpi": 300,
        "savefig.bbox": "tight"
    })

def plot_thermal_comparison(normal_dir, fever_dir, output_path):
    normal_files = glob.glob(os.path.join(normal_dir, "*.npy"))
    fever_files = glob.glob(os.path.join(fever_dir, "*.npy"))
    
    if not normal_files or not fever_files:
        print("Missing thermal data for visualization.")
        return

    normal_data = np.load(normal_files[0])
    fever_data = np.load(fever_files[0])

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    
    # Using a perceptually uniform colormap good for thermal data
    cmap = "inferno"

    sns.heatmap(normal_data, ax=axes[0], cmap=cmap, cbar=True, cbar_kws={'label': 'Temperature (°C)'})
    axes[0].set_title("Healthy Subject (Thermal Profile)")
    axes[0].axis('off')

    sns.heatmap(fever_data, ax=axes[1], cmap=cmap, cbar=True, cbar_kws={'label': 'Temperature (°C)'})
    axes[1].set_title("Feverish Subject (Thermal Profile)")
    axes[1].axis('off')

    plt.suptitle("Arogya AI: Thermal Sensor (24x32) Comparative Analysis", y=1.05)
    plt.savefig(output_path)
    plt.close()
    print(f"Saved thermal visualization to {output_path}")

def plot_multimodal_stream(csv_path, output_path):
    if not os.path.exists(csv_path):
        print(f"Missing {csv_path} for visualization.")
        return
        
    try:
        # Load only the first 6 columns to avoid label parsing issues
        df = pd.read_csv(csv_path, usecols=[0, 1, 2, 3, 4, 5], names=["Timestamp", "ECG", "GSR", "Gas", "Pulse_IR", "Temp_Max"], header=0)
        
        # Take a 1000 sample window for clear visualization
        window = df.iloc[1000:2000].copy()
        
        # Normalize timestamp to seconds
        window["Time_s"] = (window["Timestamp"] - window["Timestamp"].iloc[0]) / 1000.0
        
        fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
        
        # Plot ECG
        axes[0].plot(window["Time_s"], window["ECG"], color="royalblue", linewidth=1.5)
        axes[0].set_title("ECG Signal")
        axes[0].set_ylabel("Amplitude")
        axes[0].grid(True, linestyle="--", alpha=0.6)
        
        # Plot Pulse (PPG)
        axes[1].plot(window["Time_s"], window["Pulse_IR"], color="crimson", linewidth=1.5)
        axes[1].set_title("Pulse (IR) Signal")
        axes[1].set_ylabel("Amplitude")
        axes[1].grid(True, linestyle="--", alpha=0.6)
        
        # Plot GSR
        axes[2].plot(window["Time_s"], window["GSR"], color="forestgreen", linewidth=1.5)
        axes[2].set_title("Galvanic Skin Response (GSR)")
        axes[2].set_ylabel("Conductance")
        axes[2].set_xlabel("Time (seconds)")
        axes[2].grid(True, linestyle="--", alpha=0.6)
        
        plt.suptitle("Arogya AI: Multimodal Physiological Sensor Streams", y=1.02)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        print(f"Saved multimodal visualization to {output_path}")
        
    except Exception as e:
        print(f"Error plotting multimodal data: {e}")

def plot_training_curves(history_csv, output_path):
    if not os.path.exists(history_csv):
        print(f"Training history {history_csv} not found.")
        return
        
    df = pd.read_csv(history_csv)
    fig, ax1 = plt.subplots(figsize=(8, 5))

    color1 = 'tab:red'
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Training Loss', color=color1)
    ax1.plot(df['Epoch'], df['Loss'], color=color1, marker='o', linewidth=2, label='Loss')
    ax1.tick_params(axis='y', labelcolor=color1)

    ax2 = ax1.twinx()
    color2 = 'tab:blue'
    ax2.set_ylabel('Validation Accuracy', color=color2)
    ax2.plot(df['Epoch'], df['Val_Acc'], color=color2, marker='s', linewidth=2, label='Val Acc')
    ax2.tick_params(axis='y', labelcolor=color2)

    plt.title("Arogya AI: FeverCNN Training Dynamics")
    fig.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved training curve to {output_path}")

def plot_model_metrics(output_path):
    # Data from Arogya AI_Project_Report.md
    classes = ['Healthy', 'Fever']
    accuracy = [100.0, 100.0]
    confidence = [98.01, 99.27]

    x = np.arange(len(classes))
    width = 0.35

    fig, ax = plt.subplots(figsize=(7, 5))
    rects1 = ax.bar(x - width/2, accuracy, width, label='Accuracy (%)', color='mediumseagreen')
    rects2 = ax.bar(x + width/2, confidence, width, label='Avg Confidence (%)', color='royalblue')

    ax.set_ylabel('Percentage (%)')
    ax.set_title('Arogya AI: Final Model Evaluation Metrics')
    ax.set_xticks(x)
    ax.set_xticklabels(classes)
    ax.set_ylim(0, 120)
    ax.legend(loc='lower right')

    ax.bar_label(rects1, padding=3, fmt='%.1f')
    ax.bar_label(rects2, padding=3, fmt='%.2f')

    fig.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved model metrics to {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    normal_dir = os.path.join(base_dir, "datasets", "SmartASHA_Dataset", "Normal")
    fever_dir = os.path.join(base_dir, "datasets", "SmartASHA_Dataset", "Fever")
    csv_path = os.path.join(base_dir, "data", "resting_baseline.csv")
    
    out_dir = os.path.join(base_dir, "docs", "visualizations")
    os.makedirs(out_dir, exist_ok=True)
    
    setup_style()
    plot_thermal_comparison(normal_dir, fever_dir, os.path.join(out_dir, "thermal_comparison.png"))
    plot_multimodal_stream(csv_path, os.path.join(out_dir, "multimodal_streams.png"))
    
    history_csv = os.path.join(out_dir, "training_history.csv")
    plot_training_curves(history_csv, os.path.join(out_dir, "training_curves.png"))
    plot_model_metrics(os.path.join(out_dir, "model_metrics.png"))
