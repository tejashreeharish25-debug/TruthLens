
import { useState } from 'react'

function App() {
  const [file, setFile] = useState(null)
  const [mediaType, setMediaType] = useState('image')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const mediaOptions = [
    { id: 'image', name: 'Image Analysis', accept: 'image/*', icon: '🖼️' },
    { id: 'video', name: 'Video Analysis', accept: 'video/*', icon: '🎬' },
    { id: 'audio', name: 'Audio Analysis', accept: 'audio/*', icon: '🎧' }
  ]

  const selectedOption = mediaOptions.find(
    option => option.id === mediaType
  )

  function handleFileChange(event) {
    setFile(event.target.files[0])
    setResult(null)
  }

  function handleAnalyze() {
    if (!file) return

    setLoading(true)
    setResult(null)

    setTimeout(() => {
      setLoading(false)
      setResult({
        status: 'Demo analysis complete',
        confidence: 94.5,
        explanation: 'This is a simulated result for frontend testing. No actual AI detection has been performed.'
      })
    }, 2500)
  }

  return (
    <div className="app">
      <nav className="navbar">
        <h2>TruthLens<span>.</span></h2>
        <div className="nav-links">
          <a href="#">Dashboard</a>
          <a href="#">About</a>
        </div>
      </nav>

      <main className="hero">
        <p className="tagline">AI-POWERED DIGITAL FORENSICS</p>

        <h1>
          Discover the <span>Truth.</span>
          <br />
          Verify What You See.
        </h1>

        <p className="description">
          Analyze images, videos and audio to detect
          manipulated media and uncover misinformation.
        </p>

        <div className="upload-options">
          {mediaOptions.map(option => (
            <button
              className={`upload-card ${mediaType === option.id ? 'active' : ''}`}
              key={option.id}
              onClick={() => {
                setMediaType(option.id)
                setFile(null)
                setResult(null)
              }}
            >
              <h3>{option.icon} {option.name}</h3>
              <p>Select to analyze {option.id} files</p>
            </button>
          ))}
        </div>

        <section className="upload-section">
          <h2>Upload Your Media</h2>
          <p>Selected mode: {selectedOption.name}</p>

          <label className="file-upload">
            <span>＋</span>
            <strong>Choose a {mediaType} file</strong>
            <small>Supported formats depend on your browser</small>

            <input
              type="file"
              accept={selectedOption.accept}
              onChange={handleFileChange}
            />
          </label>

          {file && (
            <div className="file-info">
              <p>Selected file: {file.name}</p>
              <p>Size: {(file.size / (1024 * 1024)).toFixed(2)} MB</p>

              <button
                className="analyze-btn"
                onClick={handleAnalyze}
                disabled={loading}
              >
                {loading ? 'Analyzing...' : 'Analyze Media →'}
              </button>
            </div>
          )}

          {loading && (
            <div className="loading-panel">
              <div className="loader"></div>
              <h3>Analyzing your media...</h3>
              <p>Please wait while the demo runs.</p>
            </div>
          )}

          {result && (
            <div className="result-panel">
              <p className="tagline">DEMO RESULT — NOT AI VERIFIED</p>
              <h2>{result.status}</h2>
              <div className="confidence">
                {result.confidence}%
              </div>
              <p>{result.explanation}</p>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
