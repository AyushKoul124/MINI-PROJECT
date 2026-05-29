"""
main.py — AI-Based Cybersecurity Project Entry Point
Usage:
    python main.py                        # Run all components
    python main.py --component intrusion  # Run specific component
    python main.py --component anomaly
    python main.py --component traffic
    python main.py --component adversarial
    python main.py --download-data        # Download NSL-KDD dataset only
"""
import sys
import argparse
import logging
import warnings
warnings.filterwarnings('ignore')

# ── Config & path setup ───────────────────────────────────────────────────────
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent))

import config

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger('main')


# ── Helpers ──────────────────────────────────────────────────────────────────

def banner(title: str):
    width = 72
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)


def section(title: str):
    print(f"\n{'─'*72}")
    print(f"  ▶  {title}")
    print(f"{'─'*72}")


# ── Components ────────────────────────────────────────────────────────────────

def run_download():
    """Download NSL-KDD dataset."""
    section("Downloading NSL-KDD Dataset")
    from data_loader import download_nsl_kdd
    ok = download_nsl_kdd()
    if ok:
        print("  ✅ Dataset ready.")
    else:
        print("  ⚠️  Download failed — components will use synthetic data.")


def run_intrusion():
    """Component 1 — Intrusion Detection (Supervised Learning)."""
    section("COMPONENT 1: Intrusion Detection System")
    print("  Models: Random Forest | Decision Tree | Neural Network")
    try:
        from intrusion_detection import main as ids_main
        ids_main()
    except Exception as exc:
        logger.error("Intrusion Detection failed: %s", exc, exc_info=True)
        print(f"  ❌ Error: {exc}")


def run_anomaly():
    """Component 2 — Anomaly Detection (Unsupervised Learning)."""
    section("COMPONENT 2: Anomaly Detection")
    print("  Methods: Isolation Forest | One-Class SVM")
    try:
        from anomaly_detection import main as anomaly_main
        anomaly_main()
    except Exception as exc:
        logger.error("Anomaly Detection failed: %s", exc, exc_info=True)
        print(f"  ❌ Error: {exc}")


def run_traffic():
    """Component 3 — Traffic Classification (Multi-Class)."""
    section("COMPONENT 3: Network Traffic Classification")
    print("  Classes: Normal | DoS | Probe | R2L | U2R")
    try:
        from traffic_classification import main as traffic_main
        traffic_main()
    except Exception as exc:
        logger.error("Traffic Classification failed: %s", exc, exc_info=True)
        print(f"  ❌ Error: {exc}")


def run_adversarial():
    """Component 4 — Adversarial Attacks Analysis."""
    section("COMPONENT 4: Adversarial Attacks")
    print("  Attacks: FGSM | Random Noise | Feature Manipulation")
    try:
        from adversarial_attacks import main as adv_main
        adv_main()
    except Exception as exc:
        logger.error("Adversarial Attacks failed: %s", exc, exc_info=True)
        print(f"  ❌ Error: {exc}")


# ── CLI ───────────────────────────────────────────────────────────────────────

COMPONENT_MAP = {
    'intrusion':   run_intrusion,
    'anomaly':     run_anomaly,
    'traffic':     run_traffic,
    'adversarial': run_adversarial,
}


def parse_args():
    parser = argparse.ArgumentParser(
        prog='main.py',
        description='AI-Based Cybersecurity Mini Project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Components:
  intrusion   — Binary IDS (RF, DT, MLP) with cross-validation
  anomaly     — Unsupervised anomaly detection (IF, OC-SVM)
  traffic     — 5-class traffic classification (Normal/DoS/Probe/R2L/U2R)
  adversarial — Adversarial robustness evaluation (FGSM, noise, manipulation)

Examples:
  python main.py                          # Run all
  python main.py --component intrusion    # Run one component
  python main.py --download-data          # Download NSL-KDD only
        """
    )
    parser.add_argument(
        '--component', '-c',
        choices=list(COMPONENT_MAP.keys()),
        default=None,
        help='Run a single component instead of all.'
    )
    parser.add_argument(
        '--download-data',
        action='store_true',
        help='Download the NSL-KDD dataset and exit.'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging.'
    )
    return parser.parse_args()


# ── Entry Point ───────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    banner("🛡  AI-BASED CYBERSECURITY MINI PROJECT")
    print("  Dataset    : NSL-KDD (real benchmark) with synthetic fallback")
    print("  Components : Intrusion Detection | Anomaly Detection |")
    print("               Traffic Classification | Adversarial Attacks")
    print(f"  Output dir : {config.DOCS_DIR}")
    print(f"  Models dir : {config.MODELS_DIR}")

    # ── Download only ─────────────────────────────────────────────────────────
    if args.download_data:
        run_download()
        return

    # ── Single component ──────────────────────────────────────────────────────
    if args.component:
        COMPONENT_MAP[args.component]()
    else:
        # ── All components ────────────────────────────────────────────────────
        run_intrusion()
        run_anomaly()
        run_traffic()
        run_adversarial()

    # ── Final summary ─────────────────────────────────────────────────────────
    banner("✅  PROJECT EXECUTION COMPLETE")
    print(f"  📊 Charts saved  → {config.DOCS_DIR}")
    print(f"  💾 Models saved  → {config.MODELS_DIR}")
    print("\n  Generated outputs:")
    for f in sorted(config.DOCS_DIR.glob('*.png')):
        print(f"    • {f.name}")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  ⏹  Interrupted by user.")
        sys.exit(0)
    except Exception as exc:
        logger.critical("Fatal error: %s", exc, exc_info=True)
        sys.exit(1)
