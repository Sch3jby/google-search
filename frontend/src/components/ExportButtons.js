import React, { useState } from 'react';

const ExportButtons = ({ results, query }) => {
  const [isExporting, setIsExporting] = useState(false);

  const downloadFile = (content, filename, mimeType) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
  };

  const createFileName = (extension) => {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '').replace('T', '_');
    const queryPart = query.replace(/[^a-z0-9]/gi, '_').toLowerCase().substring(0, 30);
    return `vysledky_${queryPart}_${timestamp}.${extension}`;
  };

  const exportToJSON = async () => {
    setIsExporting(true);
    
    try {
      const exportData = {
        query,
        timestamp: new Date().toISOString(),
        totalResults: results.length,
        results: results.map((result, index) => ({
          position: index + 1,
          title: result.title,
          url: result.link,
          snippet: result.snippet || ''
        }))
      };

      const jsonContent = JSON.stringify(exportData, null, 2);
      const filename = createFileName('json');
      
      downloadFile(jsonContent, filename, 'application/json');
      alert('JSON soubor byl úspěšně stažen!');
      
    } catch (error) {
      alert('Chyba při exportu JSON souboru.');
    } finally {
      setIsExporting(false);
    }
  };

  const exportToCSV = async () => {
    setIsExporting(true);
    
    try {
      const headers = ['Pozice', 'Nadpis', 'URL', 'Popis'];
      const csvRows = [
        headers.join(','),
        ...results.map((result, index) => [
          index + 1,
          `"${result.title.replace(/"/g, '""')}"`,
          `"${result.link}"`,
          `"${(result.snippet || '').replace(/"/g, '""')}"`
        ].join(','))
      ];

      const csvContent = '\uFEFF' + csvRows.join('\n');
      const filename = createFileName('csv');
      
      downloadFile(csvContent, filename, 'text/csv;charset=utf-8');
      alert('CSV soubor byl úspěšně stažen!');
      
    } catch (error) {
      alert('Chyba při exportu CSV souboru.');
    } finally {
      setIsExporting(false);
    }
  };

  if (results.length === 0) {
    return null;
  }

  return (
    <div style={{ display: 'flex', gap: '10px' }}>
      <button 
        onClick={exportToJSON}
        disabled={isExporting}
        className="btn btn-success"
      >
        {isExporting ? 'Exportuji...' : '📄 JSON'}
      </button>
      <button 
        onClick={exportToCSV}
        disabled={isExporting}
        className="btn btn-success"
      >
        {isExporting ? 'Exportuji...' : '📊 CSV'}
      </button>
    </div>
  );
};

export default ExportButtons;