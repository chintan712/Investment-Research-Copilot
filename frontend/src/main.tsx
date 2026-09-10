import { StrictMode, useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';

type Citation = { document: string; page: number };
type ChatResponse = { answer: string; sources: Citation[]; usage: { model?: string; total_tokens?: number; retrieved_chunks: number; latency_ms: number }; tool_calls: { tool: string; result: number }[] };
type Document = { id: number; filename: string; document_type?: string; uploaded_at: string };
type RequestHistory = { id: number; timestamp: string; question: string; model?: string; total_tokens?: number; retrieved_chunks: number; latency_ms: number; response: string };

const API = 'http://localhost:8000';

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [history, setHistory] = useState<RequestHistory[]>([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [documentType, setDocumentType] = useState('research');
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | null>(null);
  const [error, setError] = useState('');

  const loadDocuments = () => fetch(`${API}/documents`).then((response) => response.json()).then((items: Document[]) => { setDocuments(items); setSelectedDocumentId((current) => current !== null && items.some((item) => item.id === current) ? current : null); }).catch(() => setError('Backend is unavailable. Start the API and try again.'));
  const loadHistory = () => fetch(`${API}/requests`).then((response) => response.json()).then(setHistory).catch(() => undefined);

  useEffect(() => { loadDocuments(); loadHistory(); }, []);

  async function upload(file: File) {
    setUploading(true);
    setError('');
    const body = new FormData();
    body.append('file', file);
    body.append('document_type', documentType);
    try {
      const response = await fetch(`${API}/documents/upload`, { method: 'POST', body });
      if (!response.ok) throw new Error((await response.json()).detail || 'Upload failed');
      const uploaded: Document = await response.json();
      setSelectedDocumentId(uploaded.id);
      await loadDocuments();
    } catch (reason) {
      setError(String(reason));
    } finally {
      setUploading(false);
    }
  }

  async function ask() {
    if (!question.trim()) return;
    setLoading(true);
    setError('');
    try {
      const response = await fetch(`${API}/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question, document_id: selectedDocumentId }) });
      if (!response.ok) throw new Error((await response.json()).detail);
      setAnswer(await response.json());
      await loadHistory();
    } catch (reason) {
      setError(String(reason));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header><p className="kicker">INTERNAL RESEARCH WORKSPACE</p><h1>Investment Research<br /><em>Copilot</em></h1><p className="lede">Grounded answers for fictional deal teams, with every claim tied back to the source material.</p></header>
      <section className="workspace">
        <aside>
          <div className="section-title"><span>01 / Evidence</span><span>{uploading ? 'Uploading...' : `${documents.length} PDF sources`}</span></div>
          <div className="upload-controls">
            <select value={documentType} onChange={(event) => setDocumentType(event.target.value)} disabled={uploading} aria-label="Document type">
              <option value="research">Research document</option><option value="financials">Financials</option><option value="management">Management presentation</option><option value="risk">Risk report</option>
            </select>
            <label className="upload">{uploading ? 'Processing PDF...' : '+ Add PDF'}<input type="file" accept="application/pdf" disabled={uploading} onChange={(event) => { const file = event.target.files?.[0]; if (file) void upload(file); event.currentTarget.value = ''; }} /></label>
          </div>
          <div className="scope-row"><span>Ask about</span><button className={selectedDocumentId === null ? 'scope active' : 'scope'} onClick={() => setSelectedDocumentId(null)} disabled={uploading}>All documents</button></div>
          <div className="docs">{documents.length ? documents.map((document) => <button className={selectedDocumentId === document.id ? 'doc selected' : 'doc'} key={document.id} onClick={() => setSelectedDocumentId(document.id)} disabled={uploading} aria-pressed={selectedDocumentId === document.id}><span className="pdf">PDF</span><div><strong>{document.filename}</strong><small>{document.document_type || 'Research document'}{selectedDocumentId === document.id ? ' · Selected' : ''}</small></div></button>) : <p className="muted">Upload fictional company PDFs to begin.</p>}</div>
        </aside>
        <section className="chat">
          <div className="section-title"><span>02 / Ask the desk</span><span className="status">{selectedDocumentId === null ? '● ALL SOURCES' : '● SELECTED PDF'}</span></div>
          <div className="question"><textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="What are the company's biggest risks?" /><button onClick={ask} disabled={loading || uploading}>{loading ? 'Researching...' : 'Run research →'}</button></div>
          {error && <p className="error">{error}</p>}
          {answer && <article className="answer"><p className="answer-label">RESEARCH NOTE</p><p className="answer-text">{answer.answer}</p><div className="sources"><strong>Sources</strong>{answer.sources.map((source) => <span key={`${source.document}-${source.page}`}>{source.document} · p.{source.page}</span>)}</div><div className="metadata"><span>MODEL <b>{answer.usage.model || 'Unavailable'}</b></span><span>TOKENS <b>{answer.usage.total_tokens ?? 'Unavailable'}</b></span><span>CHUNKS <b>{answer.usage.retrieved_chunks}</b></span><span>LATENCY <b>{(answer.usage.latency_ms / 1000).toFixed(1)}s</b></span>{answer.tool_calls.map((tool) => <span key={tool.tool}>TOOL <b>{tool.tool}</b></span>)}</div></article>}
          <div className="history"><div className="section-title"><span>03 / Request history</span><span>{history.length} requests</span></div>{history.length ? history.map((item) => <div className="history-item" key={item.id}><strong>{item.question}</strong><small>{new Date(item.timestamp).toLocaleString()} · {item.total_tokens ?? 'Tokens unavailable'} tokens · {item.latency_ms}ms</small></div>) : <p className="muted">Completed research requests will appear here.</p>}</div>
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>);
