"""
traffic_classification.py — Multi-Class Network Traffic Classifier
Classes: Normal, DoS, Probe, R2L, U2R  (NSL-KDD taxonomy)
Dataset: NSL-KDD (with synthetic fallback)
"""
import sys
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
import joblib
import warnings
warnings.filterwarnings('ignore')

# ── Path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
class TrafficClassifier:
    """Multi-class network traffic classifier (Normal / DoS / Probe / R2L / U2R)."""

    def __init__(self):
        self.model         = RandomForestClassifier(
            n_estimators=config.RF_N_ESTIMATORS,
            random_state=config.RANDOM_STATE, n_jobs=-1)
        self.scaler        = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = None

    # ── Preprocessing ─────────────────────────────────────────────────────────
    def preprocess_data(self, X, y=None, fit: bool = True):
        if isinstance(X, pd.DataFrame):
            self.feature_names = list(X.columns)
        X_scaled = self.scaler.fit_transform(X) if fit else self.scaler.transform(X)
        if y is not None:
            y_enc = (self.label_encoder.fit_transform(y)
                     if fit else self.label_encoder.transform(y))
            return X_scaled, y_enc
        return X_scaled

    # ── Train ─────────────────────────────────────────────────────────────────
    def train(self, X_train, y_train):
        print("\n  Training Multi-Class Traffic Classifier...")
        X_s, y_enc = self.preprocess_data(X_train, y_train, fit=True)
        self.model.fit(X_s, y_enc)
        print(f"  ✓ Done  |  Classes: {', '.join(self.label_encoder.classes_)}")

    # ── Inference ─────────────────────────────────────────────────────────────
    def predict(self, X_test):
        X_s    = self.preprocess_data(X_test, fit=False)
        y_enc  = self.model.predict(X_s)
        return self.label_encoder.inverse_transform(y_enc)

    # ── Evaluation ────────────────────────────────────────────────────────────
    def evaluate(self, X_test, y_test):
        y_pred   = self.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\n{'='*60}")
        print(f"  TRAFFIC CLASSIFICATION RESULTS")
        print(f"{'='*60}")
        print(f"  Overall Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"\n{classification_report(y_test, y_pred)}")
        return accuracy, y_pred

    # ── Plots ─────────────────────────────────────────────────────────────────
    def plot_confusion_matrix(self, y_test, y_pred, save_path=None):
        try:
            plt.style.use(config.PLOT_STYLE)
        except Exception:
            pass

        cm = confusion_matrix(y_test, y_pred,
                              labels=self.label_encoder.classes_)
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='YlOrRd',
                    xticklabels=self.label_encoder.classes_,
                    yticklabels=self.label_encoder.classes_,
                    cbar_kws={'label': 'Samples'}, ax=ax)
        ax.set_title('Traffic Classification — Confusion Matrix',
                     fontsize=14, fontweight='bold', pad=12)
        ax.set_ylabel('True Label', fontsize=12)
        ax.set_xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=config.DPI, bbox_inches='tight')
            logger.info("Confusion matrix saved → %s", save_path)
        return fig

    def plot_class_distribution(self, y_train, y_test, save_path=None):
        try:
            plt.style.use(config.PLOT_STYLE)
        except Exception:
            pass

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle('Class Distribution in Train / Test Sets',
                     fontsize=14, fontweight='bold')

        for ax, y, split, color in zip(
                axes, [y_train, y_test], ['Train', 'Test'],
                [config.PALETTE[0], config.PALETTE[1]]):
            counts = pd.Series(y).value_counts().sort_index()
            bars = ax.bar(counts.index, counts.values,
                          color=color, alpha=0.85,
                          edgecolor='white', linewidth=1.2)
            ax.set_title(f'{split} Set', fontsize=12, fontweight='bold')
            ax.set_xlabel('Traffic Class', fontsize=11)
            ax.set_ylabel('Number of Samples', fontsize=11)
            ax.tick_params(axis='x', rotation=20)
            ax.grid(axis='y', alpha=0.4)
            for bar, v in zip(bars, counts.values):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(counts.values) * 0.01,
                        f'{v:,}', ha='center', va='bottom',
                        fontweight='bold', fontsize=9)

        plt.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=config.DPI, bbox_inches='tight')
            logger.info("Class distribution saved → %s", save_path)
        return fig

    def plot_feature_importance(self, top_n: int = 15, save_path=None):
        if not hasattr(self.model, 'feature_importances_') or not self.feature_names:
            return None
        try:
            plt.style.use(config.PLOT_STYLE)
        except Exception:
            pass

        imp  = self.model.feature_importances_
        idx  = np.argsort(imp)[-top_n:]
        fig, ax = plt.subplots(figsize=(9, max(5, top_n * 0.45)))
        colors  = plt.cm.plasma(np.linspace(0.3, 0.9, top_n))
        ax.barh([self.feature_names[i] for i in idx], imp[idx],
                color=colors, edgecolor='white', height=0.7)
        ax.set_xlabel('Importance Score', fontsize=12)
        ax.set_title('Feature Importance — Traffic Classifier',
                     fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.4)
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=config.DPI, bbox_inches='tight')
        return fig

    # ── Persistence ───────────────────────────────────────────────────────────
    def save_model(self, path=None):
        path = Path(path) if path else config.MODELS_DIR / 'traffic_classifier.pkl'
        joblib.dump(dict(model=self.model, scaler=self.scaler,
                         label_encoder=self.label_encoder,
                         feature_names=self.feature_names), path)
        print(f"  💾 Model saved → {path}")

    def load_model(self, path=None):
        path = Path(path) if path else config.MODELS_DIR / 'traffic_classifier.pkl'
        p = joblib.load(path)
        self.model, self.scaler = p['model'], p['scaler']
        self.label_encoder      = p['label_encoder']
        self.feature_names      = p['feature_names']


