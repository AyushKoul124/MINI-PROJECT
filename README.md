# 🛡️ AI-Based Cybersecurity Network Intrusion Detection System (NIDS)

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.x-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

> **Project 16 — Implementation of an AI-Based Cybersecurity Use Case**  

A comprehensive Machine Learning framework for network intrusion detection, anomaly analysis,
multi-class traffic classification, and adversarial-robustness evaluation — all wrapped in an
interactive Streamlit dashboard.

---

## 📋 Table of Contents

1. [Architecture](#-architecture)
2. [Dataset](#-dataset)
3. [Installation](#-installation)
4. [Quick Start](#-quick-start)
5. [Components](#-components)
6. [Results](#-results)
7. [Project Structure](#-project-structure)
8. [Authors](#-authors)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  AI-Based Cybersecurity System                  │
│                        (Project 16)                             │
└──────────┬──────────────┬──────────────┬────────────────────────┘
           │              │              │               │
   ┌───────▼────┐  ┌──────▼──────┐ ┌────▼──────┐ ┌─────▼────────┐
   │ Intrusion  │  │  Anomaly    │ │  Traffic  │ │ Adversarial  │
   │ Detection  │  │ Detection   │ │Classific. │ │  Attack Sim. │
   │ (Binary)   │  │(Unsupervsd.)│ │(5-class)  │ │  Analysis    │
   │            │  │             │ │           │ │              │
   │ • RF       │  │ • Isolation │ │ • Random  │ │ • FGSM       │
   │ • DT       │  │   Forest    │ │   Forest  │ │ • Rnd. Noise │
   │ • MLP      │  │ • 1-class   │ │           │ │ • Feat. Manip│
   │            │  │   SVM       │ │           │ │              │
   └────────────┘  └─────────────┘ └───────────┘ └──────────────┘
           │              │              │               │
           └──────────────┴──────────────┴───────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Streamlit Dashboard │
                    │  (Interactive UI)    │
                    └─────────────────────┘
```

---

## 📦 Dataset

The project is designed around the **NSL-KDD** dataset — the standard benchmark for
network intrusion detection research.

| Property         | Detail                                      |
|------------------|---------------------------------------------|
| **Source**       | Canadian Institute for Cybersecurity (CIC)  |
| **Features**     | 41 per connection record (continuous + categorical) |
| **Training set** | ~125 973 records                            |
| **Test set**     | ~22 544 records                             |
| **Classes**      | 5 (Normal, DoS, Probe, R2L, U2R)            |
| **Format**       | CSV / ARFF                                  |

### Traffic Categories

| Label      | Description                                          | Approx. Share |
|------------|------------------------------------------------------|---------------|
| **Normal** | Legitimate network traffic                           | 53 %          |
| **DoS**    | Denial-of-Service (flood, smurf, neptune …)          | 23 %          |
| **Probe**  | Surveillance & scanning (portsweep, nmap …)          | 14 %          |
| **R2L**    | Remote-to-Local unauthorised access (ftp_write …)    | 9 %           |
| **U2R**    | User-to-Root privilege escalation (buffer overflow …)| 1 %           |

> NSL-KDD resolves the redundancy issues in the original KDD Cup 1999 dataset and provides
> a balanced, reproducible benchmark.

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-cybersecurity.git
cd ai-cybersecurity/MINI-PROJECT

# 2. (Recommended) Create a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

**Minimum requirements** (add to `requirements.txt`):

```text
numpy>=1.24
pandas>=1.5
scikit-learn>=1.2
matplotlib>=3.6
seaborn>=0.12
streamlit>=1.28
```

---

## 🚀 Quick Start

```bash
# Run all four components sequentially
python main.py

# Run a specific component
python main.py --component intrusion
python main.py --component anomaly
python main.py --component traffic
python main.py --component adversarial

# Launch the interactive web dashboard
streamlit run dashboard.py
```

Open your browser at **http://localhost:8501** to explore the dashboard.

---

## 🔬 Components

### 1. 🔍 Intrusion Detection System (`src/intrusion_detection.py`)

Supervised binary classification that distinguishes **Normal** traffic from **Attack** traffic.

- **Algorithms**: Random Forest (100 trees), Decision Tree (max-depth 10), MLP Neural Network (64-32)
- **Features**: StandardScaler normalisation, LabelEncoder for targets
- **Output**: Accuracy, Precision, Recall, F1-Score, Confusion Matrix, Feature Importance

```python
from src.intrusion_detection import IntrusionDetectionSystem, compare_algorithms

ids = IntrusionDetectionSystem(algorithm='random_forest')
ids.train(X_train, y_train)
metrics, y_pred = ids.evaluate(X_test, y_test)
```

---

### 2. 📡 Anomaly Detection (`src/anomaly_detection.py`)

Unsupervised detection of network anomalies — no labelled attack data needed during training.

- **Methods**: Isolation Forest, One-Class SVM
- **Output**: Accuracy, Precision, Recall, F1-Score, ROC-AUC, ROC Curve

```python
from src.anomaly_detection import AnomalyDetector, compare_anomaly_methods

detector = AnomalyDetector(method='isolation_forest', contamination=0.3)
detector.fit(X_train)
metrics, y_pred = detector.evaluate(X_test, y_test_binary)
```

---

### 3. 🌐 Traffic Classification (`src/src/traffic_classification.py`)

Multi-class classification of five distinct traffic categories using a Random Forest.

- **Classes**: Normal, DoS, Probe, R2L, U2R
- **Output**: Per-class Precision/Recall/F1, multi-class Confusion Matrix, Class Distribution charts

```python
from src.src.traffic_classification import TrafficClassifier, generate_multiclass_traffic

df = generate_multiclass_traffic(n_samples=10_000)
clf = TrafficClassifier()
clf.train(X_train, y_train)
accuracy, y_pred = clf.evaluate(X_test, y_test)
```

---

### 4. ⚔️ Adversarial Attacks (`src/adversarial_attacks.py`)

Probes the robustness of a trained IDS against three adversarial strategies.

| Attack                  | Description                                                      |
|-------------------------|------------------------------------------------------------------|
| **FGSM**                | Gradient-based perturbation (ε-scaled random noise simulation)   |
| **Random Noise**        | Proportional Gaussian noise added to all features                |
| **Feature Manipulation**| Targeted reduction of high-importance features to evade detection |

```python
from src.adversarial_attacks import AdversarialAttackSimulator, demonstrate_adversarial_attacks

simulator = AdversarialAttackSimulator(model=ids.model, scaler=ids.scaler)
results = simulator.evaluate_robustness(X_test, y_test_binary, attack_type='fgsm', epsilon=0.1)
```

---

## 📊 Results

### Intrusion Detection (Binary Classification — Synthetic NSL-KDD-style data)

| Model              | Accuracy | Precision | Recall | F1-Score | Train Time |
|--------------------|----------|-----------|--------|----------|------------|
| **Random Forest**  | ~99.0%   | ~0.990    | ~0.990 | ~0.990   | ~2.1 s     |
| **Decision Tree**  | ~98.2%   | ~0.982    | ~0.982 | ~0.982   | ~0.1 s     |
| **Neural Network** | ~97.5%   | ~0.975    | ~0.975 | ~0.975   | ~8.3 s     |

### Anomaly Detection (Unsupervised)

| Method              | Accuracy | F1-Score | AUC-ROC |
|---------------------|----------|----------|---------|
| **Isolation Forest**| ~85%     | ~0.83    | ~0.91   |
| **One-Class SVM**   | ~78%     | ~0.76    | ~0.87   |

### Traffic Classification (5-class)

| Class    | Precision | Recall | F1-Score |
|----------|-----------|--------|----------|
| Normal   | ~0.99     | ~0.99  | ~0.99    |
| DoS      | ~0.99     | ~0.99  | ~0.99    |
| Probe    | ~0.98     | ~0.97  | ~0.97    |
| R2L      | ~0.96     | ~0.96  | ~0.96    |
| U2R      | ~0.95     | ~0.94  | ~0.94    |

---

## 📁 Project Structure

```
MINI-PROJECT/
├── dashboard.py                  # 🖥️  Streamlit web dashboard (main UI)
├── README.md                     # 📖  This file
│
├── src/                          # Source modules
│   ├── intrusion_detection.py    # 🔍  Binary IDS (RF, DT, MLP)
│   ├── anomaly_detection.py      # 📡  Unsupervised anomaly detection
│   ├── adversarial_attacks.py    # ⚔️   Adversarial robustness analysis
│   ├── main.py                   # ▶️   CLI entry point (runs all components)
│   └── src/
│       └── traffic_classification.py  # 🌐 Multi-class traffic classifier
│
├── data/                         # (created at runtime)
│   └── NSL-KDD/
│       ├── KDDTrain+.txt
│       └── KDDTest+.txt
│
└── docs/                         # (created at runtime — generated plots)
    ├── algorithm_comparison.png
    ├── confusion_matrix_rf.png
    ├── anomaly_comparison.png
    ├── adversarial_attacks_comparison.png
    └── class_distribution.png
```

---

## 👨‍💻 Authors

| Name                       | Role                                     | Institution                                              |
|----------------------------|------------------------------------------|----------------------------------------------------------|
| **Ayush Koul**             | Front end, AI research                   | Model Institute of Engineering and Technology (Autonomous) |
| **Vinayak Singh Jamwal**   | AI research, ML research                 | Model Institute of Engineering and Technology (Autonomous) |
| **Prajwal Shan**           | Backend, Implementation                  | Model Institute of Engineering and Technology (Autonomous) |

---

## 📄 License

This project is released under the [MIT License](LICENSE).  
Feel free to use, modify, and distribute for educational purposes.

---

<div align="center">
Made with ❤️ using Python · scikit-learn · Streamlit · NSL-KDD
</div>
