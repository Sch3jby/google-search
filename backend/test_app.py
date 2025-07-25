import unittest
from unittest.mock import patch, Mock
import json
from app import app

class TestSearchApp(unittest.TestCase):
    
    def setUp(self):
        """Nastavení testovacího prostředí"""
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_search_endpoint_exists(self):
        """Test, že endpoint /search existuje"""
        response = self.client.post('/search', 
                                   json={'query': 'test'},
                                   content_type='application/json')
        self.assertNotEqual(response.status_code, 404)
    
    def test_search_empty_query(self):
        """Test prázdného dotazu"""
        response = self.client.post('/search', 
                                   json={'query': ''},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Query is empty')
    
    def test_search_missing_query(self):
        """Test chybějícího parametru query"""
        response = self.client.post('/search', 
                                   json={},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
    
    def test_search_invalid_json(self):
        """Test nevalidního JSON"""
        response = self.client.post('/search', 
                                   data='invalid json',
                                   content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    @patch('app.requests.get')
    def test_search_successful_request(self, mock_get):
        """Test úspěšného vyhledávání"""
        # Mock HTML odpověď s výsledky pro DuckDuckGo
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
        
        response = self.client.post('/search', 
                                   json={'query': 'test query'},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
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
        
        response = self.client.post('/search', 
                                   json={'query': 'no results query'},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
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
        
        response = self.client.post('/search', 
                                   json={'query': 'test'},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(len(data['results']), 1)
        result = data['results'][0]
        self.assertEqual(result['title'], 'Example Title')
        self.assertEqual(result['link'], 'https://example.com')
        self.assertEqual(result['snippet'], '')  # Prázdný snippet
    
    @patch('app.requests.get')
    def test_search_no_link_tag(self, mock_get):
        """Test výsledku bez link tagu - měl by být přeskočen"""
        mock_html = '''
        <html>
            <body>
                <div class="result">
                    <span class="result__snippet">Snippet bez linku</span>
                </div>
                <div class="result">
                    <a class="result__a" href="https://valid.com">Valid Title</a>
                </div>
            </body>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_get.return_value = mock_response
        
        response = self.client.post('/search', 
                                   json={'query': 'test'},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        # Pouze jeden validní výsledek (druhý)
        self.assertEqual(len(data['results']), 1)
        result = data['results'][0]
        self.assertEqual(result['title'], 'Valid Title')
        self.assertEqual(result['link'], 'https://valid.com')
    
    @patch('app.requests.get')
    def test_search_url_encoding(self, mock_get):
        """Test správného URL enkódování dotazu"""
        mock_response = Mock()
        mock_response.text = '<html><body></body></html>'
        mock_get.return_value = mock_response
        
        query_with_spaces = 'test query with spaces'
        
        self.client.post('/search', 
                        json={'query': query_with_spaces},
                        content_type='application/json')
        
        # Kontrola, že byl request zavolán se správně enkódovanou URL
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        self.assertIn('test%20query%20with%20spaces', called_url)
        self.assertTrue(called_url.startswith('https://html.duckduckgo.com/html/?q='))
    
    @patch('app.requests.get')
    def test_search_headers_sent(self, mock_get):
        """Test, že se posílají správné hlavičky"""
        mock_response = Mock()
        mock_response.text = '<html><body></body></html>'
        mock_get.return_value = mock_response
        
        self.client.post('/search', 
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
        
        # V současné implementaci aplikace nemá exception handling
        # takže výjimka se propaguje nahoru - to je očekávané chování
        with self.assertRaises(Exception):
            response = self.client.post('/search', 
                                       json={'query': 'test'},
                                       content_type='application/json')
    
    def test_cors_enabled(self):
        """Test, že CORS je povolen"""
        response = self.client.options('/search')
        # CORS hlavičky by měly být přítomny
        self.assertIn('Access-Control-Allow-Origin', response.headers)
    
    @patch('app.requests.get')
    def test_special_characters_in_query(self, mock_get):
        """Test speciálních znaků v dotazu"""
        mock_response = Mock()
        mock_response.text = '<html><body></body></html>'
        mock_get.return_value = mock_response
        
        special_query = 'test & query with "quotes" and #hash'
        
        response = self.client.post('/search', 
                                   json={'query': special_query},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        mock_get.assert_called_once()
        called_url = mock_get.call_args[0][0]
        # URL by měla obsahovat enkódované speciální znaky
        self.assertIn('%20', called_url)  # mezera
        self.assertIn('%26', called_url)  # &
        self.assertIn('%22', called_url)  # "
        self.assertIn('%23', called_url)  # #
    
    @patch('app.requests.get')
    def test_complex_html_structure(self, mock_get):
        """Test parsování komplexnější HTML struktury"""
        mock_html = '''
        <html>
            <head><title>DuckDuckGo</title></head>
            <body>
                <div class="header">Header content</div>
                <div class="result">
                    <a class="result__a" href="https://first.com">
                        <b>First</b> Result Title
                    </a>
                    <span class="result__snippet">
                        This is a <em>detailed</em> snippet with HTML tags.
                    </span>
                </div>
                <div class="other-content">Other content</div>
                <div class="result">
                    <a class="result__a" href="https://second.com">Second Result</a>
                    <span class="result__snippet">Another snippet</span>
                </div>
                <div class="footer">Footer</div>
            </body>
        </html>
        '''
        
        mock_response = Mock()
        mock_response.text = mock_html
        mock_get.return_value = mock_response
        
        response = self.client.post('/search', 
                                   json={'query': 'test'},
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        
        self.assertEqual(len(data['results']), 2)
        
        # První výsledek - text bez HTML tagů (s ošetřením whitespace)
        first_result = data['results'][0]
        self.assertEqual(first_result['title'].strip(), 'First Result Title')
        self.assertEqual(first_result['link'], 'https://first.com')
        self.assertEqual(first_result['snippet'].strip(), 'This is a detailed snippet with HTML tags.')
        
        # Druhý výsledek
        second_result = data['results'][1]
        self.assertEqual(second_result['title'].strip(), 'Second Result')
        self.assertEqual(second_result['link'], 'https://second.com')
        self.assertEqual(second_result['snippet'].strip(), 'Another snippet')


if __name__ == '__main__':
    # Spuštění testů s podrobným výstupem
    unittest.main(verbosity=2)