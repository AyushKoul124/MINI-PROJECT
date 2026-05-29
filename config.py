"""
config.py — Central Configuration
AI-Based Cybersecurity Mini Project
"""
from pathlib import Path

# ── Directories ────────────────────────────────────────────────────────────────
ROOT_DIR   = Path(__file__).parent
DATA_DIR   = ROOT_DIR / "data"
DOCS_DIR   = ROOT_DIR / "docs"
MODELS_DIR = ROOT_DIR / "models"
LOGS_DIR   = ROOT_DIR / "logs"
SRC_DIR    = ROOT_DIR / "src"

for _d in [DATA_DIR, DOCS_DIR, MODELS_DIR, LOGS_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# ── NSL-KDD Dataset ────────────────────────────────────────────────────────────
NSL_KDD_TRAIN_URL  = "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain%2B.txt"
NSL_KDD_TEST_URL   = "https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTest%2B.txt"
NSL_KDD_TRAIN_FILE = DATA_DIR / "KDDTrain+.txt"
NSL_KDD_TEST_FILE  = DATA_DIR / "KDDTest+.txt"

# Synthetic fallback
N_SAMPLES_SYNTHETIC = 10000
ATTACK_RATIO        = 0.3

# ── General ML ─────────────────────────────────────────────────────────────────
RANDOM_STATE = 42
TEST_SIZE    = 0.3
CV_FOLDS     = 5
N_JOBS       = -1

# ── Model Hyperparameters ──────────────────────────────────────────────────────
RF_N_ESTIMATORS = 100
DT_MAX_DEPTH    = 10
MLP_HIDDEN      = (64, 32)
MLP_MAX_ITER    = 500

IF_CONTAMINATION = 0.3
OC_SVM_NU        = 0.3

# ── Adversarial Attack Parameters ─────────────────────────────────────────────
FGSM_EPSILON        = 0.1
RANDOM_NOISE_LEVEL  = 0.05
MANIPULATION_FACTOR = 0.5

# ── Plotting ───────────────────────────────────────────────────────────────────
PLOT_STYLE    = "seaborn-v0_8-darkgrid"
COLOR_PALETTE = ["#6C63FF", "#FF6584", "#43C6AC", "#F8D800", "#FF9A3C"]
PALETTE       = COLOR_PALETTE          # alias used in some modules
FIGURE_DPI    = 150
DPI           = 150                    # alias used in some modules
