"""
data_loader.py — NSL-KDD Dataset Loader
Downloads the real NSL-KDD benchmark dataset and preprocesses it.
Falls back to synthetic data if download fails.
"""
import sys
import logging
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

# ── Make config importable from root ──────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

logger = logging.getLogger(__name__)

# ── NSL-KDD Schema ─────────────────────────────────────────────────────────────
NSL_KDD_COLUMNS = [
    'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
    'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins', 'logged_in',
    'num_compromised', 'root_shell', 'su_attempted', 'num_root',
    'num_file_creations', 'num_shells', 'num_access_files', 'num_outbound_cmds',
    'is_host_login', 'is_guest_login', 'count', 'srv_count',
    'serror_rate', 'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate',
    'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
    'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate',
    'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
    'dst_host_srv_serror_rate', 'dst_host_rerror_rate',
    'dst_host_srv_rerror_rate', 'label', 'difficulty_level'
]

CATEGORICAL_FEATURES = ['protocol_type', 'service', 'flag']

NUMERIC_FEATURES = [
    'duration', 'src_bytes', 'dst_bytes', 'land', 'wrong_fragment', 'urgent',
    'hot', 'num_failed_logins', 'logged_in', 'num_compromised', 'root_shell',
    'su_attempted', 'num_root', 'num_file_creations', 'num_shells',
    'num_access_files', 'num_outbound_cmds', 'is_host_login', 'is_guest_login',
    'count', 'srv_count', 'serror_rate', 'srv_serror_rate', 'rerror_rate',
    'srv_rerror_rate', 'same_srv_rate', 'diff_srv_rate', 'srv_diff_host_rate',
    'dst_host_count', 'dst_host_srv_count', 'dst_host_same_srv_rate',
    'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
    'dst_host_srv_diff_host_rate', 'dst_host_serror_rate',
    'dst_host_srv_serror_rate', 'dst_host_rerror_rate',
    'dst_host_srv_rerror_rate',
]

# Fine-grained labels → 5 attack categories (matches KDD'99 taxonomy)
ATTACK_MAP = {
    'normal': 'normal',
    # DoS
    'back': 'dos', 'land': 'dos', 'neptune': 'dos', 'pod': 'dos',
    'smurf': 'dos', 'teardrop': 'dos', 'mailbomb': 'dos', 'apache2': 'dos',
    'processtable': 'dos', 'udpstorm': 'dos',
    # Probe
    'ipsweep': 'probe', 'nmap': 'probe', 'portsweep': 'probe',
    'satan': 'probe', 'mscan': 'probe', 'saint': 'probe',
    # R2L
    'ftp_write': 'r2l', 'guess_passwd': 'r2l', 'imap': 'r2l',
    'multihop': 'r2l', 'phf': 'r2l', 'spy': 'r2l',
    'warezclient': 'r2l', 'warezmaster': 'r2l', 'sendmail': 'r2l',
    'named': 'r2l', 'snmpattack': 'r2l', 'snmpgetattack': 'r2l',
    'httptunnel': 'r2l', 'xlock': 'r2l', 'xsnoop': 'r2l', 'worm': 'r2l',
    # U2R
    'buffer_overflow': 'u2r', 'loadmodule': 'u2r', 'perl': 'u2r',
    'rootkit': 'u2r', 'ps': 'u2r', 'sqlattack': 'u2r', 'xterm': 'u2r',
}


# ── Download ────────────────────────────────────────────────────────────────────

def _download_file(url: str, dest: Path) -> bool:
    """Download a single file, returning True on success."""
    try:
        print(f"  ⬇  Downloading {dest.name} ...", end=" ", flush=True)
        urllib.request.urlretrieve(url, dest)
        print("✓")
        return True
    except Exception as exc:
        print(f"✗  ({exc})")
        logger.warning("Download failed for %s: %s", url, exc)
        if dest.exists():
            dest.unlink()
        return False


def download_nsl_kdd() -> bool:
    """
    Download NSL-KDD train/test files into the data/ directory.
    Skips files that already exist.

    Returns:
        True if both files are available, False otherwise.
    """
    train_ok = config.NSL_KDD_TRAIN_FILE.exists()
    test_ok  = config.NSL_KDD_TEST_FILE.exists()

    if train_ok and test_ok:
        logger.info("NSL-KDD files already present — skipping download.")
        print("✅ NSL-KDD dataset already present.")
        return True

    print("\n📥 Downloading NSL-KDD benchmark dataset...")
    if not train_ok:
        train_ok = _download_file(config.NSL_KDD_TRAIN_URL, config.NSL_KDD_TRAIN_FILE)
    if not test_ok:
        test_ok = _download_file(config.NSL_KDD_TEST_URL, config.NSL_KDD_TEST_FILE)

    if train_ok and test_ok:
        print("✅ NSL-KDD download complete.")
    else:
        print("⚠️  NSL-KDD download failed — will use synthetic data.")
    return train_ok and test_ok


