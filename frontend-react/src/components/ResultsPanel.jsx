import { useRef, useEffect } from 'react'
import Pipeline       from './Pipeline'
import MetaStrip      from './MetaStrip'
import ScoreCard      from './ScoreCard'
import AgentCard      from './AgentCard'
import Timeline       from './Timeline'
import ExecutiveSummary from './ExecutiveSummary'
import styles         from './ResultsPanel.module.css'

export default function ResultsPanel({ running, error, metadata, agentStates, reviews, report }) {
  const scrollRef  = useRef(null)
  const hasContent = running || metadata || reviews.length > 0 || report

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [reviews.length, !!report, !!metadata])

  return (
    <div className={styles.panel}>
      <div className={styles.scroll} ref={scrollRef}>

        {!hasContent && !error && (
          <div className={styles.empty}>
            <div className={styles.emptyTitle}>No review loaded</div>
            <div className={styles.emptySub}>Switch to Editor tab → paste code → Run Review</div>
          </div>
        )}

        {error && <div className={styles.errorBox}>{error}</div>}

        {hasContent && (
          <div className={styles.topRow}>
            <Pipeline agentStates={agentStates} />
            {metadata && <MetaStrip metadata={metadata} />}
          </div>
        )}

        {report && <ScoreCard report={report} />}

        {reviews.length > 0 && (
          <Timeline reviews={reviews} agentStates={agentStates} />
        )}

        {reviews.length > 0 && (
          <div className={styles.agentsSection}>
            <div className={styles.sectionLabel}>Agent Reviews</div>
            <div className={styles.agentGrid}>
              {reviews.map((r, i) => (
                <AgentCard key={i} review={r} />
              ))}
            </div>
          </div>
        )}

        {report?.merged_issues?.length > 0 && (
          <ChangesCard issues={report.merged_issues} />
        )}

        {report && <ExecutiveSummary report={report} />}

      </div>
    </div>
  )
}

function ChangesCard({ issues }) {
  const colors = { critical:'#f06868', high:'#e88848', medium:'#d4aa30', low:'#5a9cf0' }
  const bgs    = { critical:'#f0686812', high:'#e8884812', medium:'#d4aa3012', low:'#5a9cf012' }

  return (
    <div className={styles.changesCard}>
      <div className={styles.changesHead}>
        Recommended Changes
        <span className={styles.changesCount}>{issues.length} deduplicated</span>
      </div>
      <div className={styles.changesBody}>
        {issues.map((iss, i) => {
          const c  = colors[iss.severity] ?? '#888'
          const bg = bgs[iss.severity]    ?? '#fff2'
          return (
            <div key={i} className={styles.changeRow} style={{ borderLeftColor: c + '66' }}>
              <div className={styles.changeTop}>
                <span className={styles.sevPill} style={{ color:c, background:bg }}>{iss.severity?.toUpperCase()}</span>
                <span className={styles.changeIssue}>{iss.issue}</span>
              </div>
              <div className={styles.changeFix}>{iss.suggestion}</div>
              <div className={styles.changeMeta}>
                Flagged by: {(iss.flagged_by ?? []).join(', ')} · Confidence: {Math.round((iss.confidence ?? 1) * 100)}%
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}