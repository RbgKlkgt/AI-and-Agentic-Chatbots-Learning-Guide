import { useState, useRef, useEffect } from 'react'
import './index.css'

const API_URL = 'http://localhost:8000'

function App() {
  const [prompt, setPrompt] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const conversationIdRef = useRef(null)
  const historyEndRef = useRef(null)

  useEffect(() => {
    historyEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function sendMessage() {
    if (!prompt.trim() || loading) return

    const userText = prompt.trim()
    setMessages((prev) => [...prev, { role: 'user', text: userText }])
    setPrompt('')
    setLoading(true)

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: userText,
          conversation_id: conversationIdRef.current,
        }),
      })
      const data = await res.json()
      conversationIdRef.current = data.conversation_id
      setMessages((prev) => [...prev, { role: 'agent', text: data.response }])
    } catch {
      setMessages((prev) => [...prev, { role: 'agent', text: 'Erreur : impossible de joindre le serveur.' }])
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
      <div className="chat-history">
        {messages.map((msg, i) => (
          <div key={i} className={`msg-bubble ${msg.role === 'user' ? 'msg-user' : 'msg-agent'}`}>
            {msg.text}
          </div>
        ))}
        {loading && <div className="msg-bubble msg-agent msg-loading">…</div>}
        <div ref={historyEndRef} />
      </div>
      <textarea
        className="prompt-input"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Écris ton message ici... (Ctrl+Entrée pour envoyer)"
        rows={4}
        disabled={loading}
      />
      <button className="send-btn" onClick={sendMessage} disabled={loading}>
        {loading ? 'Envoi...' : 'Envoyer'}
      </button>
    </div>
  )
}

export default App
