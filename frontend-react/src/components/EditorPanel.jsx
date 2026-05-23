import { useRef, useMemo, useEffect, useState } from 'react'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import styles from './EditorPanel.module.css'

const LANGS = ['python','javascript','typescript','java','go','rust','cpp','c','ruby']

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

export default function EditorPanel({ code, lang, fname, onCodeChange, onLangChange, onFnameChange }) {
  const taRef      = useRef(null)
  const hlRef      = useRef(null)
  const lnRef      = useRef(null)
  const lines      = code.split('\n')

  const highlighted = useMemo(() => {
    try {
      const l = hljs.getLanguage(lang) ? lang : 'plaintext'
      return hljs.highlight(code, { language: l }).value
    } catch {
      return escapeHtml(code)
    }
  }, [code, lang])

  function syncScroll() {
    const ta = taRef.current
    const hl = hlRef.current
    const ln = lnRef.current
    if (!ta) return
    if (hl) { hl.scrollTop = ta.scrollTop; hl.scrollLeft = ta.scrollLeft }
    if (ln) { ln.scrollTop = ta.scrollTop }
  }

  function onKeyDown(e) {
    if (e.key === 'Tab') {
      e.preventDefault()
      const s  = e.target.selectionStart
      const en = e.target.selectionEnd
      const next = code.slice(0, s) + '    ' + code.slice(en)
      onCodeChange(next)
      requestAnimationFrame(() => {
        if (taRef.current) {
          taRef.current.selectionStart = taRef.current.selectionEnd = s + 4
        }
      })
    }
  }

  return (
    <div className={styles.panel}>
      <div className={styles.toolbar}>
        <span className={styles.label}>Editor</span>
        <select
          className={styles.langSelect}
          value={lang}
          onChange={e => onLangChange(e.target.value)}
        >
          {LANGS.map(l => <option key={l}>{l}</option>)}
        </select>
      </div>

      <div className={styles.editorWrap}>
        <div className={styles.lineNumbers} ref={lnRef}>
          {lines.map((_, i) => (
            <span key={i} className={styles.lineNum}>{i + 1}</span>
          ))}
        </div>

        <div className={styles.codeArea}>
          <textarea
            ref={taRef}
            className={styles.textarea}
            value={code}
            onChange={e => onCodeChange(e.target.value)}
            onScroll={syncScroll}
            onKeyDown={onKeyDown}
            spellCheck={false}
            autoComplete="off"
            placeholder="paste code here..."
          />
          <div
            className={styles.highlight}
            ref={hlRef}
            aria-hidden
            dangerouslySetInnerHTML={{
              __html: `<pre><code class="hljs language-${lang}">${highlighted}</code></pre>`
            }}
          />
        </div>
      </div>

      <div className={styles.footer}>
        <input
          className={styles.fname}
          value={fname}
          onChange={e => onFnameChange(e.target.value)}
          placeholder="filename.py"
        />
      </div>
    </div>
  )
}