import styles from './Timeline.module.css'

function scoreColor(n) {
  return n >= 8 ? '#3ec97a' : n >= 5 ? '#d4aa30' : '#f06868'
}

export default function Timeline({ reviews }) {
  if (!reviews.length) return null

  const maxMs = Math.max(...reviews.map(r => r.ms ?? 0), 1)
  const sorted = [...reviews].sort((a, b) => (a.ms ?? 0) - (b.ms ?? 0))
  const fastest = sorted[0]?.domain
  const slowest = sorted[sorted.length - 1]?.domain

  return (
    <div className={styles.card}>
      <div className={styles.head}>
        <span>Agent Performance</span>
        <span className={styles.headRight}>response timeline</span>
      </div>
      <div className={styles.body}>
        {reviews.map((r, i) => {
          const pct = ((r.ms ?? 0) / maxMs) * 100
          const isFastest = r.domain === fastest
          const isSlowest = r.domain === slowest && reviews.length > 1
          const sc = scoreColor(r.score)

          return (
            <div key={i} className={styles.row}>
              <div className={styles.agentName}>{r.domain}</div>
              <div className={styles.barWrap}>
                <div
                  className={styles.bar}
                  style={{
                    width: `${pct}%`,
                    background: sc,
                    opacity: 0.7,
                  }}
                />
              </div>
              <div className={styles.right}>
                <span className={styles.time}>{r.ms != null ? `${(r.ms / 1000).toFixed(1)}s` : '—'}</span>
                {isFastest && <span className={styles.badge} style={{ color:'#3ec97a', background:'#3ec97a12', border:'1px solid #3ec97a33' }}>fastest</span>}
                {isSlowest && <span className={styles.badge} style={{ color:'#d4aa30', background:'#d4aa3012', border:'1px solid #d4aa3033' }}>slowest</span>}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}