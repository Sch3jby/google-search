import React, { useState, useMemo } from 'react';
import ExportButtons from './ExportButtons';
import './SearchResults.css';

const SearchResults = ({ results, query, onClear }) => {
  const [viewMode, setViewMode] = useState('list');
  
  const resultStats = useMemo(() => ({
    total: results.length,
    withSnippets: results.filter(r => r.snippet && r.snippet.trim()).length,
    avgSnippetLength: results.reduce((acc, r) => acc + (r.snippet?.length || 0), 0) / results.length
  }), [results]);

  const formatUrl = (url) => {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname.replace('www.', '');
    } catch {
      return url;
    }
  };

  const highlightQuery = (text, query) => {
    if (!text || !query) return text;
    
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<mark>$1</mark>');
  };

  const truncateText = (text, maxLength = 160) => {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
  };

  if (results.length === 0) {
    return null;
  }

  return (
    <div className="search-results">
      <div className="results-header card">
        <div className="card-header">
          <div className="results-meta">
            <h2 className="results-title">
              <span className="results-icon">📊</span>
              Výsledky vyhledávání
            </h2>
            <div className="results-info">
              <span className="results-count">
                Nalezeno <strong>{resultStats.total}</strong> výsledků pro "{query}"
              </span>
              <div className="results-stats">
                <span className="stat">
                  {resultStats.withSnippets} s popisem
                </span>
                <span className="stat-separator">•</span>
                <span className="stat">
                  Průměrná délka: {Math.round(resultStats.avgSnippetLength)} znaků
                </span>
              </div>
            </div>
          </div>

          <div className="results-actions">
            <div className="view-toggle">
              <button
                onClick={() => setViewMode('list')}
                className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
                title="Seznam"
              >
                📋
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
                title="Mřížka"
              >
                🔲
              </button>
            </div>

            <ExportButtons results={results} query={query} />
            
            <button 
              onClick={onClear}
              className="clear-btn btn btn-secondary btn-sm"
              title="Vymazat výsledky"
            >
              <span>🗑️</span>
              Vymazat
            </button>
          </div>
        </div>
      </div>

      <div className={`results-container ${viewMode === 'grid' ? 'grid-view' : 'list-view'}`}>
        {results.map((result, index) => (
          <div key={index} className="result-item card">
            <div className="card-body">
              <div className="result-header">
                <span className="result-position">
                  #{index + 1}
                </span>
                <div className="result-meta">
                  <span className="result-domain">
                    {formatUrl(result.link)}
                  </span>
                  <span className="result-timestamp">
                    {new Date().toLocaleTimeString('cs-CZ', { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </span>
                </div>
              </div>

              <h3 className="result-title">
                <a 
                  href={result.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="result-link"
                  dangerouslySetInnerHTML={{
                    __html: highlightQuery(result.title, query)
                  }}
                />
              </h3>

              <div className="result-url">
                <a 
                  href={result.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="result-url-link"
                >
                  🔗 {result.link}
                </a>
              </div>

              {result.snippet && (
                <p 
                  className="result-description"
                  dangerouslySetInnerHTML={{
                    __html: highlightQuery(truncateText(result.snippet), query)
                  }}
                />
              )}

              <div className="result-actions">
                <button
                  onClick={() => navigator.clipboard.writeText(result.link)}
                  className="action-btn btn btn-secondary btn-sm"
                  title="Kopírovat odkaz"
                >
                  📋 Kopírovat
                </button>
                <button
                  onClick={() => window.open(result.link, '_blank')}
                  className="action-btn btn btn-primary btn-sm"
                  title="Otevřít v novém okně"
                >
                  🚀 Otevřít
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {results.length > 10 && (
        <div className="results-footer">
          <button 
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="scroll-top-btn btn btn-secondary"
          >
            ⬆️ Zpět nahoru
          </button>
        </div>
      )}
    </div>
  );
};

export default SearchResults;