import React, { useState, useCallback } from 'react';
import axios from 'axios';
import SearchForm from './components/SearchForm';
import SearchResults from './components/SearchResults';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchHistory, setSearchHistory] = useState([]);

  const handleSearch = useCallback(async (searchQuery) => {
    if (!searchQuery.trim()) {
      setError('Zadejte prosím hledaný výraz');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post('/search', { query: searchQuery });
      setResults(response.data.results || []);
      
      setSearchHistory(prev => [
        searchQuery,
        ...prev.filter(q => q !== searchQuery).slice(0, 4)
      ]);
      
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
  }, []);

  const clearResults = useCallback(() => {
    setResults([]);
    setError('');
    setQuery('');
  }, []);

  const clearHistory = useCallback(() => {
    setSearchHistory([]);
  }, []);

  return (
    <div className="app">
      <div className="app-container">
        <header className="app-header">
          <h1 className="app-title">
            <span className="title-icon">🔍</span>
            Search Tool
          </h1>
          <p className="app-subtitle">
            Vyhledávejte a exportujte výsledky jednoduše a rychle
          </p>
        </header>

        <main className="main-content">
          <SearchForm
            query={query}
            onQueryChange={setQuery}
            onSearch={handleSearch}
            loading={loading}
            searchHistory={searchHistory}
            onClearHistory={clearHistory}
          />

          {results.length > 0 && (
            <SearchResults
              results={results}
              query={query}
              onClear={clearResults}
            />
          )}
        </main>

        <footer className="app-footer">
          <p>© 2025 Search Tool</p>
        </footer>
      </div>
    </div>
  );
}

export default App;