import unittest
from unittest.mock import patch, Mock
import json
from app import app

class TestSearchApp(unittest.TestCase):
    
    def setUp(self):
        """Nastavení testovacího prostředí"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_search_endpoint_exists(self):
        """Test, že endpoint /search existuje"""
        response = self.app.post('/search', 
                                json={'query': 'test'},
                                content_type='application/json')
        self.assertNotEqual(response.status_code, 404)
    
    def test_search_empty_query(self):
        """Test prázdného dotazu"""
        response = self.app.post('/search', 
                                json={'query': ''},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Query is empty')
    
    def test_search_missing_query(self):
        """Test chybějícího parametru query"""
        response = self.app.post('/search', 
                                json={},
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_search_invalid_json(self):
        """Test nevalidního JSON"""
        response = self.app.post('/search', 
                                data='invalid json',
                                content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.requests.get')
    def test_search_successful_request(self, mock_get):
        """Test úspěšného vyhledávání"""
        # Mock HTML odpověď s výsledky
        mock_html = '''
        <html>
            <body>
                <div class="result">
                    <a class="result__a" href="https://example.com">Example Title</a>
                    <span class="result__snippet">Example snippet text</span>
                </div>
                <div class="result">
                    <a class="result__a" href="https://test.com">Test Title</a>
                    <span class="result__snippet">Test snippet text</span>
                </div>
            </body>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_get.return_value = mock_response
        
        response = self.app.post('/search', 
                                json={'query': 'test query'},
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 2)
        
        # Kontrola prvního výsledku
        first_result = data['results'][0]
        self.assertEqual(first_result['title'], 'Example Title')
        self.assertEqual(first_result['link'], 'https://example.com')
        self.assertEqual(first_result['snippet'], 'Example snippet text')
        
        # Kontrola druhého výsledku
        second_result = data['results'][1]
        self.assertEqual(second_result['title'], 'Test Title')
        self.assertEqual(second_result['link'], 'https://test.com')
        self.assertEqual(second_result['snippet'], 'Test snippet text')
    
    @patch('app.requests.get')
    def test_search_no_results(self, mock_get):
        """Test vyhledávání bez výsledků"""
        mock_html = '<html><body></body></html>'
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_get.return_value = mock_response
        
        response = self.app.post('/search', 
                                json={'query': 'no results query'},
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 0)
    
    @patch('app.requests.get')
    def test_search_missing_snippet(self, mock_get):
        """Test výsledku bez snippet"""
        mock_html = '''
        <html>
            <body>
                <div class="result">
                    <a class="result__a" href="https://example.com">Example Title</a>
                </div>
            </body>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_get.return_value = mock_response
        
        response = self.app.post('/search', 
                                json={'query': 'test'},
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(len(data['results']), 1)
        result = data['results'][0]
        self.assertEqual(result['title'], 'Example Title')
        self.assertEqual(result['link'], 'https://example.com')
        self.assertEqual(result['snippet'], '')  # Prázdný snippet
    
    @patch('app.requests.get')
    def test_search_url_encoding(self, mock_get):
        """Test správného URL enkódování dotazu"""
        mock_response = Mock()
        mock_response.text = '<html><body></body></html>'
        mock_get.return_value = mock_response
        
        query_with_spaces = 'test query with spaces'
        
        self.app.post('/search', 
                     json={'query': query_with_spaces},
                     content_type='application/json')
        
        # Kontrola, že byl request zavolán se správně enkódovanou URL
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        self.assertIn('test%20query%20with%20spaces', called_url)
    
    @patch('app.requests.get')
    def test_search_headers_sent(self, mock_get):
        """Test, že se posílají správné hlavičky"""
        mock_response = Mock()
        mock_response.text = '<html><body></body></html>'
        mock_get.return_value = mock_response
        
        self.app.post('/search', 
                     json={'query': 'test'},
                     content_type='application/json')
        
        # Kontrola hlaviček
        mock_get.assert_called_once()
        called_headers = mock_get.call_args[1]['headers']
        self.assertEqual(called_headers['User-Agent'], 'Mozilla/5.0')
    
    @patch('app.requests.get')
    def test_search_request_exception(self, mock_get):
        """Test chování při výjimce v requests"""
        mock_get.side_effect = Exception('Connection error')
        
        response = self.app.post('/search', 
                                json={'query': 'test'},
                                content_type='application/json')
        
        # Aplikace by měla spadnout nebo vrátit chybu
        # V současné implementaci není exception handling
        self.assertEqual(response.status_code, 500)
    
    def test_cors_enabled(self):
        """Test, že CORS je povolen"""
        response = self.app.options('/search')
        # CORS hlavičky by měly být přítomny
        self.assertIn('Access-Control-Allow-Origin', response.headers)


class TestSearchAppIntegration(unittest.TestCase):
    """Integrační testy - vyžadují internetové připojení"""
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    @unittest.skip("Přeskočeno - vyžaduje internetové připojení")
    def test_real_search_request(self):
        """Integrační test se skutečným požadavkem na DuckDuckGo"""
        response = self.app.post('/search', 
                                json={'query': 'python programming'},
                                content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('results', data)
        # Očekáváme alespoň nějaké výsledky pro běžný dotaz
        self.assertGreater(len(data['results']), 0)


if __name__ == '__main__':
    # Spuštění testů
    unittest.main(verbosity=2)