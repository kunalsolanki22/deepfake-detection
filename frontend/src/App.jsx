import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Upload, Fingerprint, AlertTriangle, CheckCircle2, BarChart3, ChevronDown, 
  Cpu, Zap, Database, ArrowRight, FileVideo, ScanFace, Wand2, BrainCircuit, Sigma, Eye
} from 'lucide-react';
import { VerticalTimeline, VerticalTimelineElement } from 'react-vertical-timeline-component';
import 'react-vertical-timeline-component/style.min.css';
import { projectMilestones, finalMetrics } from './data/projectData';
import './App.css';

const METRICS = [
  { label: "Test Accuracy", value: finalMetrics.accuracy, icon: <Zap size={20} />, color: "#10b981" },
  { label: "ROC - AUC", value: finalMetrics.auc, icon: <BarChart3 size={20} />, color: "#3b82f6" },
  { label: "Precision", value: finalMetrics.precision, icon: <CheckCircle2 size={20} />, color: "#8b5cf6" },
  { label: "Recall", value: finalMetrics.recall, icon: <Fingerprint size={20} />, color: "#f59e0b" },
];

const PIPELINE_STEPS = [
  { id: 1, title: "Input Ingestion", short: "MP4/AVI Upload", detail: "User uploads raw video. System validates codec/format and initializes the frame buffer.", icon: <FileVideo size={24} /> },
  { id: 2, title: "Smart Preprocessing", short: "MediaPipe ROI Crop", detail: "Extracts 1 frame every 10 frames. MediaPipe detects facial landmarks to crop & align inputs.", icon: <ScanFace size={24} /> },
  { id: 3, title: "Noise Robustness", short: "Albumentations", detail: "Applies Gaussian noise & compression simulation to match real-world artifacts.", icon: <Wand2 size={24} /> },
  { id: 4, title: "Deep Inference", short: "XceptionNet (Optuna)", detail: "Fine-tuned Xception backbone analyzes texture patterns to assign 'Fake Probability'.", icon: <BrainCircuit size={24} /> },
  { id: 5, title: "Temporal Aggregation", short: "Percentile Pooling", detail: "Frame scores aggregated using 70th Percentile method to filter outliers.", icon: <Sigma size={24} /> },
];

