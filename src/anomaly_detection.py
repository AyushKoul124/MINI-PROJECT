"""
Anomaly Detection for Network Traffic
Using unsupervised learning approaches (IsolationForest & OneClassSVM).

Improvements over v1
---------------------
* pathlib for all file-system paths (config at project root)
* Python logging throughout
* Professional plot aesthetics (seaborn-v0_8-darkgrid, custom palette)
* Cross-validation support in compare_anomaly_methods()
* main() loads NSL-KDD via data_loader, falls back to synthetic data
* Model persistence via joblib (save_model / load_model)
* Plot functions return their Figure objects as well as saving to disk
"""

import sys
import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

# ── Make sure the project root is on sys.path so config is importable ─────────
_SRC_DIR  = Path(__file__).parent
_ROOT_DIR = _SRC_DIR.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

import config  # noqa: E402  (project-level config)

# ── Logger ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Plot defaults ─────────────────────────────────────────────────────────────
try:
    plt.style.use(config.PLOT_STYLE)
except OSError:
    plt.style.use("seaborn-v0_8-darkgrid")

_PALETTE = getattr(config, "COLOR_PALETTE", ["#6C63FF", "#FF6584", "#43D8C9", "#FFC857"])
_DPI     = getattr(config, "FIGURE_DPI", 150)


# ═══════════════════════════════════════════════════════════════════════════════
class AnomalyDetector:
    """
    Wraps IsolationForest or OneClassSVM with a consistent sklearn-like API.

    Parameters
    ----------
    method        : 'isolation_forest' | 'one_class_svm'
    contamination : expected fraction of outliers in training data
    """

    def __init__(self, method: str = "isolation_forest", contamination: float | None = None):
        self.method = method
        self.contamination = contamination or getattr(config, "IF_CONTAMINATION", 0.10)
        self.scaler = StandardScaler()
        random_state = getattr(config, "RANDOM_STATE", 42)

        if method == "isolation_forest":
            self.model = IsolationForest(
                contamination=self.contamination,
                random_state=random_state,
                n_estimators=100,
            )
        elif method == "one_class_svm":
            nu = getattr(config, "OC_SVM_NU", self.contamination)
            self.model = OneClassSVM(nu=nu, kernel="rbf", gamma="auto")
        else:
            raise ValueError(f"Unknown method: {method!r}")

        logger.info("AnomalyDetector initialised — method=%s  contamination=%.3f", method, self.contamination)

    # ── Fit / predict ──────────────────────────────────────────────────────────
    def fit(self, X):
        logger.debug("Fitting scaler + model on %d samples, %d features", *np.array(X).shape[:2] if np.array(X).ndim > 1 else (len(X), 1))
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        logger.info("Model fit complete.")
        return self

    def predict(self, X):
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def decision_function(self, X):
        X_scaled = self.scaler.transform(X)
        return self.model.decision_function(X_scaled)

    # ── Evaluation ────────────────────────────────────────────────────────────
    def evaluate(self, X_test, y_test_binary):
        """
        Returns (metrics_dict, y_pred) where y_pred uses {0: normal, 1: anomaly}.
        """
        predictions = self.predict(X_test)
        y_pred = np.where(predictions == -1, 1, 0)
        scores  = self.decision_function(X_test)

        tn, fp, fn, tp = confusion_matrix(y_test_binary, y_pred).ravel()
        accuracy  = (tp + tn) / (tp + tn + fp + fn)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1        = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        try:
            auc = roc_auc_score(y_test_binary, -scores)
        except Exception:
            auc = 0.0

        metrics = {
            "accuracy":        accuracy,
            "precision":       precision,
            "recall":          recall,
            "f1_score":        f1,
            "auc":             auc,
            "true_positives":  int(tp),
            "false_positives": int(fp),
            "true_negatives":  int(tn),
            "false_negatives": int(fn),
        }
        logger.info(
            "Evaluation — acc=%.4f  prec=%.4f  rec=%.4f  f1=%.4f  auc=%.4f",
            accuracy, precision, recall, f1, auc,
        )
        return metrics, y_pred

    # ── Persistence ───────────────────────────────────────────────────────────
    def save_model(self, path: Path | str | None = None) -> Path:
        """Persist scaler + model bundle to *path* (default: MODELS_DIR/<method>.joblib)."""
        if path is None:
            models_dir = getattr(config, "MODELS_DIR", _ROOT_DIR / "models")
            Path(models_dir).mkdir(parents=True, exist_ok=True)
            path = Path(models_dir) / f"anomaly_{self.method}.joblib"
        path = Path(path)
        bundle = {"scaler": self.scaler, "model": self.model, "method": self.method,
                  "contamination": self.contamination}
        joblib.dump(bundle, path)
        logger.info("Model saved → %s", path)
        return path

    @classmethod
    def load_model(cls, path: Path | str) -> "AnomalyDetector":
        """Load a previously saved AnomalyDetector from *path*."""
        path = Path(path)
        bundle = joblib.load(path)
        obj = cls.__new__(cls)
        obj.scaler        = bundle["scaler"]
        obj.model         = bundle["model"]
        obj.method        = bundle["method"]
        obj.contamination = bundle["contamination"]
        logger.info("Model loaded ← %s  (method=%s)", path, obj.method)
        return obj


