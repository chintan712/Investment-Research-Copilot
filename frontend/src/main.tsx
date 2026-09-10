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
  const [error, setError] = useState('');

  const loadDocuments = () => fetch(`${API}/documents`).then((response) => response.json()).then(setDocuments).catch(() => setError('Backend is unavailable. Start the API and try again.'));
  const loadHistory = () => fetch(`${API}/requests`).then((response) => response.json()).then(setHistory).catch(() => undefined);
  useEffect(() => { loadDocuments(); loadHistory(); }, []);

  async function upload(file: File) {
    const body = new FormData(); body.append('file', file);
    const response = await fetch(`${API}/documents/upload`, { method: 'POST', body });
    if (!response.ok) throw new Error((await response.json()).detail || 'Upload failed');
    await loadDocuments();
  }

  async function ask() {
    if (!question.trim()) return;
    setLoading(true); setError('');
    try { const response = await fetch(`${API}/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question }) }); if (!response.ok) throw new Error((await response.json()).detail); setAnswer(await response.json()); await loadHistory(); } catch (reason) { setError(String(reason)); } finally { setLoading(false); }
  }

  return <main><header><p className="kicker">INTERNAL RESEARCH WORKSPACE</p><h1>Investment Research<br /><em>Copilot</em></h1><p className="lede">Grounded answers for fictional deal teams, with every claim tied back to the source material.</p></header><section className="workspace"><aside><div className="section-title"><span>01 / Evidence</span><label className="upload">+ Add PDF<input type="file" accept="application/pdf" onChange={(event) => event.target.files?.[0] && upload(event.target.files[0]).catch((reason) => setError(String(reason)))} /></label></div><div className="docs">{documents.length ? documents.map((document) => <div className="doc" key={document.id}><span className="pdf">PDF</span><div><strong>{document.filename}</strong><small>{document.document_type || 'Research document'}</small></div></div>) : <p className="muted">Upload fictional company PDFs to begin.</p>}</div></aside><section className="chat"><div className="section-title"><span>02 / Ask the desk</span><span className="status">● LIVE RAG</span></div><div className="question"><textarea value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="What are the company's biggest risks?" /><button onClick={ask} disabled={loading}>{loading ? 'Researching...' : 'Run research →'}</button></div>{error && <p className="error">{error}</p>}{answer && <article className="answer"><p className="answer-label">RESEARCH NOTE</p><p className="answer-text">{answer.answer}</p><div className="sources"><strong>Sources</strong>{answer.sources.map((source) => <span key={`${source.document}-${source.page}`}>{source.document} · p.{source.page}</span>)}</div><div className="metadata"><span>MODEL <b>{answer.usage.model || 'Unavailable'}</b></span><span>TOKENS <b>{answer.usage.total_tokens ?? 'Unavailable'}</b></span><span>CHUNKS <b>{answer.usage.retrieved_chunks}</b></span><span>LATENCY <b>{(answer.usage.latency_ms / 1000).toFixed(1)}s</b></span>{answer.tool_calls.map((tool) => <span key={tool.tool}>TOOL <b>{tool.tool}</b></span>)}</div></article>}<div className="history"><div className="section-title"><span>03 / Request history</span><span>{history.length} requests</span></div>{history.length ? history.map((item) => <div className="history-item" key={item.id}><strong>{item.question}</strong><small>{new Date(item.timestamp).toLocaleString()} · {item.total_tokens ?? 'Tokens unavailable'} tokens · {item.latency_ms}ms</small></div>) : <p className="muted">Completed research requests will appear here.</p>}</div></section></section></main>;
}

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>);
