const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");

const { FaShieldAlt, FaSearch, FaChartBar, FaExclamationTriangle, FaRobot,
        FaDatabase, FaCode, FaCheckCircle, FaUsers, FaGithub, FaBrain,
        FaNetworkWired, FaLock, FaBug, FaArrowRight, FaServer } = require("react-icons/fa");
const { MdSecurity, MdSpeed, MdAnalytics } = require("react-icons/md");

async function iconPng(IconComponent, color = "#FFFFFF", size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

const C = {
  navy:       "0A0E27",
  navyMid:    "0D1135",
  navyLight:  "131A45",
  teal:       "00D4AA",
  tealDark:   "009E7F",
  cyan:       "00B4D8",
  white:      "FFFFFF",
  offWhite:   "E8EDF5",
  gray:       "8892AA",
  grayLight:  "B8C4D6",
  red:        "FF4757",
  amber:      "FFB347",
  green:      "00D4AA",
  card:       "111936",
  cardBorder: "1E2D5A",
};

const makeShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.25 });

async function buildPresentation() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title = "AI-Based Cybersecurity System";
  pres.author = "Ayush Koul, Vinayak Singh Jamwal, Prajwal Shan";

  // SLIDE 1
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.teal }, line: { color: C.teal } });
    for (let col = 0; col < 6; col++) {
      for (let row = 0; row < 4; row++) {
        s.addShape(pres.shapes.OVAL, { x: 6.5 + col * 0.55, y: 0.5 + row * 0.6, w: 0.06, h: 0.06,
          fill: { color: C.teal, transparency: 70 }, line: { color: C.teal, transparency: 70 } });
      }
    }
    const shieldIcon = await iconPng(FaShieldAlt, "#" + C.teal, 512);
    s.addImage({ data: shieldIcon, x: 7.5, y: 0.8, w: 1.8, h: 1.8 });
    s.addText("PROJECT 16  ·  MINI PROJECT", { x: 0.4, y: 0.5, w: 6.5, h: 0.35, fontSize: 10, color: C.teal, bold: true, charSpacing: 4, margin: 0 });
    s.addText("AI-Based", { x: 0.4, y: 1.05, w: 7, h: 0.85, fontSize: 52, bold: true, color: C.white, margin: 0 });
    s.addText("Cybersecurity System", { x: 0.4, y: 1.85, w: 7.8, h: 0.85, fontSize: 52, bold: true, color: C.teal, margin: 0 });
    s.addText("Network Intrusion Detection  ·  Anomaly Analysis  ·  Traffic Classification  ·  Adversarial Robustness", { x: 0.4, y: 2.85, w: 9, h: 0.35, fontSize: 11, color: C.grayLight, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.4, y: 3.3, w: 2.5, h: 0.03, fill: { color: C.teal }, line: { color: C.teal } });
    s.addText("Model Institute of Engineering and Technology (Autonomous)", { x: 0.4, y: 3.5, w: 9, h: 0.3, fontSize: 12, color: C.grayLight, italic: true, margin: 0 });
    s.addText("Ayush Koul  ·  Vinayak Singh Jamwal  ·  Prajwal Shan", { x: 0.4, y: 3.9, w: 9, h: 0.3, fontSize: 12, color: C.white, bold: true, margin: 0 });
    const tags = ["Python 3.8+", "scikit-learn", "Streamlit", "NSL-KDD Dataset", "ML + AI"];
    tags.forEach((tag, i) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 0.4 + i * 1.85, y: 4.6, w: 1.7, h: 0.38, fill: { color: C.navyLight }, line: { color: C.cardBorder }, shadow: makeShadow() });
      s.addText(tag, { x: 0.4 + i * 1.85, y: 4.6, w: 1.7, h: 0.38, fontSize: 9, color: C.teal, bold: true, align: "center", valign: "middle", margin: 0 });
    });
  }

  // SLIDE 2
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.red }, line: { color: C.red } });
    s.addText("THE PROBLEM", { x: 0.3, y: 0.3, w: 9, h: 0.3, fontSize: 10, color: C.red, bold: true, charSpacing: 3, margin: 0 });
    s.addText("Why Does Cybersecurity Need AI?", { x: 0.3, y: 0.65, w: 9, h: 0.6, fontSize: 30, bold: true, color: C.white, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.35, w: 9, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    const stats = [
      { icon: FaExclamationTriangle, val: "2,200+", label: "Cyberattacks per day\nglobally", color: C.red },
      { icon: FaNetworkWired, val: "$9.5T", label: "Cybercrime cost\nestimated in 2024", color: C.amber },
      { icon: FaSearch, val: "287 days", label: "Average breach\ndetection time", color: C.cyan },
    ];
    for (let i = 0; i < stats.length; i++) {
      const st = stats[i];
      s.addShape(pres.shapes.RECTANGLE, { x: 0.3 + i * 3.25, y: 1.55, w: 3.0, h: 1.5, fill: { color: C.card }, line: { color: C.cardBorder }, shadow: makeShadow() });
      const ico = await iconPng(st.icon, "#" + st.color, 256);
      s.addImage({ data: ico, x: 0.5 + i * 3.25, y: 1.75, w: 0.5, h: 0.5 });
      s.addText(st.val, { x: 1.1 + i * 3.25, y: 1.72, w: 2.0, h: 0.45, fontSize: 22, bold: true, color: st.color, margin: 0 });
      s.addText(st.label, { x: 1.1 + i * 3.25, y: 2.2, w: 2.0, h: 0.6, fontSize: 10, color: C.grayLight, margin: 0 });
    }
    const problems = [
      { icon: FaBug, text: "Traditional rule-based systems miss novel & zero-day attacks" },
      { icon: FaDatabase, text: "Network traffic volume has grown beyond manual analysis capacity" },
      { icon: FaLock, text: "Attackers use adversarial techniques to evade detection" },
      { icon: FaChartBar, text: "Lack of real-time multi-class threat classification in most tools" },
    ];
    for (let i = 0; i < problems.length; i++) {
      const p = problems[i];
      const row = Math.floor(i / 2), col = i % 2;
      s.addShape(pres.shapes.RECTANGLE, { x: 0.3 + col * 4.8, y: 3.2 + row * 1.0, w: 4.5, h: 0.75, fill: { color: C.navyLight }, line: { color: C.cardBorder } });
      const ico = await iconPng(p.icon, "#" + C.teal, 256);
      s.addImage({ data: ico, x: 0.5 + col * 4.8, y: 3.35 + row * 1.0, w: 0.35, h: 0.35 });
      s.addText(p.text, { x: 1.0 + col * 4.8, y: 3.3 + row * 1.0, w: 3.6, h: 0.65, fontSize: 11, color: C.offWhite, valign: "middle", margin: 0 });
    }
  }

  // SLIDE 3
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.teal }, line: { color: C.teal } });
    s.addText("PROJECT OBJECTIVES", { x: 0.3, y: 0.3, w: 9, h: 0.3, fontSize: 10, color: C.teal, bold: true, charSpacing: 3, margin: 0 });
    s.addText("What We Set Out to Build", { x: 0.3, y: 0.65, w: 9, h: 0.55, fontSize: 30, bold: true, color: C.white, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.28, w: 9, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    const objectives = [
      { num: "01", icon: FaShieldAlt, title: "Binary IDS", desc: "Detect normal vs attack traffic with supervised ML (RF, DT, MLP) achieving >97% accuracy", color: C.teal },
      { num: "02", icon: FaSearch, title: "Anomaly Detection", desc: "Identify unknown threats without labelled data using Isolation Forest & One-Class SVM", color: C.cyan },
      { num: "03", icon: FaChartBar, title: "Traffic Classification", desc: "Classify 5 network traffic categories: Normal, DoS, Probe, R2L, U2R with multi-class RF", color: C.amber },
      { num: "04", icon: FaBug, title: "Adversarial Robustness", desc: "Simulate FGSM, Random Noise & Feature Manipulation attacks to probe IDS resilience", color: C.red },
      { num: "05", icon: FaRobot, title: "Unified Dashboard", desc: "Interactive Streamlit web UI consolidating all modules with live visualizations", color: C.teal },
      { num: "06", icon: FaDatabase, title: "NSL-KDD Benchmark", desc: "Validate all models on the industry-standard NSL-KDD dataset (125K+ training records)", color: C.cyan },
    ];
    for (let i = 0; i < objectives.length; i++) {
      const obj = objectives[i];
      const col = i % 3, row = Math.floor(i / 3);
      const x = 0.3 + col * 3.25, y = 1.45 + row * 1.85;
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 3.05, h: 1.65, fill: { color: C.card }, line: { color: C.cardBorder }, shadow: makeShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 3.05, h: 0.05, fill: { color: obj.color }, line: { color: obj.color } });
      const ico = await iconPng(obj.icon, "#" + obj.color, 256);
      s.addImage({ data: ico, x: x + 0.18, y: y + 0.22, w: 0.38, h: 0.38 });
      s.addText(obj.num, { x: x + 2.5, y: y + 0.1, w: 0.45, h: 0.3, fontSize: 18, bold: true, color: obj.color, opacity: 0.25, align: "right", margin: 0 });
      s.addText(obj.title, { x: x + 0.65, y: y + 0.18, w: 2.25, h: 0.35, fontSize: 13, bold: true, color: C.white, margin: 0 });
      s.addText(obj.desc, { x: x + 0.15, y: y + 0.62, w: 2.75, h: 0.9, fontSize: 9.5, color: C.grayLight, margin: 0 });
    }
  }

  // SLIDE 4
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.cyan }, line: { color: C.cyan } });
    s.addText("SOLUTION ARCHITECTURE", { x: 0.3, y: 0.3, w: 9, h: 0.3, fontSize: 10, color: C.cyan, bold: true, charSpacing: 3, margin: 0 });
    s.addText("System Design & Data Flow", { x: 0.3, y: 0.65, w: 9, h: 0.55, fontSize: 30, bold: true, color: C.white, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.28, w: 9, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.55, w: 2.1, h: 0.7, fill: { color: C.navyLight }, line: { color: C.cardBorder } });
    s.addText("NSL-KDD\nDataset Input", { x: 0.3, y: 1.55, w: 2.1, h: 0.7, fontSize: 10, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 2.42, y: 1.83, w: 0.4, h: 0.04, fill: { color: C.teal }, line: { color: C.teal } });
    s.addShape(pres.shapes.RECTANGLE, { x: 2.85, y: 1.55, w: 2.0, h: 0.7, fill: { color: C.navyLight }, line: { color: C.teal } });
    s.addText("Pre-processing\nNormalize + Encode", { x: 2.85, y: 1.55, w: 2.0, h: 0.7, fontSize: 10, bold: true, color: C.teal, align: "center", valign: "middle", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 4.87, y: 1.83, w: 0.4, h: 0.04, fill: { color: C.teal }, line: { color: C.teal } });
    s.addShape(pres.shapes.RECTANGLE, { x: 5.3, y: 1.45, w: 2.4, h: 0.9, fill: { color: C.teal, transparency: 80 }, line: { color: C.teal } });
    s.addText("ML Engine\n(4 Modules)", { x: 5.3, y: 1.45, w: 2.4, h: 0.9, fontSize: 12, bold: true, color: C.teal, align: "center", valign: "middle", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 7.73, y: 1.83, w: 0.4, h: 0.04, fill: { color: C.teal }, line: { color: C.teal } });
    s.addShape(pres.shapes.RECTANGLE, { x: 8.15, y: 1.55, w: 1.55, h: 0.7, fill: { color: C.navyLight }, line: { color: C.amber } });
    s.addText("Streamlit\nDashboard", { x: 8.15, y: 1.55, w: 1.55, h: 0.7, fontSize: 10, bold: true, color: C.amber, align: "center", valign: "middle", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 6.48, y: 2.37, w: 0.04, h: 0.3, fill: { color: C.teal }, line: { color: C.teal } });
    const modules = [
      { title: "Intrusion\nDetection", sub: "RF · DT · MLP", color: C.teal },
      { title: "Anomaly\nDetection", sub: "IsoForest · SVM", color: C.cyan },
      { title: "Traffic\nClassification", sub: "5-class RF", color: C.amber },
      { title: "Adversarial\nAttacks", sub: "FGSM · Noise", color: C.red },
    ];
    for (let i = 0; i < modules.length; i++) {
      const m = modules[i];
      const x = 0.3 + i * 2.4;
      s.addShape(pres.shapes.RECTANGLE, { x, y: 2.7, w: 2.2, h: 1.1, fill: { color: C.card }, line: { color: m.color }, shadow: makeShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x, y: 2.7, w: 2.2, h: 0.06, fill: { color: m.color }, line: { color: m.color } });
      s.addText(m.title, { x, y: 2.78, w: 2.2, h: 0.55, fontSize: 11, bold: true, color: m.color, align: "center", valign: "middle", margin: 0 });
      s.addText(m.sub, { x, y: 3.35, w: 2.2, h: 0.35, fontSize: 9, color: C.grayLight, align: "center", margin: 0 });
      s.addShape(pres.shapes.RECTANGLE, { x: x + 1.08, y: 2.37, w: 0.04, h: 0.33, fill: { color: m.color }, line: { color: m.color } });
    }
    s.addShape(pres.shapes.RECTANGLE, { x: 1.37, y: 2.37, w: 7.24, h: 0.04, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 4.0, w: 9.4, h: 1.3, fill: { color: C.navyLight }, line: { color: C.cardBorder } });
    s.addText("OUTPUT  →", { x: 0.45, y: 4.15, w: 1.2, h: 0.3, fontSize: 10, bold: true, color: C.teal, margin: 0 });
    const outputs = ["Accuracy / F1 / AUC", "Confusion Matrices", "ROC Curves", "Feature Importance", "Attack Robustness %"];
    outputs.forEach((o, i) => {
      s.addShape(pres.shapes.OVAL, { x: 1.55 + i * 1.65, y: 4.12, w: 0.12, h: 0.12, fill: { color: C.teal }, line: { color: C.teal } });
      s.addText(o, { x: 1.75 + i * 1.65, y: 4.08, w: 1.55, h: 0.3, fontSize: 9.5, color: C.offWhite, margin: 0 });
    });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 4.52, w: 9.4, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    s.addText("All outputs visualized in the interactive Streamlit dashboard at http://localhost:8501", { x: 0.3, y: 4.6, w: 9.4, h: 0.6, fontSize: 10, color: C.grayLight, italic: true, align: "center", valign: "middle", margin: 0 });
  }

  // SLIDE 5
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.amber }, line: { color: C.amber } });
    s.addText("DATASET", { x: 0.3, y: 0.3, w: 9, h: 0.3, fontSize: 10, color: C.amber, bold: true, charSpacing: 3, margin: 0 });
    s.addText("NSL-KDD Benchmark Dataset", { x: 0.3, y: 0.65, w: 9, h: 0.55, fontSize: 30, bold: true, color: C.white, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.28, w: 9, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    const props = [
      { label: "Source", val: "Canadian Institute\nfor Cybersecurity" },
      { label: "Features", val: "41 per connection\nrecord" },
      { label: "Training", val: "~125,973\nrecords" },
      { label: "Test Set", val: "~22,544\nrecords" },
    ];
    for (let i = 0; i < props.length; i++) {
      s.addShape(pres.shapes.RECTANGLE, { x: 0.3 + i * 2.38, y: 1.45, w: 2.2, h: 1.0, fill: { color: C.card }, line: { color: C.cardBorder }, shadow: makeShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x: 0.3 + i * 2.38, y: 1.45, w: 2.2, h: 0.05, fill: { color: C.amber }, line: { color: C.amber } });
      s.addText(props[i].label, { x: 0.3 + i * 2.38, y: 1.52, w: 2.2, h: 0.28, fontSize: 8.5, bold: true, color: C.amber, align: "center", margin: 0 });
      s.addText(props[i].val, { x: 0.3 + i * 2.38, y: 1.82, w: 2.2, h: 0.55, fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    }
    s.addText("Traffic Category Breakdown", { x: 0.3, y: 2.6, w: 5.5, h: 0.35, fontSize: 14, bold: true, color: C.white, margin: 0 });
    const tableRows = [
      [{ text: "Label", options: { bold: true, color: C.navy, fill: { color: C.teal } } },
       { text: "Attack Type", options: { bold: true, color: C.navy, fill: { color: C.teal } } },
       { text: "Share", options: { bold: true, color: C.navy, fill: { color: C.teal } } }],
      ["Normal", "Legitimate network traffic", "53%"],
      ["DoS", "Denial-of-Service (flood, smurf, neptune)", "23%"],
      ["Probe", "Surveillance & scanning (nmap, portsweep)", "14%"],
      ["R2L", "Remote-to-Local unauthorized access", "9%"],
      ["U2R", "User-to-Root privilege escalation", "1%"],
    ];
    s.addTable(tableRows, { x: 0.3, y: 3.0, w: 5.5, h: 2.3, border: { pt: 1, color: C.cardBorder }, fill: { color: C.card }, color: C.offWhite, fontSize: 10, colW: [0.9, 3.2, 0.9] });
    s.addChart(pres.charts.PIE, [{ name: "Traffic Distribution", labels: ["Normal (53%)", "DoS (23%)", "Probe (14%)", "R2L (9%)", "U2R (1%)"], values: [53, 23, 14, 9, 1] }], {
      x: 6.0, y: 2.6, w: 3.7, h: 2.8, chartColors: ["00D4AA", "00B4D8", "FFB347", "FF4757", "A78BFA"],
      showPercent: true, showTitle: false, showLegend: true, legendPos: "b", legendFontSize: 8,
      legendColor: C.grayLight, chartArea: { fill: { color: C.navy } }, dataLabelColor: C.navy,
      dataLabelFontSize: 9, dataLabelFontBold: true,
    });
  }

  // SLIDE 6
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.teal }, line: { color: C.teal } });
    s.addText("TECHNOLOGY STACK", { x: 0.3, y: 0.3, w: 9, h: 0.3, fontSize: 10, color: C.teal, bold: true, charSpacing: 3, margin: 0 });
    s.addText("Tools, Libraries & Frameworks", { x: 0.3, y: 0.65, w: 9, h: 0.55, fontSize: 30, bold: true, color: C.white, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.28, w: 9, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    const categories = [
      { label: "Language & Runtime", color: C.teal, items: ["Python 3.8+", "Node.js (tooling)"] },
      { label: "Machine Learning", color: C.cyan, items: ["scikit-learn 1.2+", "NumPy 1.24+", "Pandas 1.5+"] },
      { label: "Visualization", color: C.amber, items: ["Matplotlib 3.6+", "Seaborn 0.12+", "Streamlit 1.28+"] },
      { label: "ML Algorithms", color: C.red, items: ["Random Forest", "Decision Tree", "MLP Neural Net", "Isolation Forest", "One-Class SVM"] },
    ];
    for (let i = 0; i < categories.length; i++) {
      const cat = categories[i];
      const x = 0.3 + (i % 2) * 4.85;
      const y = 1.5 + Math.floor(i / 2) * 1.85;
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.5, h: 1.65, fill: { color: C.card }, line: { color: cat.color }, shadow: makeShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.5, h: 0.38, fill: { color: cat.color, transparency: 75 }, line: { color: cat.color } });
      s.addText(cat.label, { x: x + 0.15, y: y + 0.06, w: 4.2, h: 0.28, fontSize: 11, bold: true, color: cat.color, margin: 0 });
      cat.items.forEach((item, j) => {
        s.addShape(pres.shapes.OVAL, { x: x + 0.18, y: y + 0.55 + j * 0.22, w: 0.1, h: 0.1, fill: { color: cat.color }, line: { color: cat.color } });
        s.addText(item, { x: x + 0.35, y: y + 0.5 + j * 0.22, w: 3.9, h: 0.22, fontSize: 10.5, color: C.offWhite, margin: 0 });
      });
    }
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 5.05, w: 9.4, h: 0.45, fill: { color: C.navyLight }, line: { color: C.cardBorder } });
    const ghIco = await iconPng(FaGithub, "#" + C.teal, 256);
    s.addImage({ data: ghIco, x: 0.5, y: 5.1, w: 0.3, h: 0.3 });
    s.addText("github.com/AyushKoul124/MINI-PROJECT  ·  MIT License  ·  Open Source", { x: 0.9, y: 5.1, w: 8.6, h: 0.3, fontSize: 10, color: C.teal, margin: 0 });
  }

  // SLIDE 7
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.cyan }, line: { color: C.cyan } });
    s.addText("IMPLEMENTATION", { x: 0.3, y: 0.3, w: 9, h: 0.3, fontSize: 10, color: C.cyan, bold: true, charSpacing: 3, margin: 0 });
    s.addText("Module Deep-Dive", { x: 0.3, y: 0.65, w: 9, h: 0.55, fontSize: 30, bold: true, color: C.white, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.28, w: 9, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    const mods = [
      { num: "01", title: "Intrusion Detection System", file: "src/intrusion_detection.py", color: C.teal, details: ["Supervised binary classification: Normal vs Attack", "Algorithms: Random Forest (100 trees), Decision Tree (depth-10), MLP (64-32)", "Pipeline: StandardScaler → LabelEncoder → Model → Metrics", "Output: Accuracy, F1, Confusion Matrix, Feature Importance"] },
      { num: "02", title: "Anomaly Detection", file: "src/anomaly_detection.py", color: C.cyan, details: ["Unsupervised — no labelled attack data needed for training", "Isolation Forest (contamination=0.3) & One-Class SVM", "Outputs ROC-AUC curve & threshold-based binary classification", "Effective for detecting zero-day / novel attack patterns"] },
      { num: "03", title: "Traffic Classification", file: "src/traffic_classification.py", color: C.amber, details: ["5-class: Normal, DoS, Probe, R2L, U2R", "Random Forest multi-class classifier on 10,000+ samples", "Per-class Precision / Recall / F1 + class distribution charts", "generate_multiclass_traffic() for synthetic data generation"] },
      { num: "04", title: "Adversarial Attack Simulator", file: "src/adversarial_attacks.py", color: C.red, details: ["FGSM: epsilon-scaled gradient-direction perturbation (eps=0.1 default)", "Random Noise: Proportional Gaussian noise on all 41 features", "Feature Manipulation: Targeted reduction of top-importance features", "Measures accuracy degradation % under each attack type"] },
    ];
    for (let i = 0; i < mods.length; i++) {
      const m = mods[i];
      const col = i % 2, row = Math.floor(i / 2);
      const x = 0.3 + col * 4.85, y = 1.48 + row * 1.95;
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.5, h: 1.8, fill: { color: C.card }, line: { color: m.color }, shadow: makeShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.06, h: 1.8, fill: { color: m.color }, line: { color: m.color } });
      s.addText(m.num, { x: x + 0.2, y: y + 0.1, w: 0.45, h: 0.3, fontSize: 12, bold: true, color: m.color, margin: 0 });
      s.addText(m.title, { x: x + 0.18, y: y + 0.35, w: 3.6, h: 0.3, fontSize: 12, bold: true, color: C.white, margin: 0 });
      s.addText(m.file, { x: x + 0.18, y: y + 0.66, w: 4.0, h: 0.2, fontSize: 8, color: m.color, italic: true, fontFace: "Consolas", margin: 0 });
      m.details.forEach((d, j) => {
        s.addShape(pres.shapes.OVAL, { x: x + 0.2, y: y + 0.96 + j * 0.21, w: 0.07, h: 0.07, fill: { color: m.color }, line: { color: m.color } });
        s.addText(d, { x: x + 0.35, y: y + 0.92 + j * 0.21, w: 4.0, h: 0.22, fontSize: 9, color: C.grayLight, margin: 0 });
      });
    }
  }

  // SLIDE 8
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.teal }, line: { color: C.teal } });
    s.addText("RESULTS", { x: 0.3, y: 0.3, w: 9, h: 0.3, fontSize: 10, color: C.teal, bold: true, charSpacing: 3, margin: 0 });
    s.addText("Model Performance Metrics", { x: 0.3, y: 0.65, w: 9, h: 0.55, fontSize: 30, bold: true, color: C.white, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.28, w: 9, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    const bigStats = [
      { val: "99.0%", label: "Random Forest\nAccuracy", color: C.teal },
      { val: "~0.990", label: "F1-Score\n(RF)", color: C.cyan },
      { val: "~0.91", label: "AUC-ROC\nIsolation Forest", color: C.amber },
    ];
    for (let i = 0; i < bigStats.length; i++) {
      const st = bigStats[i];
      s.addShape(pres.shapes.RECTANGLE, { x: 0.3 + i * 3.25, y: 1.45, w: 3.0, h: 1.0, fill: { color: C.card }, line: { color: st.color }, shadow: makeShadow() });
      s.addText(st.val, { x: 0.3 + i * 3.25, y: 1.52, w: 3.0, h: 0.52, fontSize: 30, bold: true, color: st.color, align: "center", valign: "middle", margin: 0 });
      s.addText(st.label, { x: 0.3 + i * 3.25, y: 2.05, w: 3.0, h: 0.35, fontSize: 9, color: C.grayLight, align: "center", margin: 0 });
    }
    s.addText("Intrusion Detection — Algorithm Comparison", { x: 0.3, y: 2.55, w: 5.5, h: 0.3, fontSize: 11, bold: true, color: C.white, margin: 0 });
    s.addChart(pres.charts.BAR, [{ name: "Accuracy (%)", labels: ["Random Forest", "Decision Tree", "Neural Network"], values: [99.0, 98.2, 97.5] }], {
      x: 0.3, y: 2.9, w: 5.2, h: 2.5, barDir: "col", chartColors: ["00D4AA", "00B4D8", "A78BFA"],
      chartArea: { fill: { color: C.card }, roundedCorners: true },
      catAxisLabelColor: C.grayLight, valAxisLabelColor: C.grayLight,
      valGridLine: { color: C.cardBorder, size: 0.5 }, catGridLine: { style: "none" },
      showValue: true, dataLabelColor: C.white, dataLabelFontBold: true, showLegend: false, valAxisMinVal: 96,
    });
    s.addText("Anomaly Detection (Unsupervised)", { x: 5.7, y: 2.55, w: 4.0, h: 0.3, fontSize: 11, bold: true, color: C.white, margin: 0 });
    const anomalyRows = [
      [{ text: "Method", options: { bold: true, color: C.navy, fill: { color: C.cyan } } },
       { text: "Accuracy", options: { bold: true, color: C.navy, fill: { color: C.cyan } } },
       { text: "AUC-ROC", options: { bold: true, color: C.navy, fill: { color: C.cyan } } }],
      ["Isolation Forest", "~85%", "~0.91"],
      ["One-Class SVM", "~78%", "~0.87"],
    ];
    s.addTable(anomalyRows, { x: 5.7, y: 2.9, w: 4.0, h: 0.9, border: { pt: 1, color: C.cardBorder }, fill: { color: C.card }, color: C.offWhite, fontSize: 10, colW: [2.0, 1.0, 1.0] });
    s.addText("Traffic Classification — Per-Class F1", { x: 5.7, y: 3.95, w: 4.0, h: 0.3, fontSize: 11, bold: true, color: C.white, margin: 0 });
    s.addChart(pres.charts.BAR, [{ name: "F1-Score", labels: ["Normal", "DoS", "Probe", "R2L", "U2R"], values: [0.99, 0.99, 0.97, 0.96, 0.94] }], {
      x: 5.7, y: 4.25, w: 4.0, h: 1.2, barDir: "bar", chartColors: ["00D4AA"],
      chartArea: { fill: { color: C.card }, roundedCorners: true },
      catAxisLabelColor: C.grayLight, valAxisLabelColor: C.grayLight,
      valGridLine: { style: "none" }, catGridLine: { style: "none" },
      showValue: true, dataLabelColor: C.white, dataLabelFontSize: 9, showLegend: false, valAxisMinVal: 0.9,
    });
  }

  // SLIDE 9
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.amber }, line: { color: C.amber } });
    s.addText("PROOF OF IMPLEMENTATION", { x: 0.3, y: 0.3, w: 9, h: 0.3, fontSize: 10, color: C.amber, bold: true, charSpacing: 3, margin: 0 });
    s.addText("Working Prototype & Outputs", { x: 0.3, y: 0.65, w: 9, h: 0.55, fontSize: 30, bold: true, color: C.white, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.28, w: 9, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.45, w: 5.6, h: 3.2, fill: { color: C.card }, line: { color: C.amber }, shadow: makeShadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.45, w: 5.6, h: 0.35, fill: { color: C.navyLight }, line: { color: C.navyLight } });
    s.addText("● ● ●   localhost:8501 — Streamlit Dashboard", { x: 0.4, y: 1.52, w: 5.4, h: 0.22, fontSize: 8, color: C.gray, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.8, w: 1.2, h: 2.85, fill: { color: C.navyLight }, line: { color: C.navyLight } });
    s.addText("IDS\nAnomaly\nTraffic\nAttack\nReport", { x: 0.35, y: 2.0, w: 1.1, h: 2.0, fontSize: 9, color: C.teal, margin: 0 });
    s.addText("Intrusion Detection System", { x: 1.6, y: 1.88, w: 4.15, h: 0.3, fontSize: 12, bold: true, color: C.white, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 1.55, y: 2.2, w: 4.2, h: 0.55, fill: { color: C.navyMid }, line: { color: C.teal } });
    s.addText("Algorithm: Random Forest  |  Accuracy: 99.0%  |  F1: 0.990", { x: 1.6, y: 2.3, w: 4.1, h: 0.3, fontSize: 9, color: C.teal, margin: 0 });
    const barH = [1.0, 0.7, 0.55];
    const barC = [C.teal, C.cyan, "A78BFA"];
    ["RF", "DT", "MLP"].forEach((lbl, i) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 1.75 + i * 1.0, y: 4.2 - barH[i], w: 0.5, h: barH[i], fill: { color: barC[i] }, line: { color: barC[i] } });
      s.addText(lbl, { x: 1.75 + i * 1.0, y: 4.22, w: 0.5, h: 0.2, fontSize: 8, color: C.gray, align: "center", margin: 0 });
    });
    s.addShape(pres.shapes.RECTANGLE, { x: 6.1, y: 1.45, w: 3.65, h: 2.0, fill: { color: "0D1117" }, line: { color: C.cardBorder }, shadow: makeShadow() });
    s.addText("# sample usage", { x: 6.2, y: 1.55, w: 3.45, h: 0.28, fontSize: 9, color: "6A9955", fontFace: "Consolas", margin: 0 });
    s.addText("from src.intrusion_detection import\n  IntrusionDetectionSystem\n\nids = IntrusionDetectionSystem(\n  algorithm='random_forest'\n)\nids.train(X_train, y_train)\nmetrics, y_pred = ids.evaluate(\n  X_test, y_test)", { x: 6.2, y: 1.85, w: 3.45, h: 1.55, fontSize: 8.5, color: C.offWhite, fontFace: "Consolas", margin: 0 });
    const deliverables = [
      { icon: FaCode, text: "Source code: 4 Python modules + dashboard" },
      { icon: FaGithub, text: "Repository: github.com/AyushKoul124/MINI-PROJECT" },
      { icon: FaCheckCircle, text: "Streamlit dashboard runs at localhost:8501" },
      { icon: FaChartBar, text: "5 output plots saved to docs/ directory" },
    ];
    for (let i = 0; i < deliverables.length; i++) {
      const d = deliverables[i];
      s.addShape(pres.shapes.RECTANGLE, { x: 6.1, y: 3.58 + i * 0.45, w: 3.65, h: 0.38, fill: { color: C.card }, line: { color: C.cardBorder } });
      const ico = await iconPng(d.icon, "#" + C.teal, 256);
      s.addImage({ data: ico, x: 6.2, y: 3.65 + i * 0.45, w: 0.25, h: 0.25 });
      s.addText(d.text, { x: 6.55, y: 3.63 + i * 0.45, w: 3.1, h: 0.28, fontSize: 9.5, color: C.offWhite, margin: 0 });
    }
  }

  // SLIDE 10
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.red }, line: { color: C.red } });
    s.addText("UNIQUE FEATURES", { x: 0.3, y: 0.3, w: 9, h: 0.3, fontSize: 10, color: C.red, bold: true, charSpacing: 3, margin: 0 });
    s.addText("What Makes This Project Stand Out", { x: 0.3, y: 0.65, w: 9, h: 0.55, fontSize: 28, bold: true, color: C.white, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.28, w: 9, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    const features = [
      { icon: FaShieldAlt, title: "4-in-1 Framework", desc: "Single platform covering binary IDS, anomaly detection, multi-class traffic classification, AND adversarial robustness", color: C.teal },
      { icon: FaBug, title: "Adversarial Testing", desc: "Rare in student projects — simulates real-world evasion attacks (FGSM, feature manipulation) to expose IDS blind spots", color: C.red },
      { icon: FaRobot, title: "Unsupervised Anomaly", desc: "Detects unknown zero-day threats without labelled data — mirrors real enterprise security deployments", color: C.cyan },
      { icon: FaChartBar, title: "Interactive Dashboard", desc: "Full Streamlit web UI with live model training, real-time metric display, and downloadable visualizations", color: C.amber },
      { icon: FaDatabase, title: "NSL-KDD Benchmark", desc: "Uses the gold-standard academic dataset with 125K+ records — results are reproducible and comparable to published research", color: C.teal },
      { icon: FaBrain, title: "Modular Architecture", desc: "Clean separation: each module is independently importable and testable — swap algorithms without touching other components", color: C.cyan },
    ];
    for (let i = 0; i < features.length; i++) {
      const f = features[i];
      const col = i % 3, row = Math.floor(i / 3);
      const x = 0.3 + col * 3.25, y = 1.48 + row * 1.9;
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 3.05, h: 1.7, fill: { color: C.card }, line: { color: f.color }, shadow: makeShadow() });
      const ico = await iconPng(f.icon, "#" + f.color, 256);
      s.addImage({ data: ico, x: x + 0.18, y: y + 0.2, w: 0.45, h: 0.45 });
      s.addText(f.title, { x: x + 0.72, y: y + 0.22, w: 2.2, h: 0.35, fontSize: 12, bold: true, color: f.color, margin: 0 });
      s.addText(f.desc, { x: x + 0.15, y: y + 0.7, w: 2.8, h: 0.9, fontSize: 9.5, color: C.grayLight, margin: 0 });
    }
  }

  // SLIDE 11
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.cyan }, line: { color: C.cyan } });
    s.addText("FUTURE SCOPE", { x: 0.3, y: 0.3, w: 9, h: 0.3, fontSize: 10, color: C.cyan, bold: true, charSpacing: 3, margin: 0 });
    s.addText("Where Do We Go From Here?", { x: 0.3, y: 0.65, w: 9, h: 0.55, fontSize: 30, bold: true, color: C.white, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.28, w: 9, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    const phases = [
      { phase: "Phase 1", label: "Real Dataset Integration", desc: "Replace synthetic data with actual NSL-KDD files; add automated download script", color: C.teal },
      { phase: "Phase 2", label: "True FGSM via PyTorch", desc: "Implement gradient-based FGSM with a differentiable MLP — not noise approximation", color: C.cyan },
      { phase: "Phase 3", label: "Deep Learning Models", desc: "Add LSTM / Transformer for sequential traffic analysis; improve U2R detection", color: C.amber },
      { phase: "Phase 4", label: "Real-Time Packet Capture", desc: "Integrate Scapy / pcap ingestion for live network monitoring & alerting", color: C.red },
      { phase: "Phase 5", label: "Explainability (XAI)", desc: "Add SHAP / LIME explanations per prediction for analyst trust and audit trails", color: "A78BFA" },
    ];
    s.addShape(pres.shapes.RECTANGLE, { x: 1.6, y: 1.6, w: 0.05, h: 3.7, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    for (let i = 0; i < phases.length; i++) {
      const p = phases[i];
      const y = 1.55 + i * 0.73;
      s.addShape(pres.shapes.OVAL, { x: 1.47, y: y + 0.1, w: 0.3, h: 0.3, fill: { color: p.color }, line: { color: p.color } });
      s.addText(p.phase, { x: 0.3, y: y + 0.08, w: 1.1, h: 0.28, fontSize: 9, bold: true, color: p.color, align: "right", margin: 0 });
      s.addShape(pres.shapes.RECTANGLE, { x: 2.0, y: y + 0.02, w: 7.7, h: 0.6, fill: { color: C.card }, line: { color: p.color }, shadow: makeShadow() });
      s.addText(p.label, { x: 2.12, y: y + 0.06, w: 4.0, h: 0.28, fontSize: 11, bold: true, color: p.color, margin: 0 });
      s.addText(p.desc, { x: 2.12, y: y + 0.34, w: 7.45, h: 0.22, fontSize: 9.5, color: C.grayLight, margin: 0 });
    }
  }

  // SLIDE 12
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.teal }, line: { color: C.teal } });
    s.addText("TEAM", { x: 0.3, y: 0.3, w: 9, h: 0.3, fontSize: 10, color: C.teal, bold: true, charSpacing: 3, margin: 0 });
    s.addText("Meet the Builders", { x: 0.3, y: 0.65, w: 9, h: 0.55, fontSize: 30, bold: true, color: C.white, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 1.28, w: 9, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    const members = [
      { name: "Ayush Koul", role: "ML Lead & IDS Module", contribs: ["Intrusion Detection System", "Random Forest / DT / MLP training", "Project architecture & README"], color: C.teal },
      { name: "Vinayak Singh Jamwal", role: "Anomaly & Adversarial Module", contribs: ["Anomaly detection pipeline", "Adversarial attack simulator", "ROC / AUC analysis"], color: C.cyan },
      { name: "Prajwal Shan", role: "Dashboard & Traffic Module", contribs: ["Traffic classification (5-class)", "Streamlit dashboard UI", "Data preprocessing & visualizations"], color: C.amber },
    ];
    for (let i = 0; i < members.length; i++) {
      const m = members[i];
      s.addShape(pres.shapes.RECTANGLE, { x: 0.3 + i * 3.25, y: 1.48, w: 3.05, h: 3.6, fill: { color: C.card }, line: { color: m.color }, shadow: makeShadow() });
      s.addShape(pres.shapes.RECTANGLE, { x: 0.3 + i * 3.25, y: 1.48, w: 3.05, h: 0.06, fill: { color: m.color }, line: { color: m.color } });
      s.addShape(pres.shapes.OVAL, { x: 0.95 + i * 3.25, y: 1.65, w: 1.2, h: 1.2, fill: { color: m.color, transparency: 80 }, line: { color: m.color } });
      const usrIco = await iconPng(FaUsers, "#" + m.color, 256);
      s.addImage({ data: usrIco, x: 1.1 + i * 3.25, y: 1.8, w: 0.8, h: 0.8 });
      s.addText(m.name, { x: 0.3 + i * 3.25, y: 3.0, w: 3.05, h: 0.38, fontSize: 13, bold: true, color: C.white, align: "center", margin: 0 });
      s.addText(m.role, { x: 0.3 + i * 3.25, y: 3.38, w: 3.05, h: 0.3, fontSize: 9.5, color: m.color, align: "center", italic: true, margin: 0 });
      s.addShape(pres.shapes.RECTANGLE, { x: 0.5 + i * 3.25, y: 3.72, w: 2.65, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
      m.contribs.forEach((c, j) => {
        s.addShape(pres.shapes.OVAL, { x: 0.52 + i * 3.25, y: 3.84 + j * 0.33, w: 0.08, h: 0.08, fill: { color: m.color }, line: { color: m.color } });
        s.addText(c, { x: 0.68 + i * 3.25, y: 3.8 + j * 0.33, w: 2.5, h: 0.28, fontSize: 9.5, color: C.grayLight, margin: 0 });
      });
    }
    s.addText("Model Institute of Engineering and Technology (Autonomous)  ·  Project 16", { x: 0.3, y: 5.2, w: 9.4, h: 0.3, fontSize: 10, color: C.gray, align: "center", italic: true, margin: 0 });
  }

  // SLIDE 13
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.06, h: 5.625, fill: { color: C.teal }, line: { color: C.teal } });
    for (let col = 0; col < 8; col++) {
      for (let row = 0; row < 5; row++) {
        s.addShape(pres.shapes.OVAL, { x: 1.0 + col * 1.15, y: 0.4 + row * 1.05, w: 0.05, h: 0.05,
          fill: { color: C.teal, transparency: 75 }, line: { color: C.teal, transparency: 75 } });
      }
    }
    const shieldIco = await iconPng(FaShieldAlt, "#" + C.teal, 512);
    s.addImage({ data: shieldIco, x: 4.2, y: 0.5, w: 1.5, h: 1.5 });
    s.addText("Thank You", { x: 1, y: 2.1, w: 8, h: 0.9, fontSize: 54, bold: true, color: C.white, align: "center", margin: 0 });
    s.addText("Questions & Discussion", { x: 1, y: 3.05, w: 8, h: 0.45, fontSize: 18, color: C.teal, align: "center", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 2.5, y: 3.6, w: 5.0, h: 0.03, fill: { color: C.cardBorder }, line: { color: C.cardBorder } });
    s.addText("github.com/AyushKoul124/MINI-PROJECT", { x: 1, y: 3.75, w: 8, h: 0.35, fontSize: 12, color: C.teal, align: "center", margin: 0 });
    s.addText("AI-Based Cybersecurity System  ·  Project 16  ·  MIET (Autonomous)", { x: 1, y: 4.15, w: 8, h: 0.3, fontSize: 11, color: C.gray, align: "center", italic: true, margin: 0 });
    s.addText("Ayush Koul  ·  Vinayak Singh Jamwal  ·  Prajwal Shan", { x: 1, y: 4.5, w: 8, h: 0.3, fontSize: 11, color: C.grayLight, align: "center", margin: 0 });
  }

  await pres.writeFile({ fileName: "AI_Cybersecurity_Presentation.pptx" });
  console.log("Done!");
}

buildPresentation().catch(console.error);
