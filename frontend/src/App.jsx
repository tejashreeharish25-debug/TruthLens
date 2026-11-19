
import { useState } from 'react'

const API_BASE = 'http://localhost:8000'

function App() {
  const [file, setFile] = useState(null)
  const [mediaType, setMediaType] = useState('image')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const mediaOptions = [
    { id: 'image', name: 'Image Analysis', accept: 'image/*', icon: '🖼️' },
    { id: 'video', name: 'Video Analysis', accept: 'video/*', icon: '🎬' },
    { id: 'audio', name: 'Audio Analysis', accept: 'audio/*, video/*', icon: '🎙️' }
  ]

  const selectedOption = mediaOptions.find(option => option.id === mediaType)

  function handleFileChange(event) {
    setFile(event.target.files[0])
    setResult(null)
    setError(null)
  }

  async function handleAnalyze() {
    if (!file) return
    setLoading(true)
    setResult(null)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      if (mediaType === 'audio') {
        // Audio/video → dedicated forensic audio analysis endpoint (returns full forensics)
        const res = await fetch(`${API_BASE}/analyze/audio`, {
          method: 'POST',
          body: formData
        })
        if (!res.ok) {
          const err = await res.json()
          throw new Error(err.detail || 'Audio analysis failed')
        }
        const data = await res.json()
        setResult({
          type: 'audio',
          status: data.message || 'Analysis complete',
          score: data.forensics?.manipulation_score ?? data.forensics?.suspicion_score ?? null,
          confidence: data.forensics?.confidence ?? null,
          transcript: data.forensics?.transcript ?? '',
          segments: data.forensics?.suspicious_segments ?? [],
          acoustic: data.forensics?.acoustic_features ?? {},
          text_forensics: data.forensics?.text_forensics ?? {},
          raw: data
        })
      } else {
        // Image / Video → upload first, then run full /analyze
        const uploadRes = await fetch(`${API_BASE}/upload/${mediaType}`, {
          method: 'POST',
          body: formData
        })
        if (!uploadRes.ok) {
          const err = await uploadRes.json()
          throw new Error(err.detail || 'File upload failed')
        }
        const uploadData = await uploadRes.json()

        const analyzeRes = await fetch(`${API_BASE}/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ [mediaType]: uploadData.filename })
        })
        if (!analyzeRes.ok) {
          const err = await analyzeRes.json()
          throw new Error(err.detail || 'Media analysis failed')
        }
        const analysisData = await analyzeRes.json()
        setResult({ type: mediaType, ...analysisData })
      }

    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  function getScoreColor(score) {
    if (score === null || score === undefined) return '#f39c12'
    if (score < 0.4) return '#2ecc71'
    if (score < 0.7) return '#f39c12'
    return '#e74c3c'
  }

  function getVerdict(score) {
    if (score === null || score === undefined) return '⚠️ Inconclusive'
    if (score < 0.4) return '✅ Likely Authentic'
    if (score < 0.7) return '⚠️ Suspicious — Review Carefully'
    return '🚨 High Deepfake Probability'
  }

  // Extract the most relevant score from the result
  function extractScore(res) {
    if (!res) return null
    if (res.type === 'audio') return res.score
    // image result: res.image?.ai_generated_score or res.image?.manipulation_score
    const img = res.image
    if (img?.ai_generated_score != null) return img.ai_generated_score
    if (img?.manipulation_score != null) return img.manipulation_score
    // confidence object overall score
    if (res.confidence?.overall_score != null) return res.confidence.overall_score
    return null
  }

  const displayScore = extractScore(result)

  return (
    <div className="app">
      <nav className="navbar">
        <h2>TruthLens<span>.</span></h2>
        <div className="nav-links">
          <a href="#">Dashboard</a>
          <a href={`${API_BASE}/docs`} target="_blank" rel="noreferrer">API Docs</a>
          <a href="http://localhost:8501" target="_blank" rel="noreferrer">Full Dashboard</a>
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
          manipulated media and uncover deepfakes.
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
                setError(null)
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
            <small>
              {mediaType === 'image' ? 'JPG, PNG, WEBP' :
               mediaType === 'video' ? 'MP4, AVI, MOV, MKV' :
               'MP3, WAV, MP4, M4A'}
            </small>
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
                {loading ? 'Analyzing...' : `Analyze Media →`}
              </button>
            </div>
          )}

          {error && (
            <div className="result-panel" style={{ borderColor: '#e74c3c' }}>
              <p className="tagline" style={{ color: '#e74c3c' }}>ERROR</p>
              <p>{error}</p>
            </div>
          )}

          {loading && (
            <div className="loading-panel">
              <div className="loader"></div>
              <h3>Analyzing your media...</h3>
              <p>Please wait while TruthLens runs forensic analysis. Audio may take 20–60 seconds.</p>
            </div>
          )}

          {result && !loading && (
            <div className="result-panel">
              <p className="tagline">TRUTHLENS ANALYSIS REPORT</p>
              <h2>Analysis Complete</h2>

              {displayScore !== null ? (
                <>
                  <div className="confidence" style={{ color: getScoreColor(displayScore) }}>
                    {Math.round(displayScore * 100)}%
                  </div>
                  <p style={{ color: getScoreColor(displayScore), fontWeight: 700, fontSize: '1.1rem' }}>
                    {getVerdict(displayScore)}
                  </p>
                  {result.confidence?.overall_score != null && (
                    <p style={{ color: '#9cabc0', marginTop: '0.5rem' }}>
                      Confidence: {Math.round(result.confidence.overall_score * 100)}%
                    </p>
                  )}
                  {result.type === 'audio' && result.confidence != null && (
                    <p style={{ color: '#9cabc0', marginTop: '0.5rem' }}>
                      Model Confidence: {Math.round((result.confidence || 0) * 100)}%
                    </p>
                  )}
                </>
              ) : (
                <p>
                  Analysis completed. An AI-generated score
                  is not available for this media type.
                </p>
              )}

              {/* Audio transcript */}
              {result.transcript && (
                <div style={{ marginTop: '1.5rem', textAlign: 'left', background: '#101e33', padding: '1rem', borderRadius: '10px' }}>
                  <p style={{ color: '#36a8ff', fontWeight: 700, marginBottom: '0.5rem' }}>📝 Transcript</p>
                  <p style={{ color: '#ccc', lineHeight: 1.7, fontSize: '0.95rem' }}>{result.transcript}</p>
                </div>
              )}

              {/* Suspicious segments */}
              {result.segments && result.segments.length > 0 && (
                <div style={{ marginTop: '1rem', textAlign: 'left', background: '#2d1a0d', padding: '1rem', borderRadius: '10px', border: '1px solid #f39c12' }}>
                  <p style={{ color: '#f39c12', fontWeight: 700 }}>⚠️ Suspicious Segments: {result.segments.length}</p>
                  {result.segments.slice(0, 3).map((seg, i) => (
                    <p key={i} style={{ color: '#ccc', fontSize: '0.85rem' }}>
                      {seg.start_time?.toFixed(1)}s – {seg.end_time?.toFixed(1)}s | Score: {(seg.anomaly_score * 100)?.toFixed(0)}%
                    </p>
                  ))}
                </div>
              )}

              <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                <button
                  className="analyze-btn"
                  onClick={() => window.open(`${API_BASE}/report/download`, '_blank')}
                >
                  Download Report ↓
                </button>
                <button
                  className="analyze-btn"
                  style={{ background: '#152947' }}
                  onClick={() => window.open('http://localhost:8501', '_blank')}
                >
                  Open Full Dashboard →
                </button>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
