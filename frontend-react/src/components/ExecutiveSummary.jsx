import styles from './ExecutiveSummary.module.css'

function scoreColor(n) { return n >= 8 ? '#3ec97a' : n >= 5 ? '#d4aa30' : '#f06868' }
function scoreLabel(n) { return n >= 8 ? 'Good' : n >= 5 ? 'Needs Work' : 'Critical' }

export default function ExecutiveSummary({ report }) {
  const sc = scoreColor(report.overall_score)
  const total = report.critical_issues_count + report.high_issues_count +
                report.medium_issues_count   + report.low_issues_count

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.title}>Executive Summary</span>
          <span className={styles.subtitle}>Final verdict across all agents</span>
        </div>
        <div className={styles.verdict} style={{ borderColor: sc + '44', background: sc + '10' }}>
          <span className={styles.verdictScore} style={{ color: sc }}>
            {report.overall_score.toFixed(1)}
          </span>
          <span className={styles.verdictLabel} style={{ color: sc }}>{scoreLabel(report.overall_score)}</span>
        </div>
      </div>

      <div className={styles.body}>
        <p className={styles.summary}>{report.engineering_summary}</p>

        <div className={styles.prioritySection}>
          <div className={styles.priorityTitle}>Priority Action Items</div>
          <div className={styles.priorityList}>
            {(report.top_priority_fixes ?? []).map((fix, i) => (
              <div key={i} className={styles.priorityRow}>
                <span className={styles.priorityN}>{String(i + 1).padStart(2, '0')}</span>
                <span className={styles.priorityText}>{fix}</span>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.stats}>
          <div className={styles.statItem}>
            <span className={styles.statNum}>{total}</span>
            <span className={styles.statLabel}>Total Issues</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statNum} style={{ color: '#f06868' }}>
              {report.critical_issues_count}
            </span>
            <span className={styles.statLabel}>Critical</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statNum} style={{ color: '#e88848' }}>
              {report.high_issues_count}
            </span>
            <span className={styles.statLabel}>High</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statNum} style={{ color: sc }}>
              {report.overall_score.toFixed(1)}
            </span>
            <span className={styles.statLabel}>Score</span>
          </div>
        </div>
      </div>
    </div>
  )
}