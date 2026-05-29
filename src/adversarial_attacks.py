"""
Adversarial Attacks on AI-Based Intrusion Detection Systems.

Improvements over v1
---------------------
* pathlib for all file-system paths (project root config)
* Python logging throughout
* Professional plot aesthetics (seaborn-v0_8-darkgrid, custom palette)
* Uses config for hyperparameters (RANDOM_STATE, TEST_SIZE, …)
* main() loads NSL-KDD via data_loader, falls back to synthetic data
* plot_adversarial_comparison() returns Figure as well as saving to disk
"""

import sys
import logging
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

warnings.filterwarnings("ignore")

# ── Make sure the project root is on sys.path so config is importable ─────────
_SRC_DIR  = Path(__file__).parent
_ROOT_DIR = _SRC_DIR.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

import config  # noqa: E402

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
class AdversarialAttackSimulator:
    """
    Simulates common adversarial perturbations on network-traffic feature vectors.

    Parameters
    ----------
    model  : trained sklearn classifier with .predict()
    scaler : fitted StandardScaler (or compatible) used before prediction
    """

    def __init__(self, model, scaler):
        self.model  = model
        self.scaler = scaler
        logger.info("AdversarialAttackSimulator initialised — model=%s", type(model).__name__)

    # ── Attack primitives ─────────────────────────────────────────────────────

    def fgsm_attack(self, X: np.ndarray, epsilon: float = 0.1) -> np.ndarray:
        """
        Fast Gradient Sign Method (approximate, sign taken from random gradient
        direction since we target a black-box model).
        """
        perturbation    = np.sign(np.random.randn(*X.shape)) * epsilon
        X_adversarial   = X + perturbation
        return np.maximum(X_adversarial, 0)

    def random_noise_attack(self, X: np.ndarray, noise_level: float = 0.05) -> np.ndarray:
        """Multiplicative Gaussian noise (simulates sensor jitter)."""
        noise  = np.random.normal(0, noise_level, X.shape)
        X_noisy = X + X * noise
        return np.maximum(X_noisy, 0)

    def feature_manipulation_attack(
        self,
        X: np.ndarray,
        feature_indices: list[int],
        manipulation_factor: float = 0.5,
    ) -> np.ndarray:
        """Scale selected features by *manipulation_factor* (mimics evasion by an attacker
        who knows which features the IDS monitors)."""
        X_manipulated = X.copy()
        for idx in feature_indices:
            X_manipulated[:, idx] *= manipulation_factor
        return X_manipulated

    # ── Robustness evaluation ─────────────────────────────────────────────────

    def evaluate_robustness(
        self,
        X_test,
        y_test,
        attack_type: str = "fgsm",
        **kwargs,
    ) -> dict:
        """
        Evaluate how well the model withstands a given adversarial attack.

        Returns a dict with:
            attack_type, original_accuracy, adversarial_accuracy,
            accuracy_drop, evasion_rate, successful_evasions, total_samples
        """
        if isinstance(X_test, pd.DataFrame):
            X_test_np = X_test.values
        else:
            X_test_np = np.asarray(X_test)

        X_test_scaled = self.scaler.transform(X_test_np)
        y_pred_original = self.model.predict(X_test_scaled)

        # ── Generate adversarial samples ──────────────────────────────────────
        if attack_type == "fgsm":
            epsilon      = kwargs.get("epsilon", 0.1)
            X_adversarial = self.fgsm_attack(X_test_np, epsilon)
            logger.info("FGSM attack — epsilon=%.3f", epsilon)
        elif attack_type == "random_noise":
            noise_level   = kwargs.get("noise_level", 0.05)
            X_adversarial = self.random_noise_attack(X_test_np, noise_level)
            logger.info("Random noise attack — noise_level=%.3f", noise_level)
        elif attack_type == "feature_manipulation":
            feature_indices    = kwargs.get("feature_indices", [0, 1, 2])
            manipulation_factor = kwargs.get("manipulation_factor", 0.5)
            X_adversarial       = self.feature_manipulation_attack(
                X_test_np, feature_indices, manipulation_factor
            )
            logger.info(
                "Feature manipulation attack — features=%s  factor=%.3f",
                feature_indices, manipulation_factor,
            )
        else:
            raise ValueError(f"Unknown attack type: {attack_type!r}")

        X_adv_scaled    = self.scaler.transform(X_adversarial)
        y_pred_adv      = self.model.predict(X_adv_scaled)

        y_test_arr      = np.asarray(y_test)
        original_acc    = np.mean(y_pred_original == y_test_arr)
        adversarial_acc = np.mean(y_pred_adv      == y_test_arr)
        pred_changes    = np.sum(y_pred_original != y_pred_adv)
        evasion_rate    = pred_changes / len(y_test_arr)

        # Successful evasion = was correctly classified → now wrong
        correct_before  = y_pred_original == y_test_arr
        wrong_after     = y_pred_adv      != y_test_arr
        successful_evas = int(np.sum(correct_before & wrong_after))

        result = {
            "attack_type":          attack_type,
            "original_accuracy":    float(original_acc),
            "adversarial_accuracy": float(adversarial_acc),
            "accuracy_drop":        float(original_acc - adversarial_acc),
            "evasion_rate":         float(evasion_rate),
            "successful_evasions":  successful_evas,
            "total_samples":        int(len(y_test_arr)),
        }
        logger.info(
            "%s → orig_acc=%.4f  adv_acc=%.4f  drop=%.4f  evasion=%.4f",
            attack_type, original_acc, adversarial_acc,
            original_acc - adversarial_acc, evasion_rate,
        )
        return result

    def print_robustness_report(self, results: dict) -> None:
        """Pretty-print a single attack robustness result."""
        print(f"\n{'─'*42}")
        print(f"  Attack type          : {results['attack_type']}")
        print(f"  Original Accuracy    : {results['original_accuracy']:.4f}")
        print(f"  Adversarial Accuracy : {results['adversarial_accuracy']:.4f}")
        print(f"  Accuracy Drop        : {results['accuracy_drop']:.4f}")
        print(f"  Evasion Rate         : {results['evasion_rate']:.4f}")
        print(f"  Successful Evasions  : {results['successful_evasions']} / {results['total_samples']}")
        print(f"{'─'*42}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# Public helper functions
# ═══════════════════════════════════════════════════════════════════════════════

def plot_adversarial_comparison(
    all_results: list[dict],
    save_dir: Path | str | None = None,
) -> plt.Figure:
    """
    Grouped bar chart + accuracy-drop line comparing multiple adversarial attacks.

    Parameters
    ----------
    all_results : list of dicts returned by evaluate_robustness()
    save_dir    : directory to save the PNG (default: config.DOCS_DIR)

    Returns
    -------
    matplotlib Figure
    """
    if save_dir is None:
        save_dir = getattr(config, "DOCS_DIR", _ROOT_DIR / "docs")
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    attack_labels   = [r["attack_type"].replace("_", " ").title() for r in all_results]
    original_accs   = [r["original_accuracy"]    for r in all_results]
    adversarial_accs = [r["adversarial_accuracy"] for r in all_results]
    accuracy_drops  = [r["accuracy_drop"]         for r in all_results]
    evasion_rates   = [r["evasion_rate"]           for r in all_results]

    x     = np.arange(len(attack_labels))
    width = 0.30

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Adversarial Robustness Analysis", fontsize=15, fontweight="bold", y=1.02)

    # ── Left: accuracy comparison ─────────────────────────────────────────────
    ax = axes[0]
    bars_orig = ax.bar(x - width / 2, original_accs,   width, label="Original",   color=_PALETTE[0], alpha=0.88, edgecolor="white")
    bars_adv  = ax.bar(x + width / 2, adversarial_accs, width, label="Adversarial", color=_PALETTE[1], alpha=0.88, edgecolor="white")

    for bars in (bars_orig, bars_adv):
        for bar in bars:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.008,
                f"{bar.get_height():.3f}",
                ha="center", va="bottom", fontsize=8.5, fontweight="bold",
            )

    ax.set_xticks(x)
    ax.set_xticklabels(attack_labels, fontsize=10, rotation=12)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Accuracy", fontsize=12)
    ax.set_title("Accuracy: Original vs Adversarial", fontsize=12, fontweight="bold")
    ax.legend(fontsize=10, framealpha=0.85)
    ax.grid(axis="y", alpha=0.4)

    # ── Right: accuracy drop & evasion rate ───────────────────────────────────
    ax2 = axes[1]
    ax2.bar(x - width / 2, accuracy_drops, width, label="Accuracy Drop", color=_PALETTE[2], alpha=0.88, edgecolor="white")
    ax2.bar(x + width / 2, evasion_rates,  width, label="Evasion Rate",  color=_PALETTE[3], alpha=0.88, edgecolor="white")

    ax2.plot(x - width / 2, accuracy_drops, "o--", color=_PALETTE[2], lw=1.8, ms=7)
    ax2.plot(x + width / 2, evasion_rates,  "s--", color=_PALETTE[3], lw=1.8, ms=7)

    ax2.set_xticks(x)
    ax2.set_xticklabels(attack_labels, fontsize=10, rotation=12)
    ax2.set_ylim(0, max(max(accuracy_drops), max(evasion_rates)) * 1.35 + 0.05)
    ax2.set_ylabel("Rate", fontsize=12)
    ax2.set_title("Accuracy Drop & Evasion Rate", fontsize=12, fontweight="bold")
    ax2.legend(fontsize=10, framealpha=0.85)
    ax2.grid(axis="y", alpha=0.4)

    fig.tight_layout()

    out_path = save_dir / "adversarial_comparison.png"
    fig.savefig(out_path, dpi=_DPI, bbox_inches="tight")
    logger.info("Adversarial comparison plot saved → %s", out_path)
    return fig


