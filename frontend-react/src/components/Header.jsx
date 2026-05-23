import { useEffect, useState } from 'react'
import styles from './Header.module.css'

const TARGET = 'critiq'
const VIEWS = [
  { id: 'editor',  label: 'Editor'     },
  { id: 'diff',    label: 'Diff Review' },
  { id: 'multi',   label: 'Multi-File' },
  { id: 'history', label: 'History'    },
]

export default function Header({ running, hasReport, view, onViewChange, onRun, onDownload }) {
  const [displayed, setDisplayed] = useState('')
  const [done,      setDone]      = useState(false)

  useEffect(() => {
    let i = 0
    const iv = setInterval(() => {
      setDisplayed(TARGET.slice(0, i + 1))
      i++
      if (i >= TARGET.length) { clearInterval(iv); setTimeout(() => setDone(true), 500) }
    }, 160)
    return () => clearInterval(iv)
  }, [])

  return (
    <header className={styles.header}>
      <div className={styles.brand}>
        <h1 className={styles.wordmark}>
          {displayed}
          {!done && <span className={styles.cursor} />}
          {done  && <span className={styles.dot}>.</span>}
        </h1>
        <p className={styles.tagline}>AI Multi-Agent Code Review</p>
      </div>

      <nav className={styles.nav}>
        {VIEWS.map(v => (
          <button
            key={v.id}
            className={`${styles.navBtn} ${view === v.id ? styles.navActive : ''}`}
            onClick={() => onViewChange(v.id)}
          >
            {v.label}
          </button>
        ))}
        {hasReport && (
          <button
            className={`${styles.navBtn} ${view === 'results' ? styles.navActive : ''}`}
            onClick={() => onViewChange('results')}
          >
            Results
            <span className={styles.resultsDot} />
          </button>
        )}
      </nav>

      <div className={styles.actions}>
        {hasReport && (
          <button className={styles.btnOutline} onClick={onDownload}>Download</button>
        )}
        <button
          className={styles.btnPrimary}
          onClick={() => { onRun(); onViewChange('results') }}
          disabled={running}
        >
          {running ? 'Running...' : 'Run Review'}
        </button>
      </div>
    </header>
  )
}