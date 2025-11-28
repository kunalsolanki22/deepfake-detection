import { Database, BrainCircuit, Activity, CloudCog, Lock, Trophy } from 'lucide-react';

export const projectMilestones = [
  {
    week: "Weeks 1-4",
    title: "Foundation & DataOps",
    desc: "Established the Data pipeline. Integrated DVC with Google Drive Remote to handle 26GB of FaceForensics++ & Celeb-DF v2 datasets. Implemented Git version control.",
    icon: Database,
    stats: "26GB Data • DVC Integrated",
    color: "#3b82f6"
  },
  {
    week: "Weeks 5-6",
    title: "Architecture & Preprocessing",
    desc: "Selected XceptionNet as baseline. Implemented MediaPipe for face extraction and Albumentations (Compression, Noise, Dropout) to simulate real-world deepfake artifacts.",
    icon: BrainCircuit,
    stats: "Albumentations • MediaPipe ROI",
    color: "#8b5cf6"
  },
  {
    week: "Weeks 7-8",
    title: "Optimization (Optuna)",
    desc: "Detected overfitting at 80% accuracy. Implemented Optuna HPO to tune LR, Dropout, and Augmentation strengths. Validated hypothesis via 10 trials.",
    icon: Activity,
    stats: "Acc: 80% ➝ 85.5% • 10 Trials",
    color: "#f59e0b"
  },
  {
    week: "Week 9",
    title: "SOTA Performance",
    desc: "Executed final training run. Achieved definitive convergence with Test Loss: 0.1966. Confusion Matrix confirmed low false positive rate.",
    icon: Trophy,
    stats: "95.52% Accuracy • 0.9908 AUC",
    color: "#10b981"
  },
  {
    week: "Week 10",
    title: "MLOps Migration",
    desc: "Migrated Remote Storage from Google Drive to AWS S3 for production scalability. Finalized inference pipeline with Percentile Aggregation.",
    icon: CloudCog,
    stats: "AWS S3 • Scalable Pipeline",
    color: "#ec4899"
  }
];

export const finalMetrics = {
  accuracy: "93.52%",
  auc: "0.9908",
  precision: "92.59%",
  recall: "94.65%"
};