# ═══════════════════════════════════════════════════════════════════════════════
# Public helper functions
# ═══════════════════════════════════════════════════════════════════════════════

def compare_anomaly_methods(
    X_train,
    X_test,
    y_test,
    cv_folds: int = 0,
) -> dict[str, dict]:
    """
    Train both detectors and compare their metrics on the test set.

    Parameters
    ----------
    X_train, X_test : array-like feature matrices
    y_test          : binary labels (1 = anomaly)
    cv_folds        : if > 1, also run StratifiedKFold CV on X_test / y_test
                      and report mean ± std F1 for each method.

    Returns
    -------
    dict  {method_name: metrics_dict}
    """
    logger.info("Comparing anomaly detection methods …")
    results: dict[str, dict] = {}
    methods = ["isolation_forest", "one_class_svm"]

    for method in methods:
        logger.info("  Training %s …", method)
        detector = AnomalyDetector(method=method)
        detector.fit(X_train)
        metrics, _ = detector.evaluate(X_test, y_test)
        results[method] = {'metrics': metrics, 'detector': detector}

        # optional cross-validation
        if cv_folds > 1:
            skf = StratifiedKFold(n_splits=cv_folds, shuffle=True,
                                  random_state=getattr(config, "RANDOM_STATE", 42))
            X_all = np.vstack([X_train, X_test])
            y_all = np.hstack([np.zeros(len(X_train)), y_test])
            cv_f1s = []
            for train_idx, val_idx in skf.split(X_all, y_all):
                d = AnomalyDetector(method=method)
                d.fit(X_all[train_idx])
                m, _ = d.evaluate(X_all[val_idx], y_all[val_idx])
                cv_f1s.append(m["f1_score"])
            results[method]['metrics']["cv_f1_mean"] = float(np.mean(cv_f1s))
            results[method]['metrics']["cv_f1_std"]  = float(np.std(cv_f1s))
            logger.info(
                "  %s CV(%d) F1: %.4f ± %.4f",
                method, cv_folds, results[method]['metrics']["cv_f1_mean"], results[method]['metrics']["cv_f1_std"],
            )

    # ── Pretty comparison table ────────────────────────────────────────────
    header = f"{'Method':<22}{'Accuracy':>10}{'Precision':>11}{'Recall':>9}{'F1':>9}{'AUC':>9}"
    sep    = "─" * len(header)
    print(f"\n{sep}\n{header}\n{sep}")
    for method, res_dict in results.items():
        m = res_dict['metrics']
        label = method.replace("_", " ").title()
        row = (
            f"{label:<22}{m['accuracy']:>10.4f}{m['precision']:>11.4f}"
            f"{m['recall']:>9.4f}{m['f1_score']:>9.4f}{m['auc']:>9.4f}"
        )
        if "cv_f1_mean" in m:
            row += f"  CV-F1={m['cv_f1_mean']:.4f}±{m['cv_f1_std']:.4f}"
        print(row)
    print(sep + "\n")

    return results


