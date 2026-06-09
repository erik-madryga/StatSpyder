import { useEffect, useState } from 'react'

function App() {
  const [backendMessage, setBackendMessage] = useState<string>('Loading...')

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    fetch(`${API_URL}/api/trending`)
      .then(res => res.json())
      .then(data => setBackendMessage(data.message || JSON.stringify(data[0]) || 'No message received from backend'))
      .catch(err => setBackendMessage(JSON.stringify(err) + ' Error connecting to backend'))
  }, [])

  // form state
  const [url, setUrl] = useState<string>('')
  const [html, setHtml] = useState<string>('')
  const [rowSelector, setRowSelector] = useState<string>('')

  const [previewResult, setPreviewResult] = useState<any | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewError, setPreviewError] = useState<string | null>(null)

  const [scrapeResult, setScrapeResult] = useState<any | null>(null)
  const [scrapeLoading, setScrapeLoading] = useState(false)
  const [scrapeError, setScrapeError] = useState<string | null>(null)

  const [adminLoading, setAdminLoading] = useState(false)
  const [adminResult, setAdminResult] = useState<any | null>(null)
  const [adminError, setAdminError] = useState<string | null>(null)

  async function handlePreview() {
    setPreviewLoading(true)
    setPreviewError(null)
    setPreviewResult(null)
    try {
      const body: any = {}
      if (html) body.html = html
      if (url) body.url = url
      if (rowSelector) body.row_selector = rowSelector
      if (!body.html && !body.url) {
        setPreviewError('Provide either a URL or HTML')
        setPreviewLoading(false)
        return
      }

      const res = await fetch(`${API_URL}/api/preview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setPreviewResult(data)
    } catch (err: any) {
      setPreviewError(String(err))
    } finally {
      setPreviewLoading(false)
    }
  }

  async function handleScrape() {
    setScrapeLoading(true)
    setScrapeError(null)
    setScrapeResult(null)
    try {
      const body: any = {}
      if (html) body.html = html
      if (url) body.url = url
      if (rowSelector) body.row_selector = rowSelector
      if (!body.html && !body.url) {
        setScrapeError('Provide either a URL or HTML')
        setScrapeLoading(false)
        return
      }

      const res = await fetch(`${API_URL}/api/scrape`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setScrapeResult(data)
    } catch (err: any) {
      setScrapeError(String(err))
    } finally {
      setScrapeLoading(false)
    }
  }

  async function handleInitDB() {
    setAdminLoading(true)
    setAdminError(null)
    setAdminResult(null)
    try {
      const res = await fetch(`${API_URL}/api/db/init`, { method: 'POST' })
      if (!res.ok) throw new Error(await res.text())
      const data = await res.json()
      setAdminResult(data)
    } catch (err: any) {
      setAdminError(String(err))
    } finally {
      setAdminLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-6 gap-6">
      <h1 className="text-4xl font-bold mt-4 text-blue-400">StatSpyder</h1>

      <div className="w-full max-w-4xl bg-gray-800 p-6 rounded-lg shadow-xl border border-gray-700">
        <h2 className="text-2xl font-semibold mb-4 text-gray-300">Backend Connection Test</h2>
        <p className="text-sm text-gray-400 mb-2">{backendMessage}</p>

        <h3 className="text-lg font-medium mt-4 mb-2">Scrape / Preview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-300">URL</label>
            <input value={url} onChange={e => setUrl(e.target.value)} placeholder="https://example.com/page" className="w-full mt-1 p-2 rounded bg-gray-900 border border-gray-700" />

            <label className="block text-sm text-gray-300 mt-3">Row selector (optional)</label>
            <input value={rowSelector} onChange={e => setRowSelector(e.target.value)} placeholder="tr[id^='receiving_and_rushing']" className="w-full mt-1 p-2 rounded bg-gray-900 border border-gray-700" />
          </div>

          <div>
            <label className="block text-sm text-gray-300">HTML (paste fragment)</label>
            <textarea value={html} onChange={e => setHtml(e.target.value)} rows={10} className="w-full mt-1 p-2 rounded bg-gray-900 border border-gray-700 font-mono text-sm" placeholder="Paste a table or row HTML here" />
          </div>
        </div>

        <div className="flex gap-3 mt-4">
          <button onClick={handlePreview} disabled={previewLoading} className="bg-blue-600 px-4 py-2 rounded disabled:opacity-50">{previewLoading ? 'Previewing...' : 'Preview'}</button>
          <button onClick={handleScrape} disabled={scrapeLoading} className="bg-green-600 px-4 py-2 rounded disabled:opacity-50">{scrapeLoading ? 'Scraping...' : 'Scrape & Ingest'}</button>
        </div>

        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-gray-900 p-3 rounded">
            <h4 className="text-sm text-gray-300 mb-2">Preview Result</h4>
            {previewError && <div className="text-red-400">{previewError}</div>}
            {previewLoading && <div className="text-gray-400">Loading...</div>}
            {previewResult && <pre className="text-xs text-green-300 overflow-auto max-h-64">{JSON.stringify(previewResult, null, 2)}</pre>}
          </div>

          <div className="bg-gray-900 p-3 rounded">
            <h4 className="text-sm text-gray-300 mb-2">Scrape Result</h4>
            {scrapeError && <div className="text-red-400">{scrapeError}</div>}
            {scrapeLoading && <div className="text-gray-400">Loading...</div>}
            {scrapeResult && <pre className="text-xs text-green-300 overflow-auto max-h-64">{JSON.stringify(scrapeResult, null, 2)}</pre>}
          </div>
        </div>
        <div className="mt-4">
          <h3 className="text-lg font-medium mb-2">Admin</h3>
          <div className="flex items-center gap-3">
            <button onClick={handleInitDB} disabled={adminLoading} className="bg-yellow-600 px-4 py-2 rounded disabled:opacity-50">{adminLoading ? 'Creating...' : 'Create DB Tables'}</button>
            {adminError && <div className="text-red-400">{adminError}</div>}
            {adminResult && <div className="text-green-300">{JSON.stringify(adminResult)}</div>}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