# ══════════════════════════════════════════════════════════════════════════════
# Synthetic Multi-Class Generator (fallback)
# ══════════════════════════════════════════════════════════════════════════════

def generate_multiclass_traffic(n_samples: int = 10000) -> pd.DataFrame:
    """Generate synthetic 5-class traffic data (normal/dos/probe/r2l/u2r)."""
    print(f"\n⚙  Generating {n_samples:,} multi-class traffic samples...")
    np.random.seed(config.RANDOM_STATE)

    proportions = {'normal': 0.50, 'dos': 0.20, 'probe': 0.15,
                   'r2l': 0.10, 'u2r': 0.05}

    def _features(n, t):
        base = dict(
            duration=0, src_bytes=0, dst_bytes=0, wrong_fragment=0, urgent=0,
            hot=0, num_failed_logins=0, logged_in=0, num_compromised=0,
            count=0, srv_count=0, serror_rate=0, srv_serror_rate=0,
            rerror_rate=0, same_srv_rate=0)

        if t == 'normal':
            base.update(
                duration=np.random.exponential(10, n),
                src_bytes=np.random.lognormal(7, 2, n),
                dst_bytes=np.random.lognormal(7, 2, n),
                wrong_fragment=np.random.poisson(0.1, n),
                urgent=np.random.poisson(0.05, n),
                hot=np.random.poisson(0.5, n),
                logged_in=np.ones(n),
                count=np.random.poisson(5, n),
                srv_count=np.random.poisson(5, n),
                serror_rate=np.random.uniform(0, 0.1, n),
                srv_serror_rate=np.random.uniform(0, 0.1, n),
                rerror_rate=np.random.uniform(0, 0.1, n),
                same_srv_rate=np.random.uniform(0.8, 1, n))
        elif t == 'dos':
            base.update(
                duration=np.random.exponential(2, n),
                src_bytes=np.random.lognormal(5, 1, n),
                dst_bytes=np.random.lognormal(4, 1, n),
                wrong_fragment=np.random.poisson(3, n),
                count=np.random.poisson(50, n),
                srv_count=np.random.poisson(45, n),
                serror_rate=np.random.uniform(0.5, 1, n),
                srv_serror_rate=np.random.uniform(0.5, 1, n),
                rerror_rate=np.random.uniform(0.3, 0.8, n),
                same_srv_rate=np.random.uniform(0.9, 1, n))
        elif t == 'probe':
            base.update(
                duration=np.random.exponential(5, n),
                src_bytes=np.random.lognormal(5, 1.5, n),
                dst_bytes=np.random.lognormal(4, 1.5, n),
                num_failed_logins=np.random.poisson(1, n),
                logged_in=np.random.binomial(1, 0.2, n),
                count=np.random.poisson(25, n),
                srv_count=np.random.poisson(3, n),
                serror_rate=np.random.uniform(0.2, 0.6, n),
                rerror_rate=np.random.uniform(0.4, 0.8, n),
                same_srv_rate=np.random.uniform(0.1, 0.3, n))
        elif t == 'r2l':
            base.update(
                duration=np.random.exponential(30, n),
                src_bytes=np.random.lognormal(8, 2, n),
                dst_bytes=np.random.lognormal(6, 2, n),
                hot=np.random.poisson(2, n),
                num_failed_logins=np.random.poisson(3, n),
                logged_in=np.random.binomial(1, 0.4, n),
                num_compromised=np.random.poisson(1, n),
                count=np.random.poisson(8, n),
                srv_count=np.random.poisson(7, n),
                same_srv_rate=np.random.uniform(0.6, 0.9, n))
        else:  # u2r
            base.update(
                duration=np.random.exponential(40, n),
                src_bytes=np.random.lognormal(9, 2, n),
                dst_bytes=np.random.lognormal(7, 2, n),
                hot=np.random.poisson(4, n),
                num_failed_logins=np.random.poisson(2, n),
                logged_in=np.ones(n),
                num_compromised=np.random.poisson(2, n),
                count=np.random.poisson(6, n),
                srv_count=np.random.poisson(5, n))

        # Ensure all are arrays
        for k, v in base.items():
            if np.isscalar(v):
                base[k] = np.full(n, v)
        base['label'] = [t] * n
        return pd.DataFrame(base)

    frames = [_features(int(n_samples * p), t)
              for t, p in proportions.items()]
    df = pd.concat(frames, ignore_index=True)
    df = df.sample(frac=1, random_state=config.RANDOM_STATE).reset_index(drop=True)

    for t in proportions:
        n = (df['label'] == t).sum()
        print(f"  {t:8s}: {n:,} ({n/len(df)*100:.1f}%)")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "="*70)
    print("  NETWORK TRAFFIC CLASSIFICATION  (5-Class)")
    print("  Classes: Normal | DoS | Probe | R2L | U2R")
    print("="*70)

    # ── Load dataset ──────────────────────────────────────────────────────────
    try:
        from data_loader import load_dataset
        X_train, X_test, y_train, y_test, source = load_dataset(binary=False)
    except Exception as exc:
        logger.warning("data_loader failed (%s), using synthetic.", exc)
        df = generate_multiclass_traffic(config.N_SAMPLES_SYNTHETIC)
        X  = df.drop('label', axis=1)
        y  = df['label']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=config.TEST_SIZE,
            random_state=config.RANDOM_STATE, stratify=y)
        source = "Synthetic"

    print(f"\n  Source : {source}")
    print(f"  Train  : {len(X_train):,}  |  Test: {len(X_test):,}")

    clf = TrafficClassifier()
    clf.train(X_train, y_train)
    accuracy, y_pred = clf.evaluate(X_test, y_test)
    clf.save_model()

    clf.plot_class_distribution(
        y_train, y_test,
        save_path=config.DOCS_DIR / 'class_distribution.png')
    clf.plot_confusion_matrix(
        y_test, y_pred,
        save_path=config.DOCS_DIR / 'confusion_matrix_multiclass.png')
    clf.plot_feature_importance(
        save_path=config.DOCS_DIR / 'feature_importance_traffic.png')

    print("\n  ✅ Traffic Classification complete.")
    print("="*70)


if __name__ == "__main__":
    main()
