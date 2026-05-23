import styles from './MetaStrip.module.css'

export default function MetaStrip({ metadata: m }) {
  const active = [
    ['database',   m.has_database_access],
    ['network',    m.has_network_calls],
    ['auth',       m.has_auth_logic],
    ['user-input', m.has_user_input],
    ['crypto',     m.has_crypto],
    ['file-io',    m.has_file_io],
  ].filter(([, v]) => v).map(([k]) => k)

  return (
    <div className={styles.strip}>
      <span className={styles.chip}>
        {m.line_count}L · {m.function_count}fn · {m.complexity_estimate}
      </span>
      {active.map(k => (
        <span key={k} className={`${styles.chip} ${styles.on}`}>{k}</span>
      ))}
      {(m.risk_flags ?? []).map((f, i) => (
        <span key={i} className={`${styles.chip} ${styles.flag}`}>{f}</span>
      ))}
    </div>
  )
}