import styles from './DownloadModal.module.css'

export default function DownloadModal({ report, onClose }) {
  function dlHTML() {
    alert(`HTML report saved to:\n${report.html_report_path}\n\nOpen that file in your browser.`)
    onClose()
  }
  function dlJSON() {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const a = Object.assign(document.createElement('a'), {
      href: URL.createObjectURL(blob), download: 'critiq-report.json'
    })
    a.click()
    onClose()
  }
  function dlTXT() {
    const lines = [
      'CRITIQ CODE REVIEW REPORT', '='.repeat(44), '',
      `Score: ${report.overall_score?.toFixed(1)}/10`,
      `Critical: ${report.critical_issues_count}  High: ${report.high_issues_count}  Medium: ${report.medium_issues_count}  Low: ${report.low_issues_count}`, '',
      'PRIORITY FIXES', '-'.repeat(44),
      ...(report.top_priority_fixes ?? []).map((f, i) => `${i + 1}. ${f}`), '',
      'ENGINEERING SUMMARY', '-'.repeat(44),
      report.engineering_summary ?? '',
    ]
    const blob = new Blob([lines.join('\n')], { type: 'text/plain' })
    const a = Object.assign(document.createElement('a'), {
      href: URL.createObjectURL(blob), download: 'critiq-report.txt'
    })
    a.click()
    onClose()
  }

  const options = [
    { icon: '◈', title: 'HTML Report',  desc: 'Styled document, open in any browser', fn: dlHTML },
    { icon: '{}', title: 'JSON Export',  desc: 'Full structured data, all findings',    fn: dlJSON },
    { icon: '≡',  title: 'Plain Text',   desc: 'Summary and priority action items',     fn: dlTXT  },
  ]

  return (
    <div className={styles.backdrop} onClick={onClose}>
      <div className={styles.modal} onClick={e => e.stopPropagation()}>
        <div className={styles.title}>Download Report</div>
        <div className={styles.sub}>
          Export this review. The HTML report is a self-contained styled document you can share or archive.
        </div>
        <div className={styles.options}>
          {options.map(o => (
            <button key={o.title} className={styles.option} onClick={o.fn}>
              <span className={styles.optIcon}>{o.icon}</span>
              <div>
                <div className={styles.optTitle}>{o.title}</div>
                <div className={styles.optDesc}>{o.desc}</div>
              </div>
            </button>
          ))}
        </div>
        <button className={styles.cancel} onClick={onClose}>cancel</button>
      </div>
    </div>
  )
}