def plot_perturbation_effect(
    X_original: np.ndarray,
    X_adversarial: np.ndarray,
    feature_names: list[str] | None = None,
    n_features: int = 10,
    save_dir: Path | str | None = None,
) -> plt.Figure:
    """
    Violin / box plot showing the distribution shift per feature after perturbation.

    Returns the Figure.
    """
    if save_dir is None:
        save_dir = getattr(config, "DOCS_DIR", _ROOT_DIR / "docs")
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    n_features = min(n_features, X_original.shape[1])
    feature_names = feature_names or [f"F{i}" for i in range(n_features)]

    diffs = np.abs(X_adversarial[:, :n_features] - X_original[:, :n_features])
    df    = pd.DataFrame(diffs, columns=feature_names[:n_features])
    df_m  = df.melt(var_name="Feature", value_name="Absolute Perturbation")

    fig, ax = plt.subplots(figsize=(12, 5))
    sns.boxplot(data=df_m, x="Feature", y="Absolute Perturbation",
                palette=_PALETTE * (n_features // len(_PALETTE) + 1), ax=ax,
                flierprops={"marker": ".", "markersize": 3})
    ax.set_title("Feature-level Perturbation Effect", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Feature", fontsize=11)
    ax.set_ylabel("Absolute Perturbation", fontsize=11)
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()

    out_path = save_dir / "perturbation_effect.png"
    fig.savefig(out_path, dpi=_DPI, bbox_inches="tight")
    logger.info("Perturbation effect plot saved → %s", out_path)
    return fig


# ═══════════════════════════════════════════════════════════════════════════════
# High-level demo function (public API)
# ═══════════════════════════════════════════════════════════════════════════════

def demonstrate_adversarial_attacks(
    model,
    scaler,
    X_test,
    y_test,
    docs_dir: Path | str | None = None,
) -> list[dict]:
    """
    Run all three attack types against *model* and produce comparison plots.

    Parameters
    ----------
    model, scaler  : trained classifier + its scaler
    X_test, y_test : evaluation data
    docs_dir       : where to save plots (default: config.DOCS_DIR)

    Returns
    -------
    list of robustness result dicts
    """
    if docs_dir is None:
        docs_dir = getattr(config, "DOCS_DIR", _ROOT_DIR / "docs")
    docs_dir = Path(docs_dir)

    simulator   = AdversarialAttackSimulator(model, scaler)
    attack_cfgs = [
        ("fgsm",                 {"epsilon": 0.1}),
        ("random_noise",         {"noise_level": 0.05}),
        ("feature_manipulation", {"feature_indices": list(range(min(5, np.array(X_test).shape[1]))),
                                  "manipulation_factor": 0.5}),
    ]

    all_results = []
    for attack_type, kwargs in attack_cfgs:
        logger.info("Running %s attack …", attack_type)
        result = simulator.evaluate_robustness(X_test, y_test, attack_type=attack_type, **kwargs)
        simulator.print_robustness_report(result)
        all_results.append(result)

    fig = plot_adversarial_comparison(all_results, save_dir=docs_dir)

    # Perturbation effect for FGSM
    X_np   = np.asarray(X_test)
    X_fgsm = simulator.fgsm_attack(X_np, epsilon=0.1)
    plot_perturbation_effect(X_np, X_fgsm, save_dir=docs_dir)

    return all_results


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

def _generate_synthetic_data(
    n_samples: int = 2000,
    n_features: int = 20,
) -> tuple[np.ndarray, np.ndarray]:
    """Synthetic network-traffic data: label 0 = normal, 1 = attack."""
    rng      = np.random.default_rng(getattr(config, "RANDOM_STATE", 42))
    n_attack = n_samples // 4
    n_normal = n_samples - n_attack

    X_normal = rng.normal(0.0, 1.0, (n_normal,  n_features))
    X_attack = rng.normal(3.5, 1.5, (n_attack,  n_features))
    X        = np.vstack([X_normal, X_attack])
    y        = np.hstack([np.zeros(n_normal), np.ones(n_attack)]).astype(int)

    idx = rng.permutation(len(y))
    return X[idx], y[idx]


def main():
    logger.info("=" * 60)
    logger.info("Adversarial Attacks — starting")
    logger.info("=" * 60)

    docs_dir = getattr(config, "DOCS_DIR", _ROOT_DIR / "docs")
    random_state = getattr(config, "RANDOM_STATE", 42)
    Path(docs_dir).mkdir(parents=True, exist_ok=True)

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
        
        test_size    = getattr(config, "TEST_SIZE", 0.20)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

    # ── 3. Train a reference classifier ───────────────────────────────────────
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=random_state,
        n_jobs=getattr(config, "N_JOBS", -1),
    )
    model.fit(X_train_s, y_train)
    base_acc = accuracy_score(y_test, model.predict(X_test_s))
    logger.info("Reference model accuracy: %.4f", base_acc)

    # ── 4. Demonstrate attacks ────────────────────────────────────────────────
    # Note: pass the *unscaled* X_test; AdversarialAttackSimulator applies scaler internally.
    results = demonstrate_adversarial_attacks(model, scaler, X_test, y_test, docs_dir=docs_dir)

    logger.info("Adversarial Attacks — done.")
    plt.show()
    return results


if __name__ == "__main__":
    main()
