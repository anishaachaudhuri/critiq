import { useState, useRef } from 'react'
import styles from './MultiFilePanel.module.css'

const SUPPORTED = ['.py','.js','.ts','.java','.go','.rs','.cpp','.c','.rb']

export default function MultiFilePanel({ onRunMulti, running }) {
  const [files,    setFiles]    = useState([])
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  function handleFiles(fileList) {
    const arr = Array.from(fileList)
    const valid = arr.filter(f => {
      const ext = '.' + f.name.split('.').pop()
      return SUPPORTED.includes(ext) || f.name.endsWith('.zip')
    })
    setFiles(valid)
  }

  function onDrop(e) {
    e.preventDefault()
    setDragging(false)
    handleFiles(e.dataTransfer.files)
  }

  function removeFile(i) {
    setFiles(f => f.filter((_, idx) => idx !== i))
  }

  const hasZip = files.some(f => f.name.endsWith('.zip'))

  return (
    <div className={styles.panel}>
      <div className={styles.toolbar}>
        <span className={styles.label}>Multi-File / Repository Review</span>
        <button
          className={styles.runBtn}
          disabled={running || files.length === 0}
          onClick={() => onRunMulti(files[0])}
        >
          {running ? 'Running...' : `Analyze ${files.length > 0 ? files.length === 1 && hasZip ? 'Repository' : files.length + ' Files' : 'Files'}`}
        </button>
      </div>

      <div className={styles.body}>
        <div
          className={`${styles.dropzone} ${dragging ? styles.dragging : ''} ${files.length > 0 ? styles.hasFiles : ''}`}
          onDragOver={e => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => files.length === 0 && inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            multiple
            accept={[...SUPPORTED, '.zip'].join(',')}
            style={{ display: 'none' }}
            onChange={e => handleFiles(e.target.files)}
          />
          {files.length === 0 ? (
            <div className={styles.dropPrompt}>
              <div className={styles.dropIcon}>⬆</div>
              <div className={styles.dropTitle}>Drop files or a .zip here</div>
              <div className={styles.dropSub}>
                Supports: {SUPPORTED.join(', ')} and .zip archives
              </div>
            </div>
          ) : (
            <div className={styles.fileList}>
              {files.map((f, i) => (
                <div key={i} className={styles.fileRow}>
                  <span className={styles.fileIcon}>{f.name.endsWith('.zip') ? '◫' : '◻'}</span>
                  <span className={styles.fileName}>{f.name}</span>
                  <span className={styles.fileSize}>{(f.size / 1024).toFixed(1)}kb</span>
                  <button className={styles.removeBtn} onClick={() => removeFile(i)}>✕</button>
                </div>
              ))}
              <button
                className={styles.addMore}
                onClick={e => { e.stopPropagation(); inputRef.current?.click() }}
              >
                + Add more files
              </button>
            </div>
          )}
        </div>

        <div className={styles.infoCards}>
          <div className={styles.infoCard}>
            <div className={styles.infoCardTitle}>How it works</div>
            <div className={styles.infoCardBody}>
              Each file runs through the full 5-agent pipeline independently.
              A cross-file summary identifies systemic patterns and issues that
              span multiple files.
            </div>
          </div>
          <div className={styles.infoCard}>
            <div className={styles.infoCardTitle}>Limits</div>
            <div className={styles.infoCardBody}>
              Maximum 10 files per run. For .zip files, only source files with
              supported extensions are analyzed. Binary files and dependencies
              are skipped automatically.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}