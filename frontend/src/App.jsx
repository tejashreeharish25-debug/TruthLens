
import { useState } from 'react'

function App() {
  const [file, setFile] = useState(null)
  const [mediaType, setMediaType] = useState('image')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const mediaOptions = [
    { id: 'image', name: 'Image Analysis', accept: 'image/*', icon: '\u{1F5BC}\u{FE0F}' },
    { id: 'video', name: 'Video Analysis', accept: 'video/*', icon: '\u{1F3AC}' },
    { id: 'audio', name: 'Audio Analysis', accept: 'audio/*', icon: '\u{1F3A7}' }
  ]

  const selectedOption = mediaOptions.find(
    option => option.id === mediaType
  )

  function handleFileChange(event) {
    setFile(event.target.files[0])
    setResult(null)
  }

  async function handleAnalyze() {
    if (!file) return

    setLoading(true)
    setResult(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const uploadResponse = await fetch(`/upload/${mediaType}`, {
        method: 'POST',
        body: formData
      })

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json()
        throw new Error(errorData.detail || 'File upload failed')
      }

      const uploadData = await uploadResponse.json()

      const analyzeResponse = await fetch('/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          [mediaType]: uploadData.filename
        })
      })

      if (!analyzeResponse.ok) {
        const errorData = await analyzeResponse.json()
        throw new Error(errorData.detail || 'Media analysis failed')
      }

      const analysisData = await analyzeResponse.json()
      setResult(analysisData)

    } catch (error) {
      alert(error.message)
    } finally {
      setLoading(false)
    }
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
            <span>{'\u{2B06}'}</span>
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
                {loading ? 'Analyzing...' : `Analyze Media ${'\u{2192}'}`}
              </button>
            </div>
          )}

          {loading && (
            <div className="loading-panel">
              <div className="loader"></div>
              <h3>Analyzing your media...</h3>
              <p>Please wait while the analysis runs.</p>
            </div>
          )}

          {result && (
            <div className="result-panel">
              <p className="tagline">TRUTHLENS ANALYSIS REPORT</p>
              <h2>Analysis Complete</h2>

              {result.image?.ai_generated_score != null ? (
                <>
                  <div className="confidence">
                    {(result.image.ai_generated_score * 100).toFixed(2)}%
                  </div>
                  <p>AI-generated score</p>
                </>
              ) : (
                <p>
                  Analysis completed. An AI-generated image score
                  is not available for this media type.
                </p>
              )}

              <button
                className="analyze-btn"
                onClick={() => window.open('/report/download', '_blank')}
              >
                Download Report {'\u{2193}'}
              </button>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
