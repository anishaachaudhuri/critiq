import styles from './ScoreCard.module.css'

function scoreColor(n) { return n >= 8 ? '#3ec97a' : n >= 5 ? '#d4aa30' : '#f06868' }

export default function ScoreCard({ report }) {
  const sc = scoreColor(report.overall_score)
  const cells = [
    { label: 'Critical', n: report.critical_issues_count, color: '#f06868' },
    { label: 'High',     n: report.high_issues_count,     color: '#e88848' },
    { label: 'Medium',   n: report.medium_issues_count,   color: '#d4aa30' },
    { label: 'Low',      n: report.low_issues_count,      color: '#5a9cf0' },
  ]

  return (
    <div className={styles.card}>
      <div className={styles.scoreWrap}>
        <div className={styles.scoreNum} style={{ color: sc }}>
          {report.overall_score.toFixed(1)}
          <span className={styles.denom}>/10</span>
        </div>
        <div className={styles.scoreLabel}>overall quality score</div>
      </div>
      <div className={styles.divider} />
      <div className={styles.cells}>
        {cells.map(({ label, n, color }) => (
          <div key={label} className={styles.cell}>
            <div className={styles.cellNum} style={{ color }}>{n}</div>
            <div className={styles.cellLabel}>{label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}