# ── Load & Preprocess ──────────────────────────────────────────────────────────

def _encode_categoricals(train_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple:
    """Label-encode categorical columns consistently across train/test."""
    from sklearn.preprocessing import LabelEncoder
    for col in CATEGORICAL_FEATURES:
        le = LabelEncoder()
        le.fit(pd.concat([train_df[col], test_df[col]]).astype(str))
        train_df[col] = le.transform(train_df[col].astype(str))
        test_df[col]  = le.transform(test_df[col].astype(str))
    return train_df, test_df


def load_nsl_kdd(binary: bool = True):
    """
    Read and preprocess NSL-KDD from disk.

    Args:
        binary: If True → labels are 'normal' / 'attack'.
                If False → labels are 5-class categories (normal/dos/probe/r2l/u2r).

    Returns:
        (X_train, X_test, y_train, y_test) as DataFrames/Series, or None if failed.
    """
    if not (config.NSL_KDD_TRAIN_FILE.exists() and config.NSL_KDD_TEST_FILE.exists()):
        logger.info("NSL-KDD files not found on disk.")
        return None

    try:
        train_df = pd.read_csv(config.NSL_KDD_TRAIN_FILE,
                               header=None, names=NSL_KDD_COLUMNS)
        test_df  = pd.read_csv(config.NSL_KDD_TEST_FILE,
                               header=None, names=NSL_KDD_COLUMNS)

        for df in [train_df, test_df]:
            df['label'] = df['label'].str.strip().str.rstrip('.')
            df['label_cat']    = df['label'].map(ATTACK_MAP).fillna('other')
            df['label_binary'] = df['label'].apply(
                lambda x: 'normal' if x == 'normal' else 'attack'
            )

        train_df, test_df = _encode_categoricals(train_df, test_df)

        feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
        label_col    = 'label_binary' if binary else 'label_cat'

        X_train = train_df[feature_cols].reset_index(drop=True)
        y_train = train_df[label_col].reset_index(drop=True)
        X_test  = test_df[feature_cols].reset_index(drop=True)
        y_test  = test_df[label_col].reset_index(drop=True)

        mode = "binary" if binary else "5-class"
        print(f"\n✅ NSL-KDD loaded ({mode}): "
              f"{len(X_train):,} train / {len(X_test):,} test samples")
        _print_label_dist(y_train, "Train")
        _print_label_dist(y_test,  "Test")

        return X_train, X_test, y_train, y_test

    except Exception as exc:
        logger.error("Failed to parse NSL-KDD: %s", exc)
        return None


def _print_label_dist(y: pd.Series, split: str):
    counts = y.value_counts()
    parts  = [f"{lbl}: {n:,} ({n/len(y)*100:.1f}%)" for lbl, n in counts.items()]
    print(f"  {split}: " + " | ".join(parts))


# ── Public Unified Loader ──────────────────────────────────────────────────────

def load_dataset(binary: bool = True):
    """
    Download (if needed) and load the NSL-KDD dataset.
    Falls back to synthetic data on failure.

    Args:
        binary: True → binary labels; False → 5-class labels.

    Returns:
        (X_train, X_test, y_train, y_test, source_name)
    """
    from sklearn.model_selection import train_test_split

    download_nsl_kdd()
    result = load_nsl_kdd(binary=binary)

    if result is not None:
        X_train, X_test, y_train, y_test = result
        return X_train, X_test, y_train, y_test, "NSL-KDD"

    # ── Synthetic fallback ─────────────────────────────────────────────────────
    print("\n⚠️  Falling back to synthetic data.")
    if binary:
        from intrusion_detection import generate_synthetic_network_traffic
        df = generate_synthetic_network_traffic(
            config.N_SAMPLES_SYNTHETIC, config.ATTACK_RATIO
        )
        label = 'label'
    else:
        from traffic_classification import generate_multiclass_traffic
        df    = generate_multiclass_traffic(config.N_SAMPLES_SYNTHETIC)
        label = 'label'

    X = df.drop(label, axis=1)
    y = df[label]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size    = config.TEST_SIZE,
        random_state = config.RANDOM_STATE,
        stratify     = y,
    )
    return X_train, X_test, y_train, y_test, "Synthetic"