const sectionVariants = {
  hidden: { opacity: 0, y: 50 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.8, ease: "easeOut" } }
};

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [scannedFrames, setScannedFrames] = useState([]);
  const [frameIndex, setFrameIndex] = useState(0);
  const [error, setError] = useState(null);

  // --- SAFE Client-Side Frame Extraction ---
  const extractFrames = (videoFile) => {
    try {
      const url = URL.createObjectURL(videoFile);
      const video = document.createElement('video');
      video.src = url;
      video.muted = true;
      video.playsInline = true; // Important for some browsers
      video.crossOrigin = "anonymous";
      
      // Fallback if video doesn't load visuals quickly
      const timeout = setTimeout(() => {
        if (scannedFrames.length === 0) setScannedFrames(["https://via.placeholder.com/320x180/000000/00ff00?text=Scanning..."]);
      }, 2000);

      video.onloadeddata = async () => {
        clearTimeout(timeout);
        const frames = [];
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = 320; canvas.height = 180;

        for (let i = 0; i < 10; i++) {
          video.currentTime = (video.duration / 10) * i;
          await new Promise(r => video.onseeked = r);
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
          frames.push(canvas.toDataURL());
        }
        setScannedFrames(frames);
      };
      
      video.onerror = () => {
        // Fallback for unsupported codecs
        setScannedFrames(["https://via.placeholder.com/320x180/000000/ffffff?text=Video+Format+Unsupported+for+Preview"]);
      };
    } catch (e) {
      console.warn("Visual preview failed", e);
    }
  };

  useEffect(() => {
    if (loading && scannedFrames.length > 0) {
      const interval = setInterval(() => {
        setFrameIndex(prev => (prev + 1) % scannedFrames.length);
      }, 120);
      return () => clearInterval(interval);
    }
  }, [loading, scannedFrames]);

  const handleUpload = async (e) => {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f); setLoading(true); setResult(null); setError(null); setScannedFrames([]);
    
    extractFrames(f);

    const formData = new FormData();
    formData.append('file', f);

    try {
      const [res] = await Promise.all([
        fetch('http://127.0.0.1:8000/predict_video/', { method: 'POST', body: formData }),
        new Promise(r => setTimeout(r, 2000)) // Min 2s delay for UX
      ]);
      
      if (!res.ok) throw new Error(`Server Error: ${res.status}`);
      
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to connect to backend.");
    } finally {
      setLoading(false);
    }
  };

  const scrollToDemo = () => document.getElementById('live-demo').scrollIntoView({ behavior: 'smooth' });

  return (
    <div className="app-root">
      <nav className="navbar">
        <div className="nav-logo"><Fingerprint size={24} className="text-accent"/> DeepSentinel</div>
        <div className="nav-links">
          <a href="#pipeline">Pipeline</a>
          <a href="#metrics">Metrics</a>
          <button className="nav-cta" onClick={scrollToDemo}>Live Demo</button>
        </div>
      </nav>

      <header className="hero-section">
        <div className="hero-bg-glow" />
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }} className="hero-content">
          <div className="badge-pill"><span className="dot"></span> AI Forensics v2.0</div>
          <h1 className="hero-title">Detect <span className="text-gradient">DeepFakes</span> with <br/> Precision AI</h1>
          <p className="hero-subtitle">Advanced video forensics powered by <strong>Optuna-Optimized XceptionNet</strong>. Combating digital misinformation with <strong>95.5% accuracy</strong>.</p>
          <button className="cta-button" onClick={scrollToDemo}>Launch Live Demo <ArrowRight size={20} /></button>
        </motion.div>
        <ChevronDown className="scroll-hint" size={32} />
      </header>

      <motion.section id="pipeline" className="info-section" initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-100px" }} variants={sectionVariants}>
        <h2 className="section-header">Inference Workflow</h2>
        <div className="pipeline-container">
          <div className="pipeline-line"><div className="line-pulse"></div></div>
          <div className="pipeline-track">
            {PIPELINE_STEPS.map((step, i) => (
              <motion.div key={i} className="pipeline-card" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.15 }} whileHover={{ scale: 1.05, zIndex: 10 }}>
                <div className="step-badge">{step.id}</div>
                <div className="step-icon-wrapper">{step.icon}</div>
                <h3 className="step-title">{step.title}</h3>
                <p className="step-short">{step.short}</p>
                <div className="step-detail"><p>{step.detail}</p></div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.section>

      <motion.section id="metrics" className="metrics-section" initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-100px" }} variants={sectionVariants}>
        <h2 className="section-header">Evaluation Metrics</h2>
        <div className="metrics-grid">
          {METRICS.map((m, i) => (
            <div key={i} className="metric-card">
              <div className="metric-icon" style={{ color: m.color, background: `${m.color}20` }}>{m.icon}</div>
              <div className="metric-value" style={{ color: m.color }}>{m.value}</div>
              <div className="metric-label">{m.label}</div>
            </div>
          ))}
        </div>
      </motion.section>

      <motion.section id="live-demo" className="demo-section" initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-100px" }} variants={sectionVariants}>
        <h2 className="section-header"><Fingerprint className="text-accent" style={{marginRight:'10px'}}/> Live Analysis Tool</h2>
        <div className="detector-stage">
          
          {!loading && !result && (
            <div className="upload-container" onClick={() => document.getElementById('vid-upload').click()}>
              <input type="file" id="vid-upload" hidden accept="video/*" onChange={handleUpload} />
              <div className="upload-circle"><Upload size={40} className="icon-upload" /></div>
              <h3>Click to Analyze Footage</h3>
              <p>Supports MP4, AVI, MOV • Max 50MB</p>
            </div>
          )}

          {loading && (
            <div className="scanner-container">
              <div className="scan-viewport">
                {scannedFrames.length > 0 ? (
                  <img src={scannedFrames[frameIndex]} className="scan-video-frame" alt="scanning" />
                ) : (
                  <div className="scan-placeholder" />
                )}
                <div className="scan-overlay-grid" /><div className="scan-laser" />
              </div>
              <div className="scan-terminal">
                <div className="terminal-line"> Initializing MediaPipe Face Detector...</div>
                <div className="terminal-line"> Extracting ROI (Region of Interest)...</div>
                <div className="terminal-line"> Applying XceptionNet Inference...</div>
                <div className="terminal-line"> Calculating Probability Distribution...</div>
              </div>
            </div>
          )}

          {result && (
            <div className={`result-hud ${result.label === 'Fake' ? 'hud-fake' : 'hud-real'}`}>
              <div className="hud-header">
                <div className="hud-icon">{result.label === 'Fake' ? <AlertTriangle size={32}/> : <CheckCircle2 size={32}/>}</div>
                <div><h2>{result.label.toUpperCase()} DETECTED</h2><p className="hud-sub">Analysis Complete</p></div>
              </div>
              
              <div className="hud-body">
                <div className="confidence-row"><span>Confidence Score</span><span className="conf-value">{(result.confidence * 100).toFixed(2)}%</span></div>
                <div className="progress-track"><div className="progress-fill" style={{ width: `${result.confidence * 100}%` }}/></div>
                
                {/* FORENSIC EVIDENCE GRID */}
                {result.frames && result.frames.length > 0 && (
                  <div className="evidence-container">
                    <h4 className="evidence-title"><Eye size={16} /> Forensic Evidence (Analyzed Frames)</h4>
                    <div className="evidence-grid">
                      {result.frames.map((frame, i) => (
                        <div key={i} className="evidence-frame">
                          <img src={`data:image/jpeg;base64,${frame}`} alt="Evidence" />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="meta-info"><span>Processed by: XceptionNet-Optuna</span><span>Pipeline: AWS S3 / DVC</span></div>
              </div>
              <button className="btn-reset" onClick={() => {setResult(null); setFile(null);}}>Analyze Another Video</button>
            </div>
          )}

          {error && <div className="error-box"><p>⚠️ {error}</p><button onClick={() => setError(null)}>Try Again</button></div>}
        </div>
      </motion.section>

      <motion.section id="roadmap" className="timeline-section" initial="hidden" whileInView="visible" viewport={{ once: true, margin: "-100px" }} variants={sectionVariants}>
        <h2 className="section-header">Development Roadmap</h2>
        <VerticalTimeline lineColor="#334155">
          {projectMilestones.map((m, i) => (
            <VerticalTimelineElement key={i} contentStyle={{ background: '#1e293b', color: '#fff', border: `1px solid ${m.color}` }} contentArrowStyle={{ borderRight: `7px solid ${m.color}` }} date={m.date} iconStyle={{ background: m.color, color: '#fff' }} icon={<m.icon />}>
              <h3 style={{fontSize:'1.1rem', fontWeight:'700'}}>{m.title}</h3>
              <p style={{fontSize:'0.9rem', color:'#cbd5e1'}}>{m.desc}</p>
            </VerticalTimelineElement>
          ))}
        </VerticalTimeline>
      </motion.section>

      <footer className="app-footer"><p>B.Tech Minor Project • Dept. of Computer Science • 2025</p></footer>
    </div>
  );
}

export default App;