import pytest
import json
from unittest.mock import patch, Mock
from app import app, GoogleSearcher

@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_search_results():
    """Mock data pro testování"""
    return {
        'query': 'test query',
        'results_count': 2,
        'results': [
            {
                'title': 'Test Title 1',
                'url': 'https://example1.com',
                'description': 'Test description 1',
                'position': 1
            },
            {
                'title': 'Test Title 2',
                'url': 'https://example2.com',
                'description': 'Test description 2',
                'position': 2
            }
        ],
        'timestamp': '2024-01-01 12:00:00'
    }

class TestGoogleSearcher:
    """Testy pro GoogleSearcher třídu"""
    
    def test_init(self):
        """Test inicializace"""
        searcher = GoogleSearcher()
        assert 'User-Agent' in searcher.headers
        assert 'Mozilla' in searcher.headers['User-Agent']
    
    @patch('requests.get')
    def test_search_success(self, mock_get):
        """Test úspěšného vyhledávání"""
        # Mock HTML response
        mock_html = '''
        <html>
            <div class="g">
                <h3>Test Title</h3>
                <a href="https://example.com">Link</a>
                <span data-ved="true">Test description</span>
            </div>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.content = mock_html.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        searcher = GoogleSearcher()
        result = searcher.search('test query')
        
        assert result['query'] == 'test query'
        assert result['results_count'] >= 0
        assert 'results' in result
        assert 'timestamp' in result
    
    @patch('requests.get')
    def test_search_network_error(self, mock_get):
        """Test chyby sítě"""
        mock_get.side_effect = Exception("Network error")
        
        searcher = GoogleSearcher()
        
        with pytest.raises(Exception) as exc_info:
            searcher.search('test query')
        
        assert "Chyba při vyhledávání" in str(exc_info.value)

class TestAPI:
    """Testy pro API endpointy"""
    
    def test_health_endpoint(self, client):
        """Test health check endpointu"""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'OK'
    
    @patch('app.searcher.search')
    def test_search_endpoint_success(self, mock_search, client, mock_search_results):
        """Test úspěšného vyhledávání přes API"""
        mock_search.return_value = mock_search_results
        
        response = client.post('/api/search', 
                              json={'query': 'test query'},
                              content_type='application/json')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['query'] == 'test query'
        assert data['results_count'] == 2
        assert len(data['results']) == 2
        assert data['results'][0]['title'] == 'Test Title 1'
    
    def test_search_endpoint_empty_query(self, client):
        """Test s prázdným dotazem"""
        response = client.post('/api/search', 
                              json={'query': ''},
                              content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_search_endpoint_no_query(self, client):
        """Test bez dotazu"""
        response = client.post('/api/search', 
                              json={},
                              content_type='application/json')
        
        assert response.status_code == 400
    
    @patch('app.searcher.search')
    def test_search_endpoint_error(self, mock_search, client):
        """Test chyby při vyhledávání"""
        mock_search.side_effect = Exception("Search error")
        
        response = client.post('/api/search', 
                              json={'query': 'test query'},
                              content_type='application/json')
        
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_export_json(self, client, mock_search_results):
        """Test exportu do JSON"""
        response = client.post('/api/export/json',
                              json={'results': mock_search_results},
                              content_type='application/json')
        
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        assert 'attachment' in response.headers.get('Content-Disposition', '')
    
    def test_export_csv(self, client, mock_search_results):
        """Test exportu do CSV"""
        response = client.post('/api/export/csv',
                              json={'results': mock_search_results},
                              content_type='application/json')
        
        assert response.status_code == 200
        assert response.mimetype == 'text/csv'
        assert 'attachment' in response.headers.get('Content-Disposition', '')
    
    def test_export_unsupported_format(self, client, mock_search_results):
        """Test nepodporovaného formátu"""
        response = client.post('/api/export/xml',
                              json={'results': mock_search_results},
                              content_type='application/json')
        
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'error' in data

class TestDataValidation:
    """Testy pro validaci dat"""
    
    def test_search_result_structure(self, mock_search_results):
        """Test struktury výsledků vyhledávání"""
        results = mock_search_results
        
        # Kontrola základní struktury
        assert 'query' in results
        assert 'results_count' in results
        assert 'results' in results
        assert 'timestamp' in results
        
        # Kontrola struktury jednotlivých výsledků
        for result in results['results']:
            assert 'title' in result
            assert 'url' in result
            assert 'description' in result
            assert 'position' in result
            
            # Kontrola datových typů
            assert isinstance(result['title'], str)
            assert isinstance(result['url'], str)
            assert isinstance(result['description'], str)
            assert isinstance(result['position'], int)
    
    def test_results_count_consistency(self, mock_search_results):
        """Test konzistence počtu výsledků"""
        results = mock_search_results
        
        actual_count = len(results['results'])
        reported_count = results['results_count']
        
        assert actual_count == reported_count

if __name__ == '__main__':
    pytest.main(['-v', __file__])