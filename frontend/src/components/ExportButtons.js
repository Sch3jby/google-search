import React, { useState } from 'react';
import './ExportButtons.css';

const ExportButtons = ({ results, query }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [exportType, setExportType] = useState('');

  const generateTimestamp = () => {
    const now = new Date();
    return now.toISOString().slice(0, 19).replace(/[:-]/g, '').replace('T', '_');
  };

  const sanitizeFilename = (filename) => {
    return filename.replace(/[^a-z0-9]/gi, '_').toLowerCase();
  };

  const createFileName = (extension) => {
    const timestamp = generateTimestamp();
    const queryPart = sanitizeFilename(query.substring(0, 30));
    return `vysledky_${queryPart}_${timestamp}.${extension}`;
  };

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

  const escapeCSV = (text) => {
    if (!text) return '';
    const escaped = text.replace(/"/g, '""');
    return `"${escaped}"`;
  };

  const exportToJSON = async () => {
    setIsExporting(true);
    setExportType('json');
    
    try {
      const exportData = {
        metadata: {
          query,
          timestamp: new Date().toISOString(),
          totalResults: results.length,
          exportedBy: 'Search Tool v1.0'
        },
        results: results.map((result, index) => ({
          position: index + 1,
          title: result.title,
          url: result.link,
          snippet: result.snippet || '',
          domain: extractDomain(result.link)
        }))
      };

      const jsonContent = JSON.stringify(exportData, null, 2);
      const filename = createFileName('json');
      
      downloadFile(jsonContent, filename, 'application/json');
      
      // Zobrazit notifikaci o úspěchu
      showNotification('JSON soubor byl úspěšně stažen!', 'success');
      
    } catch (error) {
      console.error('Chyba při exportu JSON:', error);
      showNotification('Chyba při exportu JSON souboru.', 'error');
    } finally {
      setIsExporting(false);
      setExportType('');
    }
  };

  const exportToCSV = async () => {
    setIsExporting(true);
    setExportType('csv');
    
    try {
      const headers = ['Pozice', 'Nadpis', 'URL', 'Popis', 'Doména'];
      const csvRows = [
        headers.join(','),
        ...results.map((result, index) => [
          index + 1,
          escapeCSV(result.title),
          escapeCSV(result.link),
          escapeCSV(result.snippet || ''),
          escapeCSV(extractDomain(result.link))
        ].join(','))
      ];

      const csvContent = '\uFEFF' + csvRows.join('\n'); // BOM pro správné zobrazení českých znaků
      const filename = createFileName('csv');
      
      downloadFile(csvContent, filename, 'text/csv;charset=utf-8');
      
      showNotification('CSV soubor byl úspěšně stažen!', 'success');
      
    } catch (error) {
      console.error('Chyba při exportu CSV:', error);
      showNotification('Chyba při exportu CSV souboru.', 'error');
    } finally {
      setIsExporting(false);
      setExportType('');
    }
  };

  const exportToTXT = async () => {
    setIsExporting(true);
    setExportType('txt');
    
    try {
      const txtContent = [
        `VÝSLEDKY VYHLEDÁVÁNÍ`,
        `===================`,
        `Dotaz: ${query}`,
        `Čas: ${new Date().toLocaleString('cs-CZ')}`,
        `Počet výsledků: ${results.length}`,
        ``,
        ...results.map((result, index) => [
          `${index + 1}. ${result.title}`,
          `   URL: ${result.link}`,
          `   Doména: ${extractDomain(result.link)}`,
          result.snippet ? `   Popis: ${result.snippet}` : '',
          ''
        ].join('\n'))
      ].join('\n');

      const filename = createFileName('txt');
      
      downloadFile(txtContent, filename, 'text/plain;charset=utf-8');
      
      showNotification('TXT soubor byl úspěšně stažen!', 'success');
      
    } catch (error) {
      console.error('Chyba při exportu TXT:', error);
      showNotification('Chyba při exportu TXT souboru.', 'error');
    } finally {
      setIsExporting(false);
      setExportType('');
    }
  };

  const extractDomain = (url) => {
    try {
      return new URL(url).hostname.replace('www.', '');
    } catch {
      return url;
    }
  };

  const showNotification = (message, type) => {
    // Jednoduchá notifikace - v reálné aplikaci by se použila robustnější řešení
    const notification = document.createElement('div');
    notification.className = `export-notification ${type}`;
    notification.textContent = message;
    
    notification.style.cssText = `
      position: fixed;
      top: 2rem;
      right: 2rem;
      padding: 1rem 1.5rem;
      border-radius: 8px;
      color: white;
      font-weight: 600;
      z-index: 10000;
      animation: slideInRight 0.3s ease-out;
      ${type === 'success' ? 'background: var(--success-color);' : 'background: var(--danger-color);'}
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideOutRight 0.3s ease-in forwards';
      setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
  };

  if (results.length === 0) {
    return null;
  }

  return (
    <div className="export-buttons">
      <div className="export-dropdown">
        <button 
          className="export-trigger btn btn-success btn-sm"
          disabled={isExporting}
        >
          {isExporting ? (
            <>
              <span className="loading-spinner"></span>
              Exportuji...
            </>
          ) : (
            <>
              <span>📥</span>
              Export ({results.length})
            </>
          )}
        </button>
        
        <div className="export-menu">
          <div className="export-menu-header">
            <span className="export-icon">📊</span>
            Vyberte formát exportu
          </div>
          
          <button 
            onClick={exportToJSON}
            className="export-option"
            disabled={isExporting}
          >
            <div className="export-option-content">
              <span className="export-option-icon">📄</span>
              <div className="export-option-text">
                <div className="export-option-title">JSON</div>
                <div className="export-option-desc">Strukturovaná data s metadaty</div>
              </div>
            </div>
            {exportType === 'json' && <span className="loading-spinner"></span>}
          </button>
          
          <button 
            onClick={exportToCSV}
            className="export-option"
            disabled={isExporting}
          >
            <div className="export-option-content">
              <span className="export-option-icon">📊</span>
              <div className="export-option-text">
                <div className="export-option-title">CSV</div>
                <div className="export-option-desc">Tabulková data pro Excel</div>
              </div>
            </div>
            {exportType === 'csv' && <span className="loading-spinner"></span>}
          </button>
          
          <button 
            onClick={exportToTXT}
            className="export-option"
            disabled={isExporting}
          >
            <div className="export-option-content">
              <span className="export-option-icon">📝</span>
              <div className="export-option-text">
                <div className="export-option-title">TXT</div>
                <div className="export-option-desc">Prostý text pro čtení</div>
              </div>
            </div>
            {exportType === 'txt' && <span className="loading-spinner"></span>}
          </button>
          
          <div className="export-menu-footer">
            <small>Soubory obsahují všechny nalezené výsledky</small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportButtons;