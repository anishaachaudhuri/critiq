import { useState } from 'react'
import styles from './DiffPanel.module.css'

const LANGS = ['python','javascript','typescript','java','go','rust','cpp','c','ruby']

export default function DiffPanel({ onRunDiff, running }) {
  const [before,   setBefore]   = useState('')
  const [after,    setAfter]    = useState('')
  const [lang,     setLang]     = useState('python')
  const [filename, setFilename] = useState('')

  return (
    <div className={styles.panel}>
      <div className={styles.toolbar}>
        <span className={styles.label}>PR Diff Review</span>
        <div className={styles.toolbarRight}>
          <select
            className={styles.langSelect}
            value={lang}
            onChange={e => setLang(e.target.value)}
          >
            {LANGS.map(l => <option key={l}>{l}</option>)}
          </select>
          <input
            className={styles.fname}
            value={filename}
            onChange={e => setFilename(e.target.value)}
            placeholder="filename.py"
          />
          <button
            className={styles.runBtn}
            disabled={running || !before.trim() || !after.trim()}
            onClick={() => onRunDiff({ codeBefore: before, codeAfter: after, language: lang, filename })}
          >
            {running ? 'Running...' : 'Review Diff'}
          </button>
        </div>
      </div>

      <div className={styles.editors}>
        <div className={styles.editorCol}>
          <div className={styles.editorLabel}>
            <span className={styles.removeBadge}>before</span>
            Original code
          </div>
          <textarea
            className={styles.textarea}
            value={before}
            onChange={e => setBefore(e.target.value)}
            placeholder="Paste the original version here..."
            spellCheck={false}
          />
        </div>

        <div className={styles.divider} />

        <div className={styles.editorCol}>
          <div className={styles.editorLabel}>
            <span className={styles.addBadge}>after</span>
            Modified code
          </div>
          <textarea
            className={styles.textarea}
            value={after}
            onChange={e => setAfter(e.target.value)}
            placeholder="Paste the modified version here..."
            spellCheck={false}
          />
        </div>
      </div>

      <div className={styles.footer}>
        <span className={styles.hint}>
          Agents will focus their review on what changed between the two versions.
        </span>
      </div>
    </div>
  )
}