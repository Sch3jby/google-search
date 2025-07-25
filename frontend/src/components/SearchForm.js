import React, { useState, useRef, useEffect } from 'react';
import './SearchForm.css';

const SearchForm = ({ 
  query, 
  onQueryChange, 
  onSearch, 
  loading, 
  searchHistory, 
  onClearHistory 
}) => {
  const [showHistory, setShowHistory] = useState(false);
  const inputRef = useRef(null);
  const historyRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
      setShowHistory(false);
    }
  };

  const handleHistoryClick = (historyQuery) => {
    onQueryChange(historyQuery);
    onSearch(historyQuery);
    setShowHistory(false);
  };

  const handleInputFocus = () => {
    if (searchHistory.length > 0) {
      setShowHistory(true);
    }
  };

  const handleInputChange = (e) => {
    onQueryChange(e.target.value);
    if (e.target.value === '' && searchHistory.length > 0) {
      setShowHistory(true);
    }
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (
        historyRef.current && 
        !historyRef.current.contains(event.target) &&
        !inputRef.current.contains(event.target)
      ) {
        setShowHistory(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setShowHistory(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="search-form-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-group">
          <div className="search-input-wrapper">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={handleInputChange}
              onFocus={handleInputFocus}
              placeholder="Zadejte hledaný výraz..."
              className="search-input input input-lg"
              disabled={loading}
              autoComplete="off"
              spellCheck="false"
            />
            <div className="search-input-icon">
              🔍
            </div>
          </div>
          
          <button 
            type="submit" 
            className="search-button btn btn-primary btn-lg"
            disabled={loading || !query.trim()}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                Hledám...
              </>
            ) : (
              <>
                <span>🚀</span>
                Vyhledat
              </>
            )}
          </button>
        </div>

        {/* Historie vyhledávání */}
        {showHistory && searchHistory.length > 0 && (
          <div ref={historyRef} className="search-history">
            <div className="search-history-header">
              <span className="search-history-title">
                <span className="history-icon">🕐</span>
                Nedávno hledáno
              </span>
              <button
                type="button"
                onClick={onClearHistory}
                className="clear-history-btn btn btn-secondary btn-sm"
              >
                Smazat historii
              </button>
            </div>
            <ul className="search-history-list">
              {searchHistory.map((historyQuery, index) => (
                <li key={index} className="search-history-item">
                  <button
                    type="button"
                    onClick={() => handleHistoryClick(historyQuery)}
                    className="search-history-link"
                  >
                    <span className="history-query-icon">🔍</span>
                    {historyQuery}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </form>

      {/* Rychlé tipy */}
      <div className="search-tips">
        <div className="search-tips-header">
          <span className="tips-icon">💡</span>
          Tipy pro vyhledávání:
        </div>
        <div className="search-tips-list">
          <span className="tip">Použijte specifické klíčová slova</span>
          <span className="tip-separator">•</span>
          <span className="tip">Kombinujte více termínů</span>
          <span className="tip-separator">•</span>
          <span className="tip">Zkuste synonyma</span>
        </div>
      </div>
    </div>
  );
};

export default SearchForm;