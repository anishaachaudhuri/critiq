import { useState, useEffect } from 'react'
import styles from './HistoryPanel.module.css'

const API = 'http://localhost:8000'

function scoreColor(n) { return n >= 8 ? '#3ec97a' : n >= 5 ? '#d4aa30' : '#f06868' }

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('en-US', {
      month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  } catch { return iso }
}

export default function HistoryPanel() {
  const [reports,  setReports]  = useState([])
  const [loading,  setLoading]  = useState(true)
  const [selected, setSelected] = useState(null)
  const [detail,   setDetail]   = useState(null)
  const [loadingD, setLoadingD] = useState(false)

  useEffect(() => {
    fetch(`${API}/history`)
      .then(r => r.json())
      .then(d => { setReports(d.reports ?? []); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  async function openReport(report) {
    setSelected(report.path)
    setLoadingD(true)
    setDetail(null)
    try {
      const id   = report.path.split('/').pop().replace('.json', '')
      const data = await fetch(`${API}/history/${id}`).then(r => r.json())
      setDetail(data)
    } catch {
      setDetail(null)
    }
    setLoadingD(false)
  }

  return (
    <div className={styles.panel}>
      <div className={styles.toolbar}>
        <span className={styles.label}>Review History</span>
        <span className={styles.count}>{reports.length} reviews</span>
      </div>

      <div className={styles.body}>
        <div className={styles.list}>
          {loading && (
            <div className={styles.loading}>Loading history...</div>
          )}
          {!loading && reports.length === 0 && (
            <div className={styles.empty}>
              <div className={styles.emptyTitle}>No reviews yet</div>
              <div className={styles.emptySub}>Run a review to see it here</div>
            </div>
          )}
          {reports.map((r, i) => {
            const sc = scoreColor(r.overall_score)
            const isSelected = selected === r.path
            return (
              <div
                key={i}
                className={`${styles.reportRow} ${isSelected ? styles.selected : ''}`}
                onClick={() => openReport(r)}
              >
                <div className={styles.reportLeft}>
                  <div className={styles.reportFile}>
                    {r.filename || 'unnamed'}
                  </div>
                  <div className={styles.reportDate}>{formatDate(r.generated_at)}</div>
                </div>
                <div className={styles.reportRight}>
                  <div className={styles.sevDots}>
                    {r.critical > 0 && <span className={styles.sevDot} style={{ background:'#f06868' }} title={`${r.critical} critical`} />}
                    {r.high     > 0 && <span className={styles.sevDot} style={{ background:'#e88848' }} title={`${r.high} high`} />}
                    {r.medium   > 0 && <span className={styles.sevDot} style={{ background:'#d4aa30' }} title={`${r.medium} medium`} />}
                  </div>
                  <span className={styles.reportScore} style={{ color: sc }}>
                    {r.overall_score?.toFixed(1)}
                  </span>
                </div>
              </div>
            )
          })}
        </div>

        <div className={styles.detail}>
          {!selected && (
            <div className={styles.detailEmpty}>
              <div className={styles.emptyTitle}>Select a review</div>
              <div className={styles.emptySub}>Click any entry on the left</div>
            </div>
          )}
          {loadingD && (
            <div className={styles.detailEmpty}>
              <div className={styles.emptySub}>Loading...</div>
            </div>
          )}
          {detail && !loadingD && (
            <div className={styles.detailContent}>
              <div className={styles.detailHeader}>
                <div className={styles.detailFile}>{detail.source_filename || 'unnamed'}</div>
                <div className={styles.detailDate}>{formatDate(detail.generated_at)}</div>
              </div>

              <div className={styles.detailScore}>
                <span className={styles.detailScoreNum} style={{ color: scoreColor(detail.overall_score) }}>
                  {detail.overall_score?.toFixed(1)}/10
                </span>
                <div className={styles.detailSevRow}>
                  {[
                    ['Critical', detail.critical_issues_count, '#f06868'],
                    ['High',     detail.high_issues_count,     '#e88848'],
                    ['Medium',   detail.medium_issues_count,   '#d4aa30'],
                    ['Low',      detail.low_issues_count,      '#5a9cf0'],
                  ].map(([l, n, c]) => (
                    <div key={l} className={styles.detailSevCell}>
                      <span style={{ color: c, fontFamily:'var(--mono)', fontSize:16, fontWeight:600 }}>{n}</span>
                      <span className={styles.detailSevLabel}>{l}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className={styles.detailSection}>
                <div className={styles.detailSectionTitle}>Engineering Summary</div>
                <div className={styles.detailSummary}>{detail.engineering_summary}</div>
              </div>

              {detail.top_priority_fixes?.length > 0 && (
                <div className={styles.detailSection}>
                  <div className={styles.detailSectionTitle}>Priority Fixes</div>
                  {detail.top_priority_fixes.map((fix, i) => (
                    <div key={i} className={styles.detailFix}>
                      <span className={styles.detailFixN}>{String(i+1).padStart(2,'0')}</span>
                      <span className={styles.detailFixText}>{fix}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}