def plot_anomaly_comparison(
    results: dict,
    save_dir: Path | str | None = None,
) -> plt.Figure:
    """
    Bar chart comparing Isolation Forest vs One-Class SVM across key metrics.

    Returns the matplotlib Figure object (also saves to *save_dir* if provided).
    """
    if save_dir is None:
        save_dir = getattr(config, "DOCS_DIR", _ROOT_DIR / "docs")
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    metrics_to_plot = ["accuracy", "precision", "recall", "f1_score", "auc"]
    method_labels   = [k.replace("_", " ").title() for k in results]
    x               = np.arange(len(metrics_to_plot))
    width           = 0.35

    fig, ax = plt.subplots(figsize=(11, 6))
    for i, (method, label) in enumerate(zip(results, method_labels)):
        m = results[method]['metrics']
        vals = [m.get(met, 0) for met in metrics_to_plot]
        bars = ax.bar(x + i * width, vals, width, label=label,
                      color=_PALETTE[i % len(_PALETTE)], alpha=0.88,
                      edgecolor="white", linewidth=0.8)
        for bar, val in zip(bars, vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.012,
                f"{val:.3f}",
                ha="center", va="bottom",
                fontsize=8.5, fontweight="bold",
            )

    ax.set_xticks(x + width / 2)
    ax.set_xticklabels([m.replace("_", " ").title() for m in metrics_to_plot], fontsize=11)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Score", fontsize=12)
    ax.set_title("Anomaly Detection — Method Comparison", fontsize=14, fontweight="bold", pad=14)
    ax.legend(fontsize=11, framealpha=0.85)
    ax.grid(axis="y", alpha=0.4)
    fig.tight_layout()

    out_path = save_dir / "anomaly_comparison.png"
    fig.savefig(out_path, dpi=_DPI, bbox_inches="tight")
    logger.info("Comparison plot saved → %s", out_path)
    return fig


def plot_roc_curves(
    detectors: list[tuple[str, AnomalyDetector]],
    X_test,
    y_test,
    save_dir: Path | str | None = None,
) -> plt.Figure:
    """
    Overlay ROC curves for a list of (label, AnomalyDetector) pairs.

    Returns the Figure.
    """
    if save_dir is None:
        save_dir = getattr(config, "DOCS_DIR", _ROOT_DIR / "docs")
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    for idx, (label, detector) in enumerate(detectors):
        scores = -detector.decision_function(X_test)
        try:
            fpr, tpr, _ = roc_curve(y_test, scores)
            auc_val     = roc_auc_score(y_test, scores)
            ax.plot(fpr, tpr, color=_PALETTE[idx % len(_PALETTE)], lw=2.2,
                    label=f"{label}  (AUC = {auc_val:.3f})")
        except Exception as exc:
            logger.warning("Could not compute ROC for %s: %s", label, exc)

    ax.plot([0, 1], [0, 1], "k--", lw=1.2, alpha=0.5, label="Random")
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC Curves — Anomaly Detectors", fontsize=14, fontweight="bold", pad=14)
    ax.legend(fontsize=11, framealpha=0.85)
    fig.tight_layout()

    out_path = save_dir / "roc_curves.png"
    fig.savefig(out_path, dpi=_DPI, bbox_inches="tight")
    logger.info("ROC curve plot saved → %s", out_path)
    return fig


def plot_decision_boundary(
    detector: AnomalyDetector,
    X,
    y,
    feature_indices: tuple[int, int] = (0, 1),
    save_dir: Path | str | None = None,
) -> plt.Figure:
    """
    2-D scatter of two features coloured by anomaly score, with decision boundary.

    Returns the Figure.
    """
    if save_dir is None:
        save_dir = getattr(config, "DOCS_DIR", _ROOT_DIR / "docs")
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    fi, fj = feature_indices
    X_2d   = np.array(X)[:, [fi, fj]]

    x_min, x_max = X_2d[:, 0].min() - 1, X_2d[:, 0].max() + 1
    y_min, y_max = X_2d[:, 1].min() - 1, X_2d[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, 300),
                          np.linspace(y_min, y_max, 300))

    # Use the full-dimensional scaler; pad extra dims with zeros
    n_features = detector.scaler.n_features_in_
    grid_full  = np.zeros((xx.ravel().shape[0], n_features))
    grid_full[:, fi] = xx.ravel()
    grid_full[:, fj] = yy.ravel()

    Z = detector.decision_function(grid_full).reshape(xx.shape)

    fig, ax = plt.subplots(figsize=(9, 6))
    contour = ax.contourf(xx, yy, Z, levels=20, cmap="RdYlGn", alpha=0.55)
    plt.colorbar(contour, ax=ax, label="Anomaly Score")
    ax.contour(xx, yy, Z, levels=[0], colors="white", linewidths=2, linestyles="--")

    y_arr    = np.asarray(y)
    is_anom  = y_arr == 1
    ax.scatter(X_2d[~is_anom, 0], X_2d[~is_anom, 1],
               c=_PALETTE[0], s=18, alpha=0.65, label="Normal", edgecolors="none")
    ax.scatter(X_2d[is_anom, 0], X_2d[is_anom, 1],
               c=_PALETTE[1], s=28, alpha=0.85, label="Anomaly",
               marker="^", edgecolors="white", linewidths=0.5)

    ax.set_xlabel(f"Feature {fi}", fontsize=12)
    ax.set_ylabel(f"Feature {fj}", fontsize=12)
    ax.set_title(f"Decision Boundary — {detector.method.replace('_', ' ').title()}",
                 fontsize=14, fontweight="bold", pad=14)
    ax.legend(fontsize=11, framealpha=0.85)
    fig.tight_layout()

    out_path = save_dir / f"decision_boundary_{detector.method}.png"
    fig.savefig(out_path, dpi=_DPI, bbox_inches="tight")
    logger.info("Decision boundary plot saved → %s", out_path)
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_synthetic_data(n_samples: int = 2000, n_features: int = 20, contamination: float = 0.10):
    """Generate labelled synthetic network-traffic data for demo purposes."""
    rng          = np.random.default_rng(getattr(config, "RANDOM_STATE", 42))
    n_anomalies  = int(n_samples * contamination)
    n_normal     = n_samples - n_anomalies

    X_normal  = rng.normal(0, 1,   (n_normal,    n_features))
    X_anomaly = rng.normal(4, 1.5, (n_anomalies, n_features))
    X         = np.vstack([X_normal, X_anomaly])
    y         = np.hstack([np.zeros(n_normal), np.ones(n_anomalies)]).astype(int)

    shuffle = rng.permutation(len(y))
    return X[shuffle], y[shuffle]


