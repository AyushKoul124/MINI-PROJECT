"""
intrusion_detection.py — AI-Based Intrusion Detection System
Supervised learning models: Random Forest, Decision Tree, Neural Network
Dataset: NSL-KDD (with synthetic fallback)
"""
import sys
import time
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, classification_report)
import warnings
warnings.filterwarnings('ignore')

# ── Path setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent.parent))
import config

logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(name)s | %(message)s')
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Class: IntrusionDetectionSystem
# ══════════════════════════════════════════════════════════════════════════════

class IntrusionDetectionSystem:
    """
    AI-based Intrusion Detection System with multiple ML algorithms.
    Supports training, evaluation, cross-validation, feature importance,
    and model persistence via joblib.
    """

    ALGORITHMS = {
        'random_forest': lambda: RandomForestClassifier(
            n_estimators=config.RF_N_ESTIMATORS,
            random_state=config.RANDOM_STATE, n_jobs=-1),
        'decision_tree': lambda: DecisionTreeClassifier(
            random_state=config.RANDOM_STATE, max_depth=config.DT_MAX_DEPTH),
        'neural_network': lambda: MLPClassifier(
            hidden_layer_sizes=config.MLP_HIDDEN,
            max_iter=config.MLP_MAX_ITER,
            random_state=config.RANDOM_STATE),
    }

    def __init__(self, algorithm: str = 'random_forest'):
        if algorithm not in self.ALGORITHMS:
            raise ValueError(f"Unknown algorithm '{algorithm}'. "
                             f"Choose from: {list(self.ALGORITHMS)}")
        self.algorithm     = algorithm
        self.model         = self.ALGORITHMS[algorithm]()
        self.scaler        = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = None
        self.training_time = 0.0
        self.prediction_time = 0.0

    # ── Preprocessing ──────────────────────────────────────────────────────────

    def preprocess_data(self, X, y=None, fit: bool = True):
        """Scale features and (optionally) encode labels."""
        if isinstance(X, pd.DataFrame):
            self.feature_names = list(X.columns)
            for col in X.select_dtypes(include=['object']).columns:
                le = LabelEncoder()
                X = X.copy()
                if fit:
                    X[col] = le.fit_transform(X[col].astype(str))
                else:
                    X[col] = le.transform(X[col].astype(str))

        X_scaled = self.scaler.fit_transform(X) if fit else self.scaler.transform(X)

        if y is not None:
            y_enc = (self.label_encoder.fit_transform(y)
                     if fit else self.label_encoder.transform(y))
            return X_scaled, y_enc
        return X_scaled

    # ── Training ──────────────────────────────────────────────────────────────

    def train(self, X_train, y_train):
        """Fit the model and log training time."""
        logger.info("Training %s ...", self.algorithm)
        print(f"\n{'='*60}")
        print(f"  Training {self.algorithm.upper().replace('_',' ')}")
        print(f"{'='*60}")

        X_scaled, y_enc = self.preprocess_data(X_train, y_train, fit=True)

        t0 = time.time()
        self.model.fit(X_scaled, y_enc)
        self.training_time = time.time() - t0

        print(f"  ✓ Done in {self.training_time:.3f}s")
        self._print_feature_importance(top_n=10)

    def _print_feature_importance(self, top_n: int = 10):
        if not hasattr(self.model, 'feature_importances_') or not self.feature_names:
            return
        imp  = self.model.feature_importances_
        idx  = np.argsort(imp)[::-1][:top_n]
        print(f"\n  Top {top_n} Features:")
        for rank, i in enumerate(idx, 1):
            print(f"    {rank:2d}. {self.feature_names[i]:<35s} {imp[i]:.4f}")

    # ── Inference ─────────────────────────────────────────────────────────────

    def predict(self, X_test):
        X_scaled = self.preprocess_data(X_test, fit=False)
        t0 = time.time()
        y_enc = self.model.predict(X_scaled)
        self.prediction_time = time.time() - t0
        return self.label_encoder.inverse_transform(y_enc)

    # ── Evaluation ────────────────────────────────────────────────────────────

    def evaluate(self, X_test, y_test):
        """Return metrics dict and predictions."""
        y_pred = self.predict(X_test)
        acc    = accuracy_score(y_test, y_pred)
        unique = np.unique(y_test)
        avg    = 'binary' if len(unique) == 2 else 'weighted'
        pos    = ('attack' if 'attack' in unique else unique[1]) if avg == 'binary' else None

        kw = dict(pos_label=pos, zero_division=0) if avg == 'binary' else \
             dict(average='weighted', zero_division=0)
        prec = precision_score(y_test, y_pred, **kw)
        rec  = recall_score(y_test, y_pred, **kw)
        f1   = f1_score(y_test, y_pred, **kw)

        metrics = dict(accuracy=acc, precision=prec, recall=rec, f1_score=f1,
                       training_time=self.training_time,
                       prediction_time=self.prediction_time)
        return metrics, y_pred

    def cross_validate(self, X, y, cv: int = None):
        """
        Run stratified k-fold cross-validation.

        Returns:
            dict with mean/std of accuracy, precision, recall, f1.
        """
        cv = cv or config.CV_FOLDS
        logger.info("Cross-validating %s with %d folds ...", self.algorithm, cv)
        print(f"\n  📊 Cross-Validation ({cv} folds) — {self.algorithm}")

        X_scaled, y_enc = self.preprocess_data(X, y, fit=True)
        skf = StratifiedKFold(n_splits=cv, shuffle=True,
                              random_state=config.RANDOM_STATE)

        cv_results = {}
        for scorer in ('accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted'):
            scores = cross_val_score(self.model, X_scaled, y_enc,
                                     cv=skf, scoring=scorer, n_jobs=-1)
            key = scorer.replace('_weighted', '')
            cv_results[key] = {'mean': scores.mean(), 'std': scores.std(), 'scores': scores}
            print(f"    {key:12s}: {scores.mean():.4f} ± {scores.std():.4f}")

        return cv_results

    def print_evaluation_report(self, y_test, y_pred, metrics):
        print(f"\n{'='*60}")
        print(f"  Results — {self.algorithm.upper().replace('_',' ')}")
        print(f"{'='*60}")
        print(f"  Accuracy :  {metrics['accuracy']:.4f}  ({metrics['accuracy']*100:.2f}%)")
        print(f"  Precision:  {metrics['precision']:.4f}")
        print(f"  Recall   :  {metrics['recall']:.4f}")
        print(f"  F1-Score :  {metrics['f1_score']:.4f}")
        print(f"  Train t  :  {metrics['training_time']:.4f}s")
        print(f"  Pred  t  :  {metrics['prediction_time']:.6f}s")
        print(f"\n{classification_report(y_test, y_pred)}")

    # ── Plots ─────────────────────────────────────────────────────────────────

    def plot_confusion_matrix(self, y_test, y_pred, save_path=None):
        """Plot and optionally save confusion matrix."""
        try:
            plt.style.use(config.PLOT_STYLE)
        except Exception:
            pass

        cm = confusion_matrix(y_test, y_pred,
                              labels=self.label_encoder.classes_)
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=self.label_encoder.classes_,
                    yticklabels=self.label_encoder.classes_, ax=ax)
        ax.set_title(f'Confusion Matrix — {self.algorithm.upper().replace("_"," ")}',
                     fontsize=14, fontweight='bold', pad=12)
        ax.set_ylabel('True Label', fontsize=12)
        ax.set_xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=config.DPI, bbox_inches='tight')
            logger.info("Confusion matrix saved → %s", save_path)
        return fig

    def plot_feature_importance(self, top_n: int = 15, save_path=None):
        """Horizontal bar chart of top feature importances (tree models only)."""
        if not hasattr(self.model, 'feature_importances_') or not self.feature_names:
            logger.warning("Feature importance not available for %s", self.algorithm)
            return None

        try:
            plt.style.use(config.PLOT_STYLE)
        except Exception:
            pass

        imp  = self.model.feature_importances_
        idx  = np.argsort(imp)[-top_n:]
        names = [self.feature_names[i] for i in idx]
        vals  = imp[idx]

        fig, ax = plt.subplots(figsize=(9, max(5, top_n * 0.45)))
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(vals)))
        ax.barh(names, vals, color=colors, edgecolor='white', height=0.7)
        ax.set_xlabel('Importance Score', fontsize=12)
        ax.set_title(f'Feature Importance — {self.algorithm.upper().replace("_"," ")}',
                     fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.4)
        for v, name in zip(vals, names):
            ax.text(v + 0.001, name, f'{v:.4f}', va='center', fontsize=8)
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=config.DPI, bbox_inches='tight')
            logger.info("Feature importance plot saved → %s", save_path)
        return fig

    # ── Persistence ───────────────────────────────────────────────────────────

    def save_model(self, path=None):
        """Persist the trained model + scaler + label encoder to disk."""
        path = Path(path) if path else config.MODELS_DIR / f"{self.algorithm}_ids.pkl"
        payload = dict(model=self.model, scaler=self.scaler,
                       label_encoder=self.label_encoder,
                       feature_names=self.feature_names)
        joblib.dump(payload, path)
        print(f"  💾 Model saved → {path}")
        return path

    def load_model(self, path=None):
        """Load a previously persisted model from disk."""
        path = Path(path) if path else config.MODELS_DIR / f"{self.algorithm}_ids.pkl"
        payload = joblib.load(path)
        self.model         = payload['model']
        self.scaler        = payload['scaler']
        self.label_encoder = payload['label_encoder']
        self.feature_names = payload['feature_names']
        print(f"  📂 Model loaded ← {path}")


# ══════════════════════════════════════════════════════════════════════════════
# Synthetic Data Generator (fallback if NSL-KDD unavailable)
# ══════════════════════════════════════════════════════════════════════════════

def generate_synthetic_network_traffic(n_samples: int = 10000,
                                        attack_ratio: float = 0.3) -> pd.DataFrame:
    """Generate labelled synthetic network traffic (normal / attack)."""
    print(f"\n⚙  Generating {n_samples:,} synthetic samples "
          f"({attack_ratio*100:.0f}% attacks)...")
    np.random.seed(config.RANDOM_STATE)
    n_atk = int(n_samples * attack_ratio)
    n_nrm = n_samples - n_atk

    def _make(n, kind):
        if kind == 'normal':
            return dict(
                duration=np.random.exponential(10, n),
                src_bytes=np.random.lognormal(7, 2, n),
                dst_bytes=np.random.lognormal(7, 2, n),
                wrong_fragment=np.random.poisson(0.1, n),
                urgent=np.random.poisson(0.05, n),
                hot=np.random.poisson(0.5, n),
                num_failed_logins=np.zeros(n),
                logged_in=np.ones(n),
                num_compromised=np.zeros(n),
                root_shell=np.zeros(n),
                su_attempted=np.zeros(n),
                num_root=np.random.poisson(0.2, n),
                num_file_creations=np.random.poisson(1, n),
                num_shells=np.random.poisson(0.1, n),
                num_access_files=np.random.poisson(0.5, n),
                count=np.random.poisson(5, n),
                srv_count=np.random.poisson(5, n),
                label=['normal'] * n,
            )
        else:
            return dict(
                duration=np.random.exponential(50, n),
                src_bytes=np.random.lognormal(10, 3, n),
                dst_bytes=np.random.lognormal(5, 3, n),
                wrong_fragment=np.random.poisson(2, n),
                urgent=np.random.poisson(1, n),
                hot=np.random.poisson(3, n),
                num_failed_logins=np.random.poisson(2, n),
                logged_in=np.random.binomial(1, 0.3, n),
                num_compromised=np.random.poisson(1, n),
                root_shell=np.random.binomial(1, 0.2, n),
                su_attempted=np.random.binomial(1, 0.3, n),
                num_root=np.random.poisson(2, n),
                num_file_creations=np.random.poisson(5, n),
                num_shells=np.random.poisson(1, n),
                num_access_files=np.random.poisson(3, n),
                count=np.random.poisson(20, n),
                srv_count=np.random.poisson(15, n),
                label=['attack'] * n,
            )

    df = pd.concat([pd.DataFrame(_make(n_nrm, 'normal')),
                    pd.DataFrame(_make(n_atk, 'attack'))],
                   ignore_index=True)
    df = df.sample(frac=1, random_state=config.RANDOM_STATE).reset_index(drop=True)

    for lbl in ('normal', 'attack'):
        n = (df['label'] == lbl).sum()
        print(f"  {lbl:8s}: {n:,} ({n/len(df)*100:.1f}%)")
    return df


# ══════════════════════════════════════════════════════════════════════════════
# Algorithm Comparison
# ══════════════════════════════════════════════════════════════════════════════

def compare_algorithms(X_train, y_train, X_test, y_test) -> dict:
    """Train all three algorithms and return comparison results."""
    results = {}
    print("\n" + "="*70)
    print("  COMPARING ML ALGORITHMS")
    print("="*70)

    for algo in IntrusionDetectionSystem.ALGORITHMS:
        ids = IntrusionDetectionSystem(algorithm=algo)
        ids.train(X_train, y_train)
        metrics, y_pred = ids.evaluate(X_test, y_test)
        ids.print_evaluation_report(y_test, y_pred, metrics)
        ids.save_model()
        results[algo] = {'metrics': metrics, 'model': ids, 'y_pred': y_pred}

    return results


def plot_algorithm_comparison(results: dict, save_path=None):
    """4-panel bar chart comparing accuracy, precision, recall, F1."""
    try:
        plt.style.use(config.PLOT_STYLE)
    except Exception:
        pass

    algos  = list(results.keys())
    mnames = ['accuracy', 'precision', 'recall', 'f1_score']
    colors = config.PALETTE[:len(algos)]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Algorithm Comparison — Performance Metrics',
                 fontsize=16, fontweight='bold', y=1.01)

    for idx, metric in enumerate(mnames):
        ax  = axes[idx // 2, idx % 2]
        vals = [results[a]['metrics'][metric] for a in algos]
        bars = ax.bar([a.replace('_', '\n') for a in algos], vals,
                      color=colors, alpha=0.85, edgecolor='white', linewidth=1.2)
        ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=12)
        ax.set_ylim(0, 1.12)
        ax.grid(axis='y', alpha=0.4)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f'{val:.3f}', ha='center', va='bottom',
                    fontweight='bold', fontsize=10)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=config.DPI, bbox_inches='tight')
        logger.info("Algorithm comparison saved → %s", save_path)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("\n" + "="*70)
    print("  AI-BASED INTRUSION DETECTION SYSTEM")
    print("  Dataset: NSL-KDD  |  Models: RF, DT, MLP")
    print("="*70)

    # ── Load dataset ──────────────────────────────────────────────────────────
    try:
        from data_loader import load_dataset
        X_train, X_test, y_train, y_test, source = load_dataset(binary=True)
    except Exception as exc:
        logger.warning("data_loader failed (%s), using synthetic data.", exc)
        df = generate_synthetic_network_traffic(
            config.N_SAMPLES_SYNTHETIC, config.ATTACK_RATIO)
        X = df.drop('label', axis=1)
        y = df['label']
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=config.TEST_SIZE,
            random_state=config.RANDOM_STATE, stratify=y)
        source = "Synthetic"

    print(f"\n  Dataset source : {source}")
    print(f"  Training set   : {len(X_train):,} samples")
    print(f"  Test set       : {len(X_test):,} samples")

    # ── Cross-validation on Random Forest ─────────────────────────────────────
    rf_ids = IntrusionDetectionSystem('random_forest')
    rf_ids.cross_validate(X_train, y_train)

    # ── Train & compare all algorithms ────────────────────────────────────────
    results = compare_algorithms(X_train, y_train, X_test, y_test)

    # ── Plots ─────────────────────────────────────────────────────────────────
    plot_algorithm_comparison(
        results, save_path=config.DOCS_DIR / 'algorithm_comparison.png')

    best = results['random_forest']['model']
    best.plot_confusion_matrix(
        y_test, results['random_forest']['y_pred'],
        save_path=config.DOCS_DIR / 'confusion_matrix_rf.png')
    best.plot_feature_importance(
        save_path=config.DOCS_DIR / 'feature_importance_rf.png')

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("  PERFORMANCE RANKING")
    print("="*70)
    for rank, (algo, res) in enumerate(
            sorted(results.items(),
                   key=lambda x: x[1]['metrics']['accuracy'],
                   reverse=True), 1):
        m = res['metrics']
        print(f"  {rank}. {algo.upper().replace('_',' '):<22s}"
              f"Acc={m['accuracy']:.4f}  F1={m['f1_score']:.4f}  "
              f"Train={m['training_time']:.3f}s")

    print("\n  ✅ Intrusion Detection complete.")
    print("="*70)


if __name__ == "__main__":
    main()
