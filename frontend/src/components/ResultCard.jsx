import { useState, useEffect } from 'react'
import './ResultCard.css'

const ResultCard = ({ result, onReset }) => {
  const [showJson, setShowJson] = useState(false)
  const [confettiActive, setConfettiActive] = useState(false)
  const isReal = result.label === 'Real'
  const confidencePercent = (result.confidence * 100).toFixed(1)

  useEffect(() => {
    // Trigger confetti animation
    setConfettiActive(true)
    const timer = setTimeout(() => setConfettiActive(false), 2000)
    return () => clearTimeout(timer)
  }, [result.label])

  return (
    <div className={`result-card ${isReal ? 'result-real' : 'result-fake'}`}>
      <div className={`result-glow ${isReal ? 'glow-green' : 'glow-red'}`}></div>
      
      {confettiActive && (
        <div className="confetti-container">
          {[...Array(20)].map((_, i) => (
            <div
              key={i}
              className={`confetti confetti-${i}`}
              style={{
                '--delay': `${i * 0.1}s`,
                '--color': isReal ? '#10b981' : '#ef4444',
              }}
            />
          ))}
        </div>
      )}

      <div className="result-content">
        <div className={`result-label ${isReal ? 'label-real' : 'label-fake'}`}>
          <span className="label-icon">{isReal ? '✓' : '⚠'}</span>
          <span className="label-text">{result.label}</span>
        </div>

        <div className="confidence-section">
          <div className="confidence-header">
            <span>Confidence Score</span>
            <span className="confidence-percent">{confidencePercent}%</span>
          </div>
          
          <div className="progress-container">
            <div
              className={`progress-bar ${isReal ? 'progress-real' : 'progress-fake'}`}
              style={{ width: `${result.confidence * 100}%` }}
            >
              <div className="progress-shine"></div>
            </div>
          </div>

          <div className="circular-progress-wrapper">
            <svg className="circular-progress" viewBox="0 0 120 120">
              <circle
                className="progress-bg"
                cx="60"
                cy="60"
                r="54"
                fill="none"
                stroke="rgba(255,255,255,0.1)"
                strokeWidth="8"
              />
              <circle
                className={`progress-circle ${isReal ? 'circle-real' : 'circle-fake'}`}
                cx="60"
                cy="60"
                r="54"
                fill="none"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${2 * Math.PI * 54}`}
                strokeDashoffset={`${2 * Math.PI * 54 * (1 - result.confidence)}`}
                transform="rotate(-90 60 60)"
              />
            </svg>
            <div className="circular-progress-text">{confidencePercent}%</div>
          </div>
        </div>

        <div className="result-details">
          <div className="detail-item">
            <span className="detail-label">File:</span>
            <span className="detail-value">{result.filename}</span>
          </div>
          {result.processed_by && (
            <div className="detail-item">
              <span className="detail-label">Model:</span>
              <span className="detail-value">{result.processed_by}</span>
            </div>
          )}
        </div>

        <div className="result-actions">
          <button
            className="action-button secondary"
            onClick={() => setShowJson(!showJson)}
          >
            {showJson ? 'Hide' : 'View'} JSON
          </button>
          <button className="action-button primary" onClick={onReset}>
            Try Another Video
          </button>
        </div>

        {showJson && (
          <div className="json-section">
            <pre className="json-content">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}

export default ResultCard

