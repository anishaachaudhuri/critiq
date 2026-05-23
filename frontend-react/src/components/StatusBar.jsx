import styles from './StatusBar.module.css'

export default function StatusBar({ running, agentCount, totalIssues, report, view, onViewChange }) {
  return (
    <div className={styles.bar}>
      <div className={styles.left}>
        <div className={styles.item}>
          <div className={`${styles.dot} ${running ? styles.live : ''}`} />
          {running ? 'pipeline running' : report ? 'complete' : 'idle'}
        </div>
        {totalIssues !== null && (
          <div className={styles.item}>
            {agentCount} agents · {totalIssues} issues found
          </div>
        )}
      </div>

      <div className={styles.center}>
        <button
          className={`${styles.viewBtn} ${view === 'editor' ? styles.viewActive : ''}`}
          onClick={() => onViewChange('editor')}
        >editor</button>
        <span className={styles.sep}>·</span>
        <button
          className={`${styles.viewBtn} ${view === 'results' ? styles.viewActive : ''}`}
          onClick={() => onViewChange('results')}
        >results</button>
      </div>

      <div className={styles.right}>
        langgraph · groq · llama-3.3-70b
      </div>
    </div>
  )
}