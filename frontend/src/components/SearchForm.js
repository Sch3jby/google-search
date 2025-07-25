import React, { useState } from 'react';

const SearchForm = ({ onSearch, loading }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = () => {
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  return (
    <div style={{
      display: 'flex',
      gap: '10px',
      marginBottom: '30px'
    }}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Zadejte hledaný výraz..."
        disabled={loading}
        style={{
          flex: 1,
          padding: '12px 16px',
          fontSize: '16px',
          border: '2px solid #ddd',
          borderRadius: '8px',
          outline: 'none'
        }}
        onFocus={(e) => e.target.style.borderColor = '#007bff'}
        onBlur={(e) => e.target.style.borderColor = '#ddd'}
      />
      <button
        onClick={handleSubmit}
        disabled={loading || !query.trim()}
        className="btn btn-primary"
        style={{ minWidth: '120px' }}
      >
        {loading ? 'Hledám...' : 'Vyhledat'}
      </button>
    </div>
  );
};

export default SearchForm;