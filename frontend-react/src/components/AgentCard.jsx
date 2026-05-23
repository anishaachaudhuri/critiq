import { useState } from 'react'
import styles from './AgentCard.module.css'

const SEV_ORDER = ['critical', 'high', 'medium', 'low']
const SEV_LABELS = { critical: 'Critical Issues', high: 'High Priority', medium: 'Warnings', low: 'Suggestions' }
const SEV_COLORS = { critical: '#f06868', high: '#e88848', medium: '#d4aa30', low: '#5a9cf0' }
const SEV_BG     = { critical: '#f0686812', high: '#e8884812', medium: '#d4aa3012', low: '#5a9cf012' }

function scoreColor(n) { return n >= 8 ? '#3ec97a' : n >= 5 ? '#d4aa30' : '#f06868' }

function IssueItem({ issue, index }) {
  const [open, setOpen] = useState(false)
  const hasDetail = issue.suggestion || issue.code_snippet
  const c = SEV_COLORS[issue.severity] ?? '#888'

  return (
    <div className={styles.issueItem}>
      <div
        className={styles.issueHeader}
        onClick={() => hasDetail && setOpen(o => !o)}
        style={{ cursor: hasDetail ? 'pointer' : 'default' }}
      >
        <span className={styles.issueIndex}>{String(index + 1).padStart(2, '0')}</span>
        <span className={styles.issueTitle}>{issue.issue}</span>
        <div className={styles.issueRight}>
          {issue.line_number && (
            <span className={styles.lineNo}>:{issue.line_number}</span>
          )}
          {hasDetail && (
            <span className={styles.expandHint} style={{ color: open ? c : 'var(--muted)' }}>
              {open ? '▲' : '▼'}
            </span>
          )}
        </div>
      </div>

      {open && hasDetail && (
        <div className={styles.issueBody}>
          {issue.suggestion && (
            <div className={styles.fixBlock} style={{ borderLeftColor: c }}>
              <div className={styles.fixLabel} style={{ color: c }}>Suggested Fix</div>
              <div className={styles.fixText}>{issue.suggestion}</div>
            </div>
          )}
          {issue.code_snippet && (
            <div className={styles.snippetBlock}>
              <div className={styles.snippetLabel}>Code Reference</div>
              <pre className={styles.snippetCode}>{issue.code_snippet}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function SevGroup({ sev, items }) {
  const [open, setOpen] = useState(true)
  const c = SEV_COLORS[sev]
  const bg = SEV_BG[sev]

  return (
    <div className={styles.sevGroup}>
      <div
        className={styles.sevGroupHead}
        onClick={() => setOpen(o => !o)}
        style={{ borderLeftColor: c }}
      >
        <span className={styles.sevPill} style={{ color: c, background: bg }}>
          {sev.toUpperCase()}
        </span>
        <span className={styles.sevLabel} style={{ color: c }}>{SEV_LABELS[sev]}</span>
        <span className={styles.sevCount}>{items.length}</span>
        <span className={styles.sevChev} style={{ color: 'var(--muted)' }}>{open ? '▲' : '▼'}</span>
      </div>
      {open && (
        <div className={styles.sevItems}>
          {items.map((issue, i) => (
            <IssueItem key={i} issue={issue} index={i} />
          ))}
        </div>
      )}
    </div>
  )
}

export default function AgentCard({ review }) {
  const [open, setOpen] = useState(true)
  const issues = review.issues ?? []
  const sc = scoreColor(review.score)

  const grouped = SEV_ORDER.reduce((acc, sev) => {
    const grp = issues.filter(i => i.severity === sev)
    if (grp.length) acc.push({ sev, items: grp })
    return acc
  }, [])

  return (
    <div className={styles.card}>
      <div
        className={styles.trigger}
        onClick={() => setOpen(o => !o)}
      >
        <div className={`${styles.statusDot} ${styles.done}`} />
        <span className={styles.agentName}>{review.domain}</span>
        {review.ms != null && (
          <span className={styles.timing}>{(review.ms / 1000).toFixed(1)}s</span>
        )}
        {issues.length > 0 && (
          <span className={styles.issueCount}>
            {issues.length} issue{issues.length !== 1 ? 's' : ''}
          </span>
        )}
        <span className={styles.score} style={{ color: sc }}>{review.score}/10</span>
        <span className={`${styles.chev} ${open ? styles.chevOpen : ''}`}>▾</span>
      </div>

      {open && (
        <div className={styles.body}>
          <p className={styles.assessment}>{review.overall_assessment}</p>

          {issues.length === 0 ? (
            <p className={styles.noIssues}>No issues detected in this domain.</p>
          ) : (
            grouped.map(({ sev, items }) => (
              <SevGroup key={sev} sev={sev} items={items} />
            ))
          )}
        </div>
      )}
    </div>
  )
}