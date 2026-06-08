import { useEffect, useState } from 'react'

function App() {
  const [backendMessage, setBackendMessage] = useState<string>('Loading...')

  useEffect(() => {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    fetch(`${API_URL}/api/trending`)
      .then(res => res.json())
      .then(data => setBackendMessage(data.message))
      .catch(err => setBackendMessage(JSON.stringify(err) + 'Error connecting to backend'))
  }, [])

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
      <h1 className="text-5xl font-bold mb-8 text-blue-400">StatSpyder</h1>
      <div className="bg-gray-800 p-6 rounded-lg shadow-xl border border-gray-700">
        <h2 className="text-2xl font-semibold mb-4 text-gray-300">Backend Connection Test:</h2>
        <p className="text-xl text-green-400 font-mono">{backendMessage}</p>
      </div>
    </div>
  )
}

export default App
