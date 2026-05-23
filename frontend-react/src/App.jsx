import { useState, useRef, useCallback } from 'react'
import Header         from './components/Header'
import EditorPanel    from './components/EditorPanel'
import ResultsPanel   from './components/ResultsPanel'
import DiffPanel      from './components/DiffPanel'
import MultiFilePanel from './components/MultiFilePanel'
import HistoryPanel   from './components/HistoryPanel'
import StatusBar      from './components/StatusBar'
import DownloadModal  from './components/DownloadModal'

const API = 'http://localhost:8000'

const SAMPLE_CODE = `import sqlite3, hashlib

password = "admin123"

def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = '"
        + username + "'"
    )
    return cursor.fetchone()

def find_dupes(items):
    result = []
    for i in range(len(items)):
        for j in range(len(items)):
            if items[i] == items[j] and i != j:
                result.append(items[i])
    return result

def hash_password(pwd):
    return hashlib.md5(pwd.encode()).hexdigest()
`

export default function App() {
  const [view,        setView]        = useState('editor')
  const [code,        setCode]        = useState(SAMPLE_CODE)
  const [lang,        setLang]        = useState('python')
  const [fname,       setFname]       = useState('example.py')
  const [running,     setRunning]     = useState(false)
  const [status,      setStatus]      = useState('')
  const [metadata,    setMetadata]    = useState(null)
  const [agentStates, setAgentStates] = useState({})
  const [reviews,     setReviews]     = useState([])
  const [report,      setReport]      = useState(null)
  const [error,       setError]       = useState(null)
  const [showDl,      setShowDl]      = useState(false)

  const startTimes = useRef({})

  function resetResults() {
    setError(null); setMetadata(null)
    setAgentStates({}); setReviews([])
    setReport(null); startTimes.current = {}
  }

  async function consumeStream(response) {
    const reader  = response.body.getReader()
    const decoder = new TextDecoder()
    let   buf     = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      const parts = buf.split('\n\n')
      buf = parts.pop() ?? ''

      for (const part of parts) {
        if (!part.trim()) continue
        let evType = 'message', dataStr = ''
        for (const line of part.split('\n')) {
          if (line.startsWith('event: ')) evType  = line.slice(7).trim()
          if (line.startsWith('data: '))  dataStr = line.slice(6).trim()
        }
        if (!dataStr) continue
        let data
        try { data = JSON.parse(dataStr) } catch { continue }

        if (evType === 'status') {
          setStatus(data.message)
        } else if (evType === 'metadata') {
          setMetadata(data)
        } else if (evType === 'agent_start') {
          startTimes.current[data.domain] = Date.now()
          setAgentStates(p => ({ ...p, [data.domain]: { status: 'running' } }))
        } else if (evType === 'agent_complete') {
          const ms = Date.now() - (startTimes.current[data.domain] ?? Date.now())
          setAgentStates(p => ({ ...p, [data.domain]: { status: 'done', score: data.score, ms } }))
          setReviews(p => [...p, { ...data, ms }])
        } else if (evType === 'complete') {
          setReport(data)
          setStatus('Review complete')
          setRunning(false)
        } else if (evType === 'error') {
          setError(data.message)
          setRunning(false)
        }
      }
    }
  }

  const runReview = useCallback(async () => {
    setRunning(true); setStatus('Initializing...'); resetResults(); setView('results')
    try {
      const res = await fetch(`${API}/review/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language: lang, filename: fname || null }),
      })
      await consumeStream(res)
    } catch (e) {
      setError(`Cannot connect to API server.\n${e.message}`)
      setRunning(false)
    }
  }, [code, lang, fname])

  const runDiff = useCallback(async ({ codeBefore, codeAfter, language, filename }) => {
    setRunning(true); setStatus('Analyzing diff...'); resetResults(); setView('results')
    try {
      const res = await fetch(`${API}/review/diff`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code_before: codeBefore, code_after: codeAfter, language, filename }),
      })
      await consumeStream(res)
    } catch (e) {
      setError(`Cannot connect to API server.\n${e.message}`)
      setRunning(false)
    }
  }, [])

  const runMulti = useCallback(async (file) => {
    setRunning(true); setStatus(`Uploading ${file.name}...`); resetResults(); setView('results')
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch(`${API}/review/multi`, { method: 'POST', body: form })
      await consumeStream(res)
    } catch (e) {
      setError(`Cannot connect to API server.\n${e.message}`)
      setRunning(false)
    }
  }, [])

  const totalIssues = report
    ? report.critical_issues_count + report.high_issues_count +
      report.medium_issues_count   + report.low_issues_count
    : null

  return (
    <div style={{ display:'flex', flexDirection:'column', height:'100vh', overflow:'hidden' }}>
      {showDl && report && (
        <DownloadModal report={report} onClose={() => setShowDl(false)} />
      )}

      <Header
        running={running}
        hasReport={!!report}
        view={view}
        onViewChange={setView}
        onRun={runReview}
        onDownload={() => setShowDl(true)}
      />

      <div style={{ flex:1, overflow:'hidden', display:'flex', flexDirection:'column' }}>
        {view === 'editor'    && <EditorPanel code={code} lang={lang} fname={fname} onCodeChange={setCode} onLangChange={setLang} onFnameChange={setFname} />}
        {view === 'results'   && <ResultsPanel running={running} error={error} metadata={metadata} agentStates={agentStates} reviews={reviews} report={report} />}
        {view === 'diff'      && <DiffPanel onRunDiff={runDiff} running={running} />}
        {view === 'multi'     && <MultiFilePanel onRunMulti={runMulti} running={running} />}
        {view === 'history'   && <HistoryPanel />}
      </div>

      <StatusBar running={running} agentCount={reviews.length} totalIssues={totalIssues} report={report} view={view} onViewChange={setView} />
    </div>
  )
}