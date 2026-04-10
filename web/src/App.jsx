import './App.css'
import { useEffect, useMemo, useRef, useState } from 'react'
import brandLogo from './assets/hero.png'

function App() {
  const [askMode, setAskMode] = useState('document')
  const [documentId, setDocumentId] = useState(null)
  const [source, setSource] = useState(null)
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')

  const [url, setUrl] = useState('')
  const [file, setFile] = useState(null)

  const [messages, setMessages] = useState([
    {
      id: crypto.randomUUID(),
      role: 'assistant',
      content:
        'Choose Ask from PDF/Text for document-grounded answers, or Basic Chat for general questions.',
    },
  ])
  const [question, setQuestion] = useState('')
  const [isBusy, setIsBusy] = useState(false)

  const listRef = useRef(null)

  useEffect(() => {
    const el = listRef.current
    if (!el) return
    el.scrollTop = el.scrollHeight
  }, [messages.length, isBusy])

  const canAsk = useMemo(() => {
    if (isBusy || question.trim().length === 0) return false
    if (askMode === 'document') return Boolean(documentId)
    return true
  }, [askMode, documentId, question, isBusy])

  async function readJsonOrText(res) {
    const text = await res.text()
    if (!text) return { json: null, text: '' }
    try {
      return { json: JSON.parse(text), text }
    } catch {
      return { json: null, text }
    }
  }

  async function ingestUrl() {
    setError('')
    setStatus('')
    if (!url.trim()) {
      setError('Please enter a URL.')
      return
    }
    setIsBusy(true)
    setStatus('Ingesting website…')
    try {
      const res = await fetch('/ingest/url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      })
      const { json, text } = await readJsonOrText(res)
      if (!res.ok) throw new Error(json?.detail || text || `Failed to ingest URL (HTTP ${res.status}).`)
      setDocumentId(json.document_id)
      setSource(json.source)
      setStatus(`Ingested: ${json.source} (${json.chunk_count} chunks)`)
    } catch (e) {
      setError(e.message || String(e))
    } finally {
      setIsBusy(false)
    }
  }

  async function ingestFile() {
    setError('')
    setStatus('')
    if (!file) {
      setError('Please choose a file.')
      return
    }
    setIsBusy(true)
    setStatus('Uploading and ingesting file…')
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch('/ingest/file', { method: 'POST', body: form })
      const { json, text } = await readJsonOrText(res)
      if (!res.ok) throw new Error(json?.detail || text || `Failed to ingest file (HTTP ${res.status}).`)
      setDocumentId(json.document_id)
      setSource(json.source)
      setStatus(`Ingested: ${json.source} (${json.chunk_count} chunks)`)
    } catch (e) {
      setError(e.message || String(e))
    } finally {
      setIsBusy(false)
    }
  }

  async function sendQuestion() {
    const q = question.trim()
    if (askMode === 'document' && !documentId) {
      setError('Ingest something first (file or URL).')
      return
    }
    if (!q) return

    setError('')
    setStatus('')
    setQuestion('')

    const userMsg = { id: crypto.randomUUID(), role: 'user', content: q }
    setMessages((m) => [...m, userMsg])

    setIsBusy(true)
    try {
      const endpoint = askMode === 'document' ? '/ask' : '/chat/basic'
      const payload =
        askMode === 'document'
          ? { document_id: documentId, question: q, top_k: 10 }
          : { message: q }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const { json, text } = await readJsonOrText(res)
      if (!res.ok) throw new Error(json?.detail || text || `Failed to answer (HTTP ${res.status}).`)

      const assistantMsg = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: json.answer,
        sources: Array.isArray(json.sources) ? json.sources : [],
      }
      setMessages((m) => [...m, assistantMsg])
    } catch (e) {
      setMessages((m) => [
        ...m,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: `Error: ${e.message || String(e)}`,
          isError: true,
        },
      ])
    } finally {
      setIsBusy(false)
    }
  }

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebarInner">
          <div className="brand">
            <img className="brandLogo" src={brandLogo} alt="Brand logo" />
            <div>
              <div className="brandTitle">RAGNexus</div>
            </div>
          </div>

          <div className="modeCard">
            <div className="cardTitle">Ask Mode</div>
            <div className="modeToggle" role="tablist" aria-label="Ask mode">
              <button
                className={`modeBtn ${askMode === 'document' ? 'active' : ''}`}
                onClick={() => setAskMode('document')}
                type="button"
              >
                Ask from PDF/Text
              </button>
              <button
                className={`modeBtn ${askMode === 'basic' ? 'active' : ''}`}
                onClick={() => setAskMode('basic')}
                type="button"
              >
                Basic Chat
              </button>
            </div>
            <p className="modeHint">
              {askMode === 'document'
                ? 'Answers are retrieved only from your ingested document.'
                : 'Use this for general chat questions.'}
            </p>
          </div>

          <div className="card">
            <div className="cardTitle">Ingest</div>

            <div className="field">
              <label>Upload file (PDF/TXT/CSV)</label>
              <input
                type="file"
                accept=".pdf,.txt,.csv"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                disabled={isBusy}
              />
              <button className="btn" onClick={ingestFile} disabled={isBusy || !file}>
                Ingest file
              </button>
            </div>

            <div className="divider" />

            <div className="field">
              <label>Website URL</label>
              <input
                type="url"
                placeholder="https://example.com/docs"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isBusy}
              />
              <button className="btn" onClick={ingestUrl} disabled={isBusy || !url.trim()}>
                Ingest URL
              </button>
            </div>
          </div>

          <div className="card">
            <div className="cardTitle">Active document</div>
            <div className="kv">
              <div className="k">document_id</div>
              <div className="v mono">{documentId || '—'}</div>
            </div>
            <div className="kv">
              <div className="k">source</div>
              <div className="v">{source || '—'}</div>
            </div>
            {status ? <div className="note ok">{status}</div> : null}
            {error ? <div className="note err">{error}</div> : null}
          </div>
        </div>
      </aside>

      <main className="chat">
        <header className="chatHeader">
          <div className="chatTitle">Chat Workspace</div>
          <div className="chatHint">
            {askMode === 'document'
              ? documentId
                ? 'Document mode is on: answers come only from your ingested source.'
                : 'Ingest a file or URL, then ask from PDF/Text.'
              : 'Basic chat mode is on: ask general questions.'}
          </div>
        </header>

        <div className="messages" ref={listRef}>
          {messages.map((m) => (
            <div key={m.id} className={`msgRow ${m.role}`}>
              <div className={`msg ${m.isError ? 'error' : ''}`}>
                <div className="msgRole">{m.role === 'user' ? 'You' : 'Assistant'}</div>
                <div className="msgText">{m.content}</div>

                {m.role === 'assistant' && m.sources?.length ? (
                  <div className="sources">
                    <div className="sourcesTitle">Sources</div>
                    <ol className="sourcesList">
                      {m.sources.map((s, idx) => (
                        <li key={s.chunk_id || idx} className="sourceItem">
                          <div className="sourceTop">
                            <span className="pill">{s.source || 'unknown source'}</span>
                            {s.page_number !== null && s.page_number !== undefined ? (
                              <span className="pill">page {s.page_number}</span>
                            ) : null}
                          </div>
                          <div className="sourceText mono">{String(s.text || '').slice(0, 260)}{String(s.text || '').length > 260 ? '…' : ''}</div>
                        </li>
                      ))}
                    </ol>
                  </div>
                ) : null}
              </div>
            </div>
          ))}

          {isBusy ? (
            <div className="msgRow assistant">
              <div className="msg">
                <div className="msgRole">Assistant</div>
                <div className="msgText muted">Working…</div>
              </div>
            </div>
          ) : null}
        </div>

        <div className="composer">
          <textarea
            className="input"
            placeholder={
              askMode === 'document'
                ? documentId
                  ? 'Ask from your ingested document…'
                  : 'Ingest something first…'
                : 'Say hi or hello…'
            }
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => {
              if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') sendQuestion()
            }}
            disabled={isBusy}
          />
          <button className="btn primary" onClick={sendQuestion} disabled={!canAsk}>
            {askMode === 'document' ? 'Ask from PDF/Text' : 'Send'}
          </button>
        </div>
      </main>
    </div>
  )
}

export default App
