import { useState, useRef } from 'react'
import './UploadBox.css'

const UploadBox = ({ onUpload, file, loading, disabled }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [dragCounter, setDragCounter] = useState(0)
  const fileInputRef = useRef(null)

  const validateFile = (file) => {
    if (!file) return false
    if (!file.type.startsWith('video/')) {
      alert('Please upload a video file (mp4, avi, mov, etc.)')
      return false
    }
    return true
  }

  const handleFileSelect = (selectedFile) => {
    if (validateFile(selectedFile)) {
      onUpload(selectedFile)
    }
  }

  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragCounter((prev) => prev + 1)
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true)
    }
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragCounter((prev) => {
      const newCounter = prev - 1
      if (newCounter === 0) {
        setIsDragging(false)
      }
      return newCounter
    })
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    setDragCounter(0)

    if (disabled || loading) return

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleFileInputChange = (e) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleClick = () => {
    if (!disabled && !loading) {
      fileInputRef.current?.click()
    }
  }

  return (
    <div className="upload-box-container">
      <div
        className={`drop-area ${isDragging ? 'dragging' : ''} ${disabled || loading ? 'disabled' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
          disabled={disabled || loading}
        />

        <div className="drop-area-content">
          {loading ? (
            <>
              <div className="upload-icon loading">📹</div>
              <p className="drop-text">Processing video...</p>
            </>
          ) : file ? (
            <>
              <div className="upload-icon">✅</div>
              <p className="drop-text">Selected: {file.name}</p>
              <p className="drop-hint">Drop another file or click to change</p>
            </>
          ) : (
            <>
              <div className="upload-icon">📹</div>
              <p className="drop-text">
                Drag and drop your video here, or click to browse
              </p>
              <p className="drop-hint">Supports: MP4, AVI, MOV, and other video formats</p>
            </>
          )}
        </div>

        <button
          className="upload-button"
          onClick={handleClick}
          disabled={disabled || loading}
        >
          {file ? 'Change Video' : 'Select Video File'}
        </button>
      </div>
    </div>
  )
}

export default UploadBox