def main():
    logger.info("=" * 60)
    logger.info("Anomaly Detection — starting")
    logger.info("=" * 60)

    docs_dir   = getattr(config, "DOCS_DIR",   _ROOT_DIR / "docs")
    models_dir = getattr(config, "MODELS_DIR", _ROOT_DIR / "models")
    random_state = getattr(config, "RANDOM_STATE", 42)
    Path(docs_dir).mkdir(parents=True, exist_ok=True)
    Path(models_dir).mkdir(parents=True, exist_ok=True)

    # ── 1. Load data ──────────────────────────────────────────────────────────
    # ── 1. Load data & Train/Test split ───────────────────────────────────────
    try:
        from data_loader import load_dataset          # noqa: PLC0415

        logger.info("Attempting to load NSL-KDD via data_loader …")
        X_train, X_test, y_train_raw, y_test_raw, source = load_dataset(binary=True)
        
        y_train = np.array([1 if val == 'attack' or val == 1 else 0 for val in y_train_raw])
        y_test  = np.array([1 if val == 'attack' or val == 1 else 0 for val in y_test_raw])
        X_train = np.asarray(X_train, dtype=float)
        X_test  = np.asarray(X_test, dtype=float)
        
        logger.info("%s loaded — %d train, %d test samples", source, len(X_train), len(X_test))
    except Exception as exc:
        logger.warning("data_loader failed (%s); using synthetic data.", exc)
        logger.info("Generating synthetic data …")
        X, y = _generate_synthetic_data()
        
        from sklearn.model_selection import train_test_split
        test_size = getattr(config, "TEST_SIZE", 0.20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
    # Anomaly detectors train on normal traffic only
    X_train_normal = X_train[y_train == 0]
    
    # Subsample if too large to prevent OneClassSVM from hanging (O(n^3) complexity)
    max_train = 10000
    if len(X_train_normal) > max_train:
        np.random.seed(random_state)
        idx = np.random.choice(len(X_train_normal), max_train, replace=False)
        X_train_normal = X_train_normal[idx]
        
    logger.info("Train (normal): %d  |  Test: %d", len(X_train_normal), len(X_test))

    # ── 3. Compare methods ────────────────────────────────────────────────────
    results = compare_anomaly_methods(X_train_normal, X_test, y_test, cv_folds=0)  # disabled CV to save time

    # ── 4. Plots ──────────────────────────────────────────────────────────────
    fig_bar = plot_anomaly_comparison(results, save_dir=docs_dir)

    detectors = []
    for method in ("isolation_forest", "one_class_svm"):
        det = AnomalyDetector(method=method)
        det.fit(X_train_normal)
        det.save_model()
        detectors.append((method.replace("_", " ").title(), det))

    fig_roc = plot_roc_curves(detectors, X_test, y_test, save_dir=docs_dir)
    fig_db  = plot_decision_boundary(detectors[0][1], X_test, y_test, save_dir=docs_dir)

    logger.info("All plots saved to %s", docs_dir)
    logger.info("Anomaly Detection — done.")

    plt.show()
    return results


if __name__ == "__main__":
    main()
