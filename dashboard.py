"""
🛡️ AI-Based Cybersecurity Dashboard
Streamlit front-end for the AI-Based Cybersecurity Mini-Project (Project 16)
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# ---------------------------------------------------------------------------
# Path setup – add project root and src/ to Python's module search path
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR      = os.path.join(PROJECT_ROOT, 'src')
for _path in (PROJECT_ROOT, SRC_DIR):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import streamlit as st
import matplotlib
matplotlib.use('Agg')          # non-interactive backend (required for Streamlit)
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Page configuration (must be the first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="🛡️ AI-Based Cybersecurity Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": "AI-Based Cybersecurity Dashboard – Project 16",
    },
)

# ---------------------------------------------------------------------------
# Global CSS – dark-friendly, premium look
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ---- Google Font ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* ---- Main background ---- */
    .stApp { background: linear-gradient(135deg, #0d1117 0%, #161b22 60%, #0d1117 100%); }

    /* ---- Top header strip ---- */
    .hero-banner {
        background: linear-gradient(90deg, #0f3460 0%, #16213e 40%, #1a1a2e 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 4px 30px rgba(0,0,0,0.5);
    }
    .hero-banner h1 {
        font-size: 2.1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #58a6ff, #79c0ff, #a5d6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 .4rem;
    }
    .hero-banner p { color: #8b949e; margin: 0; font-size: .95rem; }

    /* ---- Cards ---- */
    .metric-card {
        background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 1.4rem 1.6rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.4);
        transition: transform .2s, box-shadow .2s;
    }
    .metric-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(88,166,255,.15); }
    .metric-card .value {
        font-size: 2.4rem;
        font-weight: 700;
        color: #58a6ff;
        line-height: 1;
    }
    .metric-card .label { color: #8b949e; font-size: .85rem; margin-top: .45rem; }
    .metric-card .icon  { font-size: 1.8rem; margin-bottom: .3rem; }

    /* ---- Info / dataset card ---- */
    .info-card {
        background: linear-gradient(135deg, #0d2137 0%, #162032 100%);
        border-left: 4px solid #58a6ff;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
        color: #cdd9e5;
        font-size: .93rem;
        line-height: 1.65;
    }
    .info-card h4 { color: #79c0ff; margin: 0 0 .5rem; font-size: 1rem; }

    /* ---- Section headings ---- */
    .section-title {
        font-size: 1.35rem;
        font-weight: 600;
        color: #e6edf3;
        border-bottom: 2px solid #30363d;
        padding-bottom: .45rem;
        margin: 1.2rem 0 .9rem;
    }

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
        border-right: 1px solid #30363d;
    }
    .sidebar-footer {
        position: fixed;
        bottom: 1rem;
        left: 0;
        width: 17rem;
        text-align: center;
        font-size: .73rem;
        color: #484f58;
        padding: 0 1rem;
        line-height: 1.6;
    }

    /* ---- Buttons ---- */
    .stButton > button {
        background: linear-gradient(90deg, #1f6feb, #388bfd);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: .55rem 1.4rem;
        transition: opacity .15s;
    }
    .stButton > button:hover { opacity: .85; }

    /* ---- Tab styling ---- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: transparent;
        border-bottom: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px 6px 0 0;
        padding: .4rem .9rem;
        color: #8b949e;
        font-size: .88rem;
        background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: #1c2128 !important;
        color: #58a6ff !important;
        border-bottom: 2px solid #58a6ff !important;
    }

    /* ---- Matplotlib figure frames ---- */
    .stPlotlyChart, iframe, canvas { border-radius: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Lazy-import helpers with user-friendly error messages
# ---------------------------------------------------------------------------
_import_errors = {}

def _try_import(module_name, alias=None):
    """Return the imported module, or None on failure (stores the error)."""
    key = alias or module_name
    try:
        import importlib
        mod = importlib.import_module(module_name)
        return mod
    except Exception as exc:
        _import_errors[key] = str(exc)
        return None

# Attempt imports once (cached across reruns via module-level cache)
@st.cache_resource(show_spinner=False)
def _load_modules():
    mods = {}
    mods['intrusion_detection']    = _try_import('intrusion_detection')
    mods['anomaly_detection']      = _try_import('anomaly_detection')
    mods['adversarial_attacks']    = _try_import('adversarial_attacks')
    mods['traffic_classification'] = _try_import('traffic_classification')
    mods['data_loader']            = _try_import('data_loader')
    mods['config']                 = _try_import('config')
    return mods

MODS = _load_modules()

def _mod(name):
    """Return a cached module or display an error widget."""
    m = MODS.get(name)
    if m is None:
        err = _import_errors.get(name, "Unknown import error")
        st.error(f"⚠️ Could not import **{name}**: `{err}`")
    return m

# ---------------------------------------------------------------------------
# Dataset existence check
# ---------------------------------------------------------------------------
NSL_KDD_PATHS = [
    os.path.join(PROJECT_ROOT, 'data', 'KDDTrain+.txt'),
    os.path.join(PROJECT_ROOT, 'data', 'NSL-KDD', 'KDDTrain+.txt'),
    os.path.join(PROJECT_ROOT, 'KDDTrain+.txt'),
]

def _nsl_kdd_present():
    return any(os.path.exists(p) for p in NSL_KDD_PATHS)

# ---------------------------------------------------------------------------
# Figure capture helper
# ---------------------------------------------------------------------------
def _show_current_figure(caption=""):
    """Capture plt.gcf(), render it in Streamlit, then close."""
    fig = plt.gcf()
    st.pyplot(fig)
    if caption:
        st.caption(caption)
    plt.close('all')

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style='text-align:center; padding: 1rem 0 .5rem;'>
            <span style='font-size:3rem;'>🛡️</span>
            <h2 style='color:#58a6ff; margin:.3rem 0 0; font-size:1.1rem;'>CyberSec AI Dashboard</h2>
            <p style='color:#484f58; font-size:.75rem; margin:0;'>Project 16 – University Sétif 1</p>
        </div>
        <hr style='border-color:#30363d; margin:.7rem 0 1rem;'>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigate",
        options=[
            "🏠 Overview",
            "🔍 Intrusion Detection",
            "📡 Anomaly Detection",
            "🌐 Traffic Classification",
            "⚔️ Adversarial Attacks",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<hr style='border-color:#30363d; margin:1rem 0;'>", unsafe_allow_html=True)

    # Dataset download / status
    if not _nsl_kdd_present():
        st.warning("⚠️ NSL-KDD dataset not found locally.")
        dl_mod = MODS.get('data_loader')
        if dl_mod and hasattr(dl_mod, 'download_nsl_kdd'):
            if st.button("📥 Download Dataset"):
                with st.spinner("Downloading NSL-KDD dataset…"):
                    try:
                        dl_mod.download_nsl_kdd()
                        st.success("✅ Dataset downloaded!")
                        st.experimental_rerun()
                    except Exception as exc:
                        st.error(f"Download failed: {exc}")
        else:
            st.info("Install `data_loader` module to enable auto-download.")
    else:
        st.success("✅ NSL-KDD dataset found")

    # Sidebar footer (pinned)
    st.markdown(
        """
        <div class='sidebar-footer'>
            NSL-KDD Dataset &nbsp;|&nbsp; scikit-learn<br>
            Made with ❤️ using Streamlit
        </div>
        """,
        unsafe_allow_html=True,
    )

# ===========================================================================
# PAGE: Overview
# ===========================================================================
if page == "🏠 Overview":
    st.markdown(
        """
        <div class='hero-banner'>
            <h1>🛡️ AI-Based Cybersecurity Dashboard</h1>
            <p>Project 16 – Implementation of an AI-Based Cybersecurity Use Case &nbsp;|&nbsp;
            Security &amp; Privacy – Medicine &amp; Big Data &nbsp;|&nbsp; University Sétif 1, 2025/2026</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Project description ----
    st.markdown("<div class='section-title'>About the Project</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='info-card'>
            <h4>🎯 Objective</h4>
            This project implements a comprehensive <strong>AI-Based Cybersecurity</strong> framework
            using Machine Learning techniques to detect and classify network intrusions in real time.
            It demonstrates four complementary components: <em>supervised intrusion detection</em>,
            <em>unsupervised anomaly detection</em>, <em>multi-class traffic classification</em>,
            and an analysis of <em>adversarial vulnerabilities</em> in AI-based security models.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Metric cards ----
    st.markdown("<div class='section-title'>Project at a Glance</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "🤖", "3",          "ML Models"),
        (c2, "💥", "5",          "Attack Classes"),
        (c3, "📦", "~150 K",     "Dataset Samples"),
        (c4, "🎯", "97–99%",     "Accuracy Range"),
    ]
    for col, icon, val, lbl in cards:
        col.markdown(
            f"""
            <div class='metric-card'>
                <div class='icon'>{icon}</div>
                <div class='value'>{val}</div>
                <div class='label'>{lbl}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---- Dataset info ----
    st.markdown("<div class='section-title'>NSL-KDD Dataset</div>", unsafe_allow_html=True)
    di1, di2 = st.columns([3, 2])
    with di1:
        st.markdown(
            """
            <div class='info-card'>
                <h4>📂 Dataset Overview</h4>
                The <strong>NSL-KDD</strong> dataset is the standard benchmark for network intrusion
                detection research.  It resolves redundancy issues present in the original KDD Cup 1999
                dataset and provides a balanced evaluation benchmark.
                <ul style='margin:.5rem 0 0 1rem;'>
                    <li>41 features per connection record</li>
                    <li>5 traffic categories (Normal, DoS, Probe, R2L, U2R)</li>
                    <li>~125 000 training / ~22 000 test records</li>
                    <li>Mix of continuous and categorical features</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with di2:
        # Traffic-type distribution mini chart
        labels  = ['Normal', 'DoS', 'Probe', 'R2L', 'U2R']
        sizes   = [53.46, 22.69, 13.79, 8.66, 1.40]
        colors  = ['#2ea043', '#e74c3c', '#f39c12', '#3498db', '#9b59b6']
        fig_pie, ax = plt.subplots(figsize=(4, 3.2), facecolor='none')
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors,
            autopct='%1.1f%%', startangle=140,
            pctdistance=0.75,
            textprops={'color': '#cdd9e5', 'fontsize': 8},
            wedgeprops={'edgecolor': '#0d1117', 'linewidth': 1.5},
        )
        for at in autotexts:
            at.set_fontsize(7)
        ax.set_title('NSL-KDD Class Distribution', color='#cdd9e5', fontsize=9, pad=8)
        fig_pie.patch.set_alpha(0)
        st.pyplot(fig_pie)
        plt.close('all')

    # ---- Architecture ----
    st.markdown("<div class='section-title'>System Architecture</div>", unsafe_allow_html=True)
    st.code(
        """
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
   │ • RF       │  │ • Iso.      │ │ • RF      │ │ • FGSM       │
   │ • DT       │  │   Forest    │ │ Classifier│ │ • Rnd Noise  │
   │ • MLP      │  │ • 1-class   │ │           │ │ • Feat. Manip│
   │            │  │   SVM       │ │           │ │              │
   └────────────┘  └─────────────┘ └───────────┘ └──────────────┘
           │              │              │               │
           └──────────────┴──────────────┴───────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Streamlit Dashboard│
                    │  (Interactive UI)    │
                    └─────────────────────┘
        """,
        language="",
    )

    # ---- Team ----
    st.markdown("<div class='section-title'>👩‍💻 Authors</div>", unsafe_allow_html=True)
    a1, a2 = st.columns(2)
    for col, name, role in [
        (a1, "DAHEL Rahma",    "Security & Privacy – Medicine & Big Data"),
        (a2, "GHEDJATI Zainab","Security & Privacy – Medicine & Big Data"),
    ]:
        col.markdown(
            f"""
            <div class='info-card' style='text-align:center;'>
                <div style='font-size:2.2rem;'>👩‍🔬</div>
                <strong style='color:#79c0ff;'>{name}</strong><br>
                <span style='font-size:.82rem; color:#8b949e;'>{role}</span><br>
                <span style='font-size:.78rem; color:#484f58;'>Université Sétif 1 — 2025/2026</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ===========================================================================
# PAGE: Intrusion Detection
# ===========================================================================
elif page == "🔍 Intrusion Detection":
    st.markdown(
        "<div class='hero-banner'><h1>🔍 Intrusion Detection System</h1>"
        "<p>Supervised binary classification: <em>Normal</em> vs <em>Attack</em> traffic — "
        "comparing Random Forest, Decision Tree, and Neural Network.</p></div>",
        unsafe_allow_html=True,
    )

    ids_mod = _mod('intrusion_detection')

    tab1, tab2, tab3 = st.tabs(["📊 Algorithm Comparison", "🔥 Confusion Matrix", "ℹ️ Model Details"])

    # ---- Tab 1: Run comparison ----
    with tab1:
        st.markdown("Run all three supervised models on 10 000 synthetic network-traffic samples.")
        if st.button("🚀 Run Intrusion Detection Analysis", key="ids_run"):
            if ids_mod is None:
                st.stop()
            from sklearn.model_selection import train_test_split
            with st.spinner("Generating data & training models … this may take ~30 s"):
                try:
                    df = ids_mod.generate_synthetic_network_traffic(n_samples=10_000, attack_ratio=0.3)
                    X = df.drop('label', axis=1)
                    y = df['label']
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=0.3, random_state=42, stratify=y
                    )
                    results = ids_mod.compare_algorithms(X_train, y_train, X_test, y_test)

                    st.success("✅ Analysis complete!")

                    # Metric cards
                    st.markdown("<div class='section-title'>Performance Metrics</div>", unsafe_allow_html=True)
                    algo_labels = {
                        'random_forest':  ('🌲 Random Forest',  '#2ea043'),
                        'decision_tree':  ('🌿 Decision Tree',  '#f39c12'),
                        'neural_network': ('🧠 Neural Network', '#3498db'),
                    }
                    cols = st.columns(3)
                    for idx, (algo, res) in enumerate(results.items()):
                        m   = res['metrics']
                        lbl, clr = algo_labels.get(algo, (algo, '#58a6ff'))
                        with cols[idx]:
                            st.metric(f"{lbl} Accuracy", f"{m['accuracy']*100:.2f}%")
                            st.metric("F1-Score",  f"{m['f1_score']:.4f}")
                            st.metric("Precision", f"{m['precision']:.4f}")
                            st.metric("Recall",    f"{m['recall']:.4f}")

                    # Bar chart comparison
                    st.markdown("<div class='section-title'>Bar Chart Comparison</div>", unsafe_allow_html=True)
                    ids_mod.plot_algorithm_comparison(results)
                    _show_current_figure("Performance metrics across three algorithms")

                    # Store results in session for other tabs
                    st.session_state['ids_results'] = results
                    st.session_state['ids_X_test']  = X_test
                    st.session_state['ids_y_test']  = y_test

                except Exception as exc:
                    st.error(f"Error during analysis: {exc}")
                    import traceback; st.code(traceback.format_exc())

    # ---- Tab 2: Confusion matrix ----
    with tab2:
        if 'ids_results' not in st.session_state:
            st.info("👆 Run the analysis on the **Algorithm Comparison** tab first.")
        else:
            results = st.session_state['ids_results']
            X_test  = st.session_state['ids_X_test']
            y_test  = st.session_state['ids_y_test']
            chosen  = st.selectbox("Select model", list(results.keys()),
                                   format_func=lambda x: x.replace('_', ' ').title())
            ids_obj = results[chosen]['model']
            _, y_pred = ids_obj.evaluate(X_test, y_test)
            ids_obj.plot_confusion_matrix(y_test, y_pred)
            _show_current_figure(f"Confusion matrix – {chosen.replace('_',' ').title()}")

    # ---- Tab 3: Model details ----
    with tab3:
        st.markdown(
            """
            <div class='info-card'>
                <h4>🌲 Random Forest</h4>
                An ensemble of 100 decision trees trained with bagging.
                Robust to noise and overfitting; provides feature importance scores.
                Typically achieves <strong>~99% accuracy</strong> on NSL-KDD.
            </div>
            <div class='info-card'>
                <h4>🌿 Decision Tree</h4>
                Single tree with max-depth 10. Highly interpretable; fast inference.
                Achieves <strong>~98% accuracy</strong>; slightly prone to overfitting on deep trees.
            </div>
            <div class='info-card'>
                <h4>🧠 Neural Network (MLP)</h4>
                Multi-layer perceptron with hidden layers (64, 32). Captures complex
                non-linear relationships. Achieves <strong>~97% accuracy</strong>;
                requires more training time.
            </div>
            """,
            unsafe_allow_html=True,
        )

# ===========================================================================
# PAGE: Anomaly Detection
# ===========================================================================
elif page == "📡 Anomaly Detection":
    st.markdown(
        "<div class='hero-banner'><h1>📡 Anomaly Detection</h1>"
        "<p>Unsupervised detection of network anomalies using <em>Isolation Forest</em> "
        "and <em>One-Class SVM</em> — no labelled attack data required during training.</p></div>",
        unsafe_allow_html=True,
    )

    ad_mod  = _mod('anomaly_detection')
    ids_mod = _mod('intrusion_detection')   # needed for data generation

    tab1, tab2 = st.tabs(["📊 Method Comparison", "📈 ROC Curve"])

    with tab1:
        st.markdown("Train both detectors on 8 000 synthetic samples and compare their performance.")
        if st.button("🚀 Run Anomaly Detection Analysis", key="ad_run"):
            if ad_mod is None or ids_mod is None:
                st.stop()
            from sklearn.model_selection import train_test_split
            import numpy as np
            with st.spinner("Training anomaly detectors … please wait"):
                try:
                    df = ids_mod.generate_synthetic_network_traffic(n_samples=8_000, attack_ratio=0.3)
                    X  = df.drop('label', axis=1)
                    y  = df['label']
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=0.3, random_state=42, stratify=y
                    )

                    results = ad_mod.compare_anomaly_methods(X_train, X_test, y_test)
                    st.success("✅ Analysis complete!")

                    # Metrics
                    st.markdown("<div class='section-title'>Performance Metrics</div>", unsafe_allow_html=True)
                    method_labels = {
                        'isolation_forest': '🌲 Isolation Forest',
                        'one_class_svm':    '🎯 One-Class SVM',
                    }
                    cols = st.columns(2)
                    for idx, (method, res) in enumerate(results.items()):
                        m   = res['metrics']
                        lbl = method_labels.get(method, method)
                        with cols[idx]:
                            st.metric(f"{lbl} Accuracy", f"{m['accuracy']*100:.2f}%")
                            st.metric("F1-Score", f"{m['f1_score']:.4f}")
                            st.metric("AUC-ROC",  f"{m['auc']:.4f}")
                            st.metric("Recall",   f"{m['recall']:.4f}")

                    # Bar chart
                    st.markdown("<div class='section-title'>Visual Comparison</div>", unsafe_allow_html=True)
                    ad_mod.plot_anomaly_comparison(results)
                    _show_current_figure("Anomaly detection methods comparison")

                    st.session_state['ad_results'] = results
                    st.session_state['ad_X_test']  = X_test
                    y_test_binary = np.where(y_test == 'attack', 1, 0)
                    st.session_state['ad_y_bin']   = y_test_binary

                except Exception as exc:
                    st.error(f"Error during analysis: {exc}")
                    import traceback; st.code(traceback.format_exc())

    with tab2:
        if 'ad_results' not in st.session_state:
            st.info("👆 Run the analysis on the **Method Comparison** tab first.")
        else:
            results      = st.session_state['ad_results']
            X_test       = st.session_state['ad_X_test']
            y_test_binary = st.session_state['ad_y_bin']
            chosen = st.selectbox("Select method", list(results.keys()),
                                  format_func=lambda x: x.replace('_', ' ').title())
            detector = results[chosen]['detector']
            detector.plot_roc_curve(X_test, y_test_binary)
            _show_current_figure(f"ROC Curve – {chosen.replace('_',' ').title()}")

# ===========================================================================
# PAGE: Traffic Classification
# ===========================================================================
elif page == "🌐 Traffic Classification":
    st.markdown(
        "<div class='hero-banner'><h1>🌐 Network Traffic Classification</h1>"
        "<p>Multi-class classification of five traffic categories: "
        "<em>Normal, DoS, Probe, R2L, U2R</em> using a Random Forest classifier.</p></div>",
        unsafe_allow_html=True,
    )

    tc_mod = _mod('traffic_classification')

    tab1, tab2, tab3 = st.tabs(["🚦 Classification Results", "🔥 Confusion Matrix", "📊 Class Distribution"])

    with tab1:
        st.markdown("Generate 10 000 multi-class traffic samples, train the classifier, and evaluate.")
        if st.button("🚀 Run Traffic Classification", key="tc_run"):
            if tc_mod is None:
                st.stop()
            from sklearn.model_selection import train_test_split
            with st.spinner("Training multi-class classifier … please wait"):
                try:
                    df = tc_mod.generate_multiclass_traffic(n_samples=10_000)
                    X  = df.drop('label', axis=1)
                    y  = df['label']
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=0.3, random_state=42, stratify=y
                    )

                    clf = tc_mod.TrafficClassifier()
                    clf.train(X_train, y_train)
                    accuracy, y_pred = clf.evaluate(X_test, y_test)

                    st.success("✅ Classification complete!")

                    col1, col2, col3 = st.columns(3)
                    col1.metric("Overall Accuracy", f"{accuracy*100:.2f}%")
                    col2.metric("Training Samples", f"{len(X_train):,}")
                    col3.metric("Test Samples",     f"{len(X_test):,}")

                    # Per-class bar
                    st.markdown("<div class='section-title'>Per-Class Accuracy</div>", unsafe_allow_html=True)
                    import pandas as pd
                    from sklearn.metrics import classification_report
                    report = classification_report(y_test, y_pred, output_dict=True)
                    classes = [c for c in report.keys() if c not in ('accuracy','macro avg','weighted avg')]
                    fig_bar, ax = plt.subplots(figsize=(10, 4), facecolor='none')
                    accs   = [report[c]['precision'] for c in classes]
                    clr_map = ['#2ea043','#e74c3c','#f39c12','#3498db','#9b59b6']
                    bars = ax.bar(classes, accs, color=clr_map[:len(classes)], alpha=0.85, edgecolor='#30363d')
                    ax.set_ylim(0, 1.12)
                    ax.set_ylabel('Precision', color='#cdd9e5')
                    ax.set_facecolor('none')
                    ax.tick_params(colors='#cdd9e5')
                    ax.spines[['top','right']].set_visible(False)
                    ax.spines[['left','bottom']].set_color('#30363d')
                    for bar in bars:
                        h = bar.get_height()
                        ax.text(bar.get_x()+bar.get_width()/2, h+.01,
                                f'{h:.2f}', ha='center', va='bottom',
                                color='#cdd9e5', fontsize=9, fontweight='bold')
                    st.pyplot(fig_bar)
                    plt.close('all')

                    st.session_state['tc_clf']    = clf
                    st.session_state['tc_y_test'] = y_test
                    st.session_state['tc_y_pred'] = y_pred
                    st.session_state['tc_y_train'] = y_train

                except Exception as exc:
                    st.error(f"Error during classification: {exc}")
                    import traceback; st.code(traceback.format_exc())

    with tab2:
        if 'tc_clf' not in st.session_state:
            st.info("👆 Run the analysis on the **Classification Results** tab first.")
        else:
            clf    = st.session_state['tc_clf']
            y_test = st.session_state['tc_y_test']
            y_pred = st.session_state['tc_y_pred']
            clf.plot_confusion_matrix(y_test, y_pred)
            _show_current_figure("Multi-class confusion matrix")

    with tab3:
        if 'tc_clf' not in st.session_state:
            st.info("👆 Run the analysis on the **Classification Results** tab first.")
        else:
            clf     = st.session_state['tc_clf']
            y_train = st.session_state['tc_y_train']
            y_test  = st.session_state['tc_y_test']
            clf.plot_class_distribution(y_train, y_test)
            _show_current_figure("Training and test class distributions")

# ===========================================================================
# PAGE: Adversarial Attacks
# ===========================================================================
elif page == "⚔️ Adversarial Attacks":
    st.markdown(
        "<div class='hero-banner'><h1>⚔️ Adversarial Attack Analysis</h1>"
        "<p>Probing the robustness of AI-based IDS against three adversarial strategies: "
        "<em>FGSM, Random Noise, Feature Manipulation</em>.</p></div>",
        unsafe_allow_html=True,
    )

    adv_mod = _mod('adversarial_attacks')

    tab1, tab2 = st.tabs(["⚔️ Attack Simulation", "📖 Attack Descriptions"])

    with tab1:
        st.markdown("Train a baseline Random Forest IDS, then simulate three adversarial attacks.")

        col_eps, col_noise = st.columns(2)
        epsilon    = col_eps.slider("FGSM epsilon (perturbation)",    0.01, 0.5, 0.1, 0.01)
        noise_lvl  = col_noise.slider("Random noise level",           0.01, 0.3, 0.05, 0.01)

        if st.button("🚀 Run Adversarial Attack Simulation", key="adv_run"):
            if adv_mod is None:
                st.stop()
            ids_mod = _mod('intrusion_detection')
            if ids_mod is None:
                st.stop()
            from sklearn.model_selection import train_test_split
            with st.spinner("Running adversarial simulations … this may take ~20 s"):
                try:
                    # Data
                    df = ids_mod.generate_synthetic_network_traffic(n_samples=5_000, attack_ratio=0.3)
                    X  = df.drop('label', axis=1)
                    y  = df['label']
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y, test_size=0.3, random_state=42, stratify=y
                    )

                    # Train base model
                    base_ids = ids_mod.IntrusionDetectionSystem(algorithm='random_forest')
                    base_ids.train(X_train, y_train)

                    # Adversarial simulator
                    simulator = adv_mod.AdversarialAttackSimulator(base_ids.model, base_ids.scaler)

                    # Binary labels
                    y_test_binary = base_ids.label_encoder.transform(y_test)

                    attack_configs = [
                        ('fgsm',                {'epsilon': epsilon}),
                        ('random_noise',         {'noise_level': noise_lvl}),
                        ('feature_manipulation', {'feature_indices': [0, 1, 2, 5], 'manipulation_factor': 0.5}),
                    ]

                    all_results = []
                    for attack_type, params in attack_configs:
                        res = simulator.evaluate_robustness(
                            X_test, y_test_binary, attack_type=attack_type, **params
                        )
                        all_results.append(res)

                    st.success("✅ Adversarial simulation complete!")

                    # Summary cards
                    st.markdown("<div class='section-title'>Attack Impact Summary</div>", unsafe_allow_html=True)
                    cols = st.columns(3)
                    attack_icons = ['⚡ FGSM', '🎲 Random Noise', '🔧 Feat. Manipulation']
                    for idx, (res, icon) in enumerate(zip(all_results, attack_icons)):
                        with cols[idx]:
                            st.metric(
                                label=icon,
                                value=f"{res['adversarial_accuracy']*100:.2f}%",
                                delta=f"{-res['accuracy_drop']*100:.2f}% vs baseline",
                            )
                            st.caption(f"Evasion rate: {res['evasion_rate']*100:.1f}%")

                    # Plot
                    st.markdown("<div class='section-title'>Visual Comparison</div>", unsafe_allow_html=True)
                    adv_mod.plot_adversarial_comparison(all_results)
                    _show_current_figure("Accuracy before & after each adversarial attack, plus evasion rate")

                    st.session_state['adv_results'] = all_results

                except Exception as exc:
                    st.error(f"Error during adversarial simulation: {exc}")
                    import traceback; st.code(traceback.format_exc())

    with tab2:
        st.markdown(
            """
            <div class='info-card'>
                <h4>⚡ Fast Gradient Sign Method (FGSM)</h4>
                Originally proposed for image classifiers, FGSM adds a small perturbation in the
                direction of the gradient of the loss function. Here it is simulated by adding
                random noise scaled by <code>epsilon</code> to the input feature vector.
                Even small perturbations (ε = 0.1) can meaningfully degrade IDS accuracy.
            </div>
            <div class='info-card'>
                <h4>🎲 Random Noise Attack</h4>
                Attacker injects proportional Gaussian noise into each feature.
                Simulates real-world sensor noise or minor packet-field tampering.
                At <code>noise_level = 5%</code> the model typically loses 2–5% accuracy.
            </div>
            <div class='info-card'>
                <h4>🔧 Feature Manipulation Attack</h4>
                Attacker deliberately reduces the values of the most discriminative features
                (e.g., <em>src_bytes</em>, <em>count</em>) by a factor of 0.5 to camouflage
                attack traffic as normal. This targeted evasion is the most dangerous in practice.
            </div>
            """,
            unsafe_allow_html=True,
        )
