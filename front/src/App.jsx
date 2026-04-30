import { useState, useRef } from 'react'
import './index.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)
  const conversationIdRef = useRef(null)

  async function sendMessage() {
    if (!prompt.trim() || loading) return

    setLoading(true)
    setResponse('')

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt,
          conversation_id: conversationIdRef.current,
        }),
      })
      const data = await res.json()
      conversationIdRef.current = data.conversation_id
      setResponse(data.response)
    } catch {
      setResponse('Erreur : impossible de joindre le serveur.')
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      sendMessage()
    }
  }

  return (
    <div className="container">
      <h1>Secure Bot</h1>
      <textarea
        className="prompt-input"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Écris ton message ici... (Ctrl+Entrée pour envoyer)"
        rows={6}
        disabled={loading}
      />
      <button className="send-btn" onClick={sendMessage} disabled={loading}>
        {loading ? 'Envoi...' : 'Envoyer'}
      </button>
      {response && (
        <div className="response-box">
          <p>{response}</p>
        </div>
      )}
    </div>
  )
}

export default App
