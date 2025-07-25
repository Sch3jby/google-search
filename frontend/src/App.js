import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('/search', { query });
      setResults(res.data.results);
    } catch (err) {
      console.error('Chyba:', err);
    }
  };

  const downloadJSON = () => {
    const blob = new Blob([JSON.stringify(results, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    downloadFile(url, 'vysledky.json');
  };

  const downloadCSV = () => {
    const header = ['nazev', 'link', 'popis'];
    const csvRows = [
      header.join(','), // hlavička
      ...results.map((r) =>
        [
          escapeCSV(r.title),
          escapeCSV(r.link),
          escapeCSV(r.snippet || ''),
        ].join(',')
      ),
    ];
    const blob = new Blob([csvRows.join('\n')], {
      type: 'text/csv',
    });
    const url = URL.createObjectURL(blob);
    downloadFile(url, 'vysledky.csv');
  };

  const downloadFile = (url, filename) => {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const escapeCSV = (text) => {
    if (!text) return '';
    return `"${text.replace(/"/g, '""')}"`;
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl mb-4">Google Search (bez API)</h1>
      <form onSubmit={handleSearch} className="mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Zadej hledaný výraz"
          className="border p-2 w-full mb-2"
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
          Hledat
        </button>
      </form>

      {results.length > 0 && (
        <div className="mb-4 space-x-2">
          <button onClick={downloadCSV} className="bg-green-600 text-white px-3 py-1 rounded">
            Stáhnout CSV
          </button>
          <button onClick={downloadJSON} className="bg-gray-700 text-white px-3 py-1 rounded">
            Stáhnout JSON
          </button>
        </div>
      )}

      <ul>
        {results.map((result, idx) => (
          <li key={idx} className="mb-4">
            <a href={result.link} target="_blank" rel="noopener noreferrer" className="text-blue-800 underline">
              {result.title}
            </a>
            <p className="text-sm">{result.snippet}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
