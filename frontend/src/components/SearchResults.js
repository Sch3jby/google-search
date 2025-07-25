import React from 'react';
import ExportButtons from './ExportButtons';

const SearchResults = ({ results, query, onClear }) => {
  return (
    <div>
      <div className="card">
        <div className="card-body">
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
            flexWrap: 'wrap',
            gap: '10px'
          }}>
            <h2 style={{ margin: 0, fontSize: '1.3rem', color: '#333' }}>
              Nalezeno {results.length} výsledků
            </h2>
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
              <ExportButtons results={results} query={query} />
              <button onClick={onClear} className="btn btn-danger">
                Vymazat
              </button>
            </div>
          </div>
        </div>
      </div>

      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {results.map((result, index) => (
          <div key={index} className="card">
            <div className="card-body">
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                marginBottom: '12px'
              }}>
                <span style={{
                  backgroundColor: '#007bff',
                  color: 'white',
                  padding: '4px 12px',
                  borderRadius: '16px',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  flexShrink: 0
                }}>
                  #{index + 1}
                </span>
              </div>

              <h3 style={{
                margin: '0 0 8px 0',
                fontSize: '1.2rem',
                fontWeight: '600'
              }}>
                <a
                  href={result.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: '#007bff',
                    textDecoration: 'none',
                    wordWrap: 'break-word',
                    overflowWrap: 'break-word',
                    wordBreak: 'break-word',
                    lineHeight: '1.3'
                  }}
                  onMouseOver={(e) => e.target.style.textDecoration = 'underline'}
                  onMouseOut={(e) => e.target.style.textDecoration = 'none'}
                >
                  {result.title}
                </a>
              </h3>

              <div style={{ marginBottom: '12px' }}>
                <a
                  href={result.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="url-link"
                  style={{
                    color: '#28a745',
                    fontSize: '14px',
                    textDecoration: 'none',
                    wordWrap: 'break-word',
                    overflowWrap: 'break-word',
                    wordBreak: 'break-all',
                    lineHeight: '1.4',
                    display: 'block'
                  }}
                >
                  {result.link}
                </a>
              </div>

              {result.snippet && (
                <p style={{
                  color: '#666',
                  lineHeight: '1.5',
                  margin: 0,
                  fontSize: '15px',
                  wordWrap: 'break-word',
                  overflowWrap: 'break-word'
                }}>
                  {result.snippet}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchResults;