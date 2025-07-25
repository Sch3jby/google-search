import React, { useState } from 'react';
import axios from 'axios';
import SearchForm from './components/SearchForm';
import SearchResults from './components/SearchResults';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (searchQuery) => {
    if (!searchQuery.trim()) {
      setError('Zadejte prosím hledaný výraz');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('/search', { query: searchQuery });
      setResults(response.data.results || []);
      setQuery(searchQuery);
      
      if (response.data.results?.length === 0) {
        setError('Nebyly nalezeny žádné výsledky');
      }
    } catch (err) {
      console.error('Chyba při vyhledávání:', err);
      setError(
        err.response?.data?.error || 
        'Došlo k chybě při vyhledávání. Zkuste to prosím znovu.'
      );
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setResults([]);
    setError('');
    setQuery('');
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🔍 Vyhledávání</h1>
          <p>Jednoduché vyhledávání s exportem</p>
        </header>

        <SearchForm onSearch={handleSearch} loading={loading} />

        {error && (
          <div className="error">{error}</div>
        )}

        {results.length > 0 && (
          <SearchResults
            results={results}
            query={query}
            onClear={clearResults}
          />
        )}
      </div>
    </div>
  );
}

export default App;