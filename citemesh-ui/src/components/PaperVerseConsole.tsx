import { useCallback, useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import './PaperVerseConsole.css'

type BackendStatusTone = 'neutral' | 'success' | 'error'

type BackendStatus = {
  message: string
  tone: BackendStatusTone
  loading: boolean
}

type PaperVerseAuthor = {
  id?: string
  name: string
  institution?: string
}

type PaperVerseResult = {
  id: string
  title: string
  authors: PaperVerseAuthor[]
  publication_date?: string
  publication_year?: number
  venue?: string
  cited_by_count: number
  doi?: string
  pdf_url?: string
  abstract?: string
  open_access: boolean
  relevance_score?: number
}

type SearchResponse = {
  query: string
  enhanced_query?: string
  results: PaperVerseResult[]
  total_results: number
  page: number
  per_page: number
  total_pages: number
  search_time_ms: number
}

const PRESETS = [
  {
    value: 'Find the most cited reinforcement learning papers since 2021',
    label: 'Reinforcement Learning Since 2021'
  },
  {
    value: 'Show me open access quantum computing papers from 2023 onwards',
    label: 'Quantum Computing OA 2023+'
  },
  {
    value: 'List top collaborations between University of Florida and MIT in biomedicine',
    label: 'UF x MIT Biomed Collaborations'
  }
]

const formatNumber = (value?: number) => {
  if (typeof value !== 'number') return undefined
  return new Intl.NumberFormat('en-US').format(value)
}

const resolveBackendBaseUrl = () => {
  const envUrl = import.meta.env.VITE_BACKEND_URL?.trim()
  if (envUrl) return envUrl.replace(/\/$/, '')

  const raw = window.PAPERVERSE_BACKEND?.trim()
  if (raw) return raw.replace(/\/$/, '')

  return 'http://127.0.0.1:8000'
}

export default function PaperVerseConsole() {
  const backendBaseUrl = useMemo(resolveBackendBaseUrl, [])

  const [query, setQuery] = useState('')
  const [perPage, setPerPage] = useState(5)
  const [page, setPage] = useState(1)
  const [presetValue, setPresetValue] = useState('')
  const [status, setStatus] = useState<BackendStatus>({ message: '', tone: 'neutral', loading: false })
  const [results, setResults] = useState<PaperVerseResult[]>([])
  const [meta, setMeta] = useState<{ count?: number } | undefined>()
  const [pagination, setPagination] = useState<{ page?: number } | undefined>()
  const [hasFetched, setHasFetched] = useState(false)

  const testBackendConnection = useCallback(async () => {
    setStatus({ message: 'Testing backend connection…', tone: 'neutral', loading: true })
    try {
      const response = await fetch(`${backendBaseUrl}/health`, { method: 'GET' })
      if (response.ok) {
        setStatus({ message: `✓ Backend connected at ${backendBaseUrl}`, tone: 'success', loading: false })
      } else {
        throw new Error(`HTTP ${response.status}`)
      }
    } catch (error) {
      const detail = error instanceof Error ? error.message : 'Unreachable'
      setStatus({
        message: `✗ Cannot reach backend at ${backendBaseUrl} (${detail})`,
        tone: 'error',
        loading: false
      })
    }
  }, [backendBaseUrl])

  useEffect(() => {
    testBackendConnection()
  }, [testBackendConnection])

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    if (!query.trim()) {
      setStatus({ message: 'Enter a research question to begin.', tone: 'error', loading: false })
      return
    }

    setStatus({ message: 'Translating prompt via Gemini & querying OpenAlex…', tone: 'neutral', loading: true })

    try {
      const response = await fetch(`${backendBaseUrl}/api/search/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim(), per_page: perPage, page })
      })

      if (!response.ok) {
        let detail = `${response.status} ${response.statusText}`
        try {
          const errorJson = (await response.json()) as { detail?: string }
          if (errorJson.detail) detail = errorJson.detail
        } catch {
          /* ignore parse errors */
        }
        throw new Error(detail)
      }

      const data = (await response.json()) as SearchResponse
      const payload = data.results ?? []
      setResults(payload)
      setMeta({ count: data.total_results })
      setPagination({ page: data.page })
      setHasFetched(true)

      const count = payload.length
      setStatus({
        message: `Fetched ${count} result${count === 1 ? '' : 's'} from PaperVerse backend. Total: ${data.total_results}`,
        tone: 'success',
        loading: false
      })
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unexpected error occurred.'
      setResults([])
      setMeta(undefined)
      setPagination(undefined)
      setHasFetched(true)
      setStatus({ message: `Error: ${message}`, tone: 'error', loading: false })
    }
  }

  const handleClear = () => {
    setQuery('')
    setPerPage(5)
    setPage(1)
    setPresetValue('')
    setResults([])
    setMeta(undefined)
    setPagination(undefined)
    setHasFetched(false)
    setStatus({ message: '', tone: 'neutral', loading: false })
  }

  const displayStatusMessage = status.message || `PaperVerse backend ready at ${backendBaseUrl}`

  const statusClassName = `pv-console__status pv-console__status--${status.tone}`

  const shouldShowPlaceholder = !hasFetched && results.length === 0
  const showEmptyState = hasFetched && results.length === 0 && status.tone !== 'error'

  return (
    <section className="pv-console" aria-labelledby="paperverse-console-title">
      <header className="pv-console__header">
        <div>
          <p className="pv-console__tag">Live Prototype</p>
          <h2 id="paperverse-console-title" className="pv-console__title">Ask PaperVerse Anything</h2>
          <p className="pv-console__subtitle">
            Run natural-language queries against the running backend. We translate your intent, call OpenAlex, and surface
            open-access links without leaving the dashboard.
          </p>
        </div>
        <div className={statusClassName}>
          {status.loading && <span className="pv-console__spinner" />}
          <span className="pv-console__status-text">{displayStatusMessage}</span>
        </div>
      </header>

      <form className="pv-console__form" onSubmit={handleSubmit}>
        <label className="pv-console__field">
          <span className="pv-console__label">Research Question</span>
          <textarea
            className="pv-console__textarea"
            placeholder="e.g. Find the most cited reinforcement learning papers since 2021 with open source implementations"
            required
            spellCheck={false}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>

        <div className="pv-console__controls">
          <label className="pv-console__field">
            <span className="pv-console__label">Per Page</span>
            <select className="pv-console__input" value={perPage} onChange={(event) => setPerPage(Number(event.target.value))}>
              <option value={5}>5 results</option>
              <option value={10}>10 results</option>
              <option value={25}>25 results</option>
            </select>
          </label>
          <label className="pv-console__field">
            <span className="pv-console__label">Page</span>
            <input
              className="pv-console__input"
              type="number"
              min={1}
              value={page}
              onChange={(event) => setPage(Number(event.target.value) || 1)}
            />
          </label>
          <label className="pv-console__field">
            <span className="pv-console__label">Preset Queries</span>
            <select
              className="pv-console__input"
              value={presetValue}
              onChange={(event) => {
                const value = event.target.value
                setPresetValue(value)
                if (value) setQuery(value)
              }}
            >
              <option value="">Choose a preset</option>
              {PRESETS.map((preset) => (
                <option key={preset.label} value={preset.value}>
                  {preset.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="pv-console__actions">
          <button type="button" className="pv-console__button pv-console__button--secondary" onClick={handleClear}>
            Clear
          </button>
          <button type="submit" className="pv-console__button pv-console__button--primary">
            Run Query
          </button>
        </div>
      </form>

      <div className="pv-console__results" aria-live="polite">
        {shouldShowPlaceholder && (
          <p className="pv-console__placeholder">Run a query to see PaperVerse synthesize live intelligence.</p>
        )}

        {showEmptyState && status.tone !== 'error' && (
          <p className="pv-console__placeholder">No works found for this query. Adjust your filters or try another preset.</p>
        )}

        {results.length > 0 && (
          <div className="pv-console__result-summary">
            <span>Showing {results.length} results</span>
            <span>Page {pagination?.page ?? 1}</span>
            <span>
              OpenAlex total{' '}
              <span className="pv-console__result-summary-count">{formatNumber(meta?.count) ?? '—'}</span>
            </span>
          </div>
        )}

        {results.map((item) => {
          const citationCount = formatNumber(item.cited_by_count)
          const proxyUrl = item.pdf_url
            ? `${backendBaseUrl}/pdf?url=${encodeURIComponent(item.pdf_url)}`
            : undefined
          
          const authorsText = item.authors.slice(0, 3).map(a => a.name).join(', ') + 
            (item.authors.length > 3 ? ` +${item.authors.length - 3} more` : '')

          return (
            <article key={item.id} className="pv-console__result-card">
              <h3 className="pv-console__result-title">{item.title}</h3>

              {authorsText && (
                <p className="pv-console__result-source">{authorsText}</p>
              )}

              <div className="pv-console__result-meta">
                {item.publication_year && <span>{item.publication_year}</span>}
                {item.venue && <span>{item.venue}</span>}
                {citationCount && <span>{citationCount} citations</span>}
                {item.open_access && <span>Open Access</span>}
                {item.doi && (
                  <span>
                    DOI: <a className="pv-console__link" target="_blank" rel="noopener" href={item.doi}>{item.doi.replace('https://doi.org/', '')}</a>
                  </span>
                )}
              </div>

              <div className="pv-console__result-actions">
                {proxyUrl && (
                  <a href={proxyUrl} target="_blank" rel="noopener" className="pv-console__chip">
                    Open Access PDF
                  </a>
                )}
                {item.id && (
                  <a
                    href={`https://openalex.org/works/${item.id}`}
                    target="_blank"
                    rel="noopener"
                    className="pv-console__chip"
                  >
                    View on OpenAlex
                  </a>
                )}
              </div>
            </article>
          )
        })}
      </div>
    </section>
  )
}
