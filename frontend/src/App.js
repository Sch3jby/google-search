import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Zadejte vyhledávací dotaz');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await axios.post('/api/search', {
        query: query.trim()
      });
      
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Chyba při vyhledávání');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    if (!results) return;

    try {
      const response = await axios.post(`/api/export/${format}`, {
        results: results
      }, {
        responseType: 'blob'
      });

      // Vytvoření download linku
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const contentDisposition = response.headers['content-disposition'];
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1].replace(/"/g, '')
        : `search_results.${format}`;
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Chyba při exportu dat');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Google Search Tool</h1>
        
        <form onSubmit={handleSearch} className="search-form">
          <div className="input-group">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Zadejte klíčové slovo nebo frázi..."
              className="search-input"
              disabled={loading}
            />
            <button 
              type="submit" 
              className="search-button"
              disabled={loading || !query.trim()}
            >
              {loading ? 'Vyhledávám...' : 'Vyhledat'}
            </button>
          </div>
        </form>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {results && (
          <div className="results-container">
            <div className="results-header">
              <h2>Výsledky pro: "{results.query}"</h2>
              <p>Nalezeno: {results.results_count} výsledků</p>
              <p>Čas vyhledávání: {results.timestamp}</p>
              
              <div className="export-buttons">
                <button 
                  onClick={() => handleExport('json')}
                  className="export-button"
                >
                  Stáhnout JSON
                </button>
                <button 
                  onClick={() => handleExport('csv')}
                  className="export-button"
                >
                  Stáhnout CSV
                </button>
              </div>
            </div>

            <div className="results-list">
              {results.results.map((result, index) => (
                <div key={index} className="result-item">
                  <div className="result-position">#{result.position}</div>
                  <div className="result-content">
                    <h3 className="result-title">{result.title}</h3>
                    <a 
                      href={result.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="result-url"
                    >
                      {result.url}
                    </a>
                    <p className="result-description">{result.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;