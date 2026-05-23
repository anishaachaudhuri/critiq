import styles from './Pipeline.module.css'

const AGENTS = ['Bug Detection','Security','Performance','Readability','Best Practices']

function scoreColor(n) {
  return n >= 8 ? '#3ec97a' : n >= 5 ? '#d4aa30' : '#f06868'
}

export default function Pipeline({ agentStates }) {
  return (
    <div className={styles.card}>
      <div className={styles.head}>
        <span>Execution Pipeline</span>
        <span className={styles.headRight}>parallel dispatch</span>
      </div>
      <div className={styles.rows}>
        {AGENTS.map((name, idx) => {
          const st = agentStates[name] ?? { status: 'idle' }
          return (
            <div key={name}>
              {idx > 0 && (
                <div className={styles.connector}>
                  <div className={styles.vline} />
                </div>
              )}
              <div className={styles.row}>
                <div className={`${styles.dot} ${styles[st.status]}`} />
                <span className={`${styles.name} ${st.status === 'running' ? styles.running : st.status === 'done' ? styles.done : ''}`}>
                  {name}
                </span>
                <div className={styles.meta}>
                  {st.score !== undefined && (
                    <span className={styles.score} style={{ color: scoreColor(st.score) }}>
                      {st.score}/10
                    </span>
                  )}
                  {st.ms !== undefined && (
                    <span className={styles.ms}>{(st.ms / 1000).toFixed(1)}s</span>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}