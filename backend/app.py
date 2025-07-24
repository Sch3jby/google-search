from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import csv
import io
import time
import re

app = Flask(__name__)
CORS(app)

class GoogleSearcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'cs-CZ,cs;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search(self, query, num_results=10):
        """Vyhledá výsledky na Google a vrátí je jako strukturovaná data"""
        try:
            # Sestavení URL pro Google vyhledávání
            import urllib.parse
            encoded_query = urllib.parse.quote_plus(query)
            
            # Zkusíme několik různých URL variant
            urls_to_try = [
                f"https://www.google.com/search?q={encoded_query}&num={num_results}&hl=cs&gl=cz",
                f"https://www.google.cz/search?q={encoded_query}&num={num_results}",
                f"https://www.google.com/search?q={encoded_query}",
            ]
            
            for url in urls_to_try:
                print(f"DEBUG: Zkouším URL: {url}")
                
                try:
                    # Přidáme delay aby to nevypadalo jako bot
                    time.sleep(1)
                    
                    response = self.session.get(url, timeout=15)
                    response.raise_for_status()
                    
                    print(f"DEBUG: Response status: {response.status_code}")
                    print(f"DEBUG: Response length: {len(response.content)}")
                    
                    # Kontrola, zda nás Google nepřesměroval na CAPTCHA
                    if 'captcha' in response.text.lower() or 'unusual traffic' in response.text.lower():
                        print("DEBUG: Google detekoval neobvyklý provoz - CAPTCHA")
                        continue
                    
                    # Parsování HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Debug: kontrola základní struktury
                    print(f"DEBUG: Title stránky: {soup.title.text if soup.title else 'Nenalezen'}")
                    
                    results = self._parse_results(soup, num_results, query)
                    
                    if results:
                        return {
                            'query': query,
                            'results_count': len(results),
                            'results': results,
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                            'url_used': url
                        }
                    
                except requests.RequestException as e:
                    print(f"DEBUG: Chyba při požadavku na {url}: {e}")
                    continue
            
            # Pokud žádná URL nefungovala, vrátíme prázdné výsledky
            print("DEBUG: Žádná URL neposkytla výsledky")
            return {
                'query': query,
                'results_count': 0,
                'results': [],
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'error': 'Nepodarilo se ziskat vysledky - mozna Google blokuje pozadavky'
            }
            
        except Exception as e:
            print(f"DEBUG: Obecná chyba při vyhledávání: {str(e)}")
            raise Exception(f"Chyba při vyhledávání: {str(e)}")
    
    def _parse_results(self, soup, num_results, query):
        """Parsuje výsledky z HTML"""
        results = []
        
        # Uložíme HTML pro debug
        try:
            debug_file = f'/tmp/google_debug_{int(time.time())}.html'
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            print(f"DEBUG: HTML uloženo do {debug_file}")
        except:
            pass
        
        # Různé možné selektory pro Google výsledky
        selectors_to_try = [
            # Nejnovější selektory (2024)
            {'container': 'div[data-ved]', 'title': 'h3', 'link': 'a[href^="http"]', 'desc': '.VwiC3b'},
            {'container': '.tF2Cxc', 'title': 'h3', 'link': 'a[href^="http"]', 'desc': '.VwiC3b'},
            {'container': '.g', 'title': 'h3', 'link': 'a', 'desc': '.VwiC3b'},
            {'container': '.yuRUbf', 'title': 'h3', 'link': 'a', 'desc': '.VwiC3b'},
            
            # Starší selektory
            {'container': 'div.g', 'title': 'h3', 'link': 'a', 'desc': '.s3v9rd'},
            {'container': 'div.g', 'title': 'h3', 'link': 'a', 'desc': '.st'},
            
            # Fallback selektory
            {'container': 'div', 'title': 'h3', 'link': 'a[href*="http"]', 'desc': 'span'},
        ]
        
        for selector_set in selectors_to_try:
            print(f"DEBUG: Zkouším selektor set: {selector_set['container']}")
            
            containers = soup.select(selector_set['container'])
            print(f"DEBUG: Nalezeno {len(containers)} kontejnerů")
            
            if not containers:
                continue
                
            for i, container in enumerate(containers[:num_results]):
                try:
                    # Najdeme název
                    title_elem = container.select_one(selector_set['title'])
                    title = title_elem.get_text().strip() if title_elem else ""
                    
                    # Najdeme odkaz
                    link_elem = container.select_one(selector_set['link'])
                    url = ""
                    if link_elem:
                        href = link_elem.get('href', '')
                        if href:
                            # Očistíme Google redirect
                            if href.startswith('/url?q='):
                                url = href.split('q=')[1].split('&')[0]
                                url = urllib.parse.unquote(url)
                            elif href.startswith('http'):
                                url = href
                    
                    # Najdeme popis
                    desc_elem = container.select_one(selector_set['desc'])
                    description = desc_elem.get_text().strip() if desc_elem else ""
                    
                    # Přidáme pouze platné výsledky
                    if title and url and url.startswith('http') and len(title) > 3:
                        # Kontrola, že to není Google vlastní stránka
                        if not any(domain in url for domain in ['google.com', 'youtube.com/redirect']):
                            results.append({
                                'title': title,
                                'url': url,
                                'description': description or 'Popis není dostupný',
                                'position': len(results) + 1
                            })
                            print(f"DEBUG: Přidán výsledek #{len(results)}: {title[:50]}... -> {url[:50]}...")
                    
                except Exception as e:
                    print(f"DEBUG: Chyba při parsování kontejneru {i}: {e}")
                    continue
            
            if results:
                print(f"DEBUG: Úspěšně nalezeno {len(results)} výsledků pomocí {selector_set['container']}")
                break
        
        # Pokud nic nefunguje, zkusíme velmi obecný přístup
        if not results:
            print("DEBUG: Žádné selektory nefungovaly, zkouším fallback")
            self._fallback_parsing(soup, results, num_results)
        
        return results
    
    def _fallback_parsing(self, soup, results, num_results):
        """Záložní parsování když normální selektory nefungují"""
        print("DEBUG: Spouštím fallback parsing")
        
        # Najdeme všechny odkazy, které vypadají jako výsledky
        all_links = soup.find_all('a', href=True)
        print(f"DEBUG: Celkem nalezeno {len(all_links)} odkazů")
        
        for link in all_links:
            if len(results) >= num_results:
                break
                
            href = link.get('href', '')
            text = link.get_text().strip()
            
            # Filtrujeme pouze externí odkazy
            if (href.startswith('http') and 
                text and len(text) > 10 and len(text) < 200 and
                not any(skip in href for skip in ['google.com', 'youtube.com/redirect', 'accounts.google', 'support.google'])):
                
                # Pokusíme se najít popis v rodičovském elementu
                parent = link.parent
                description = ""
                if parent:
                    desc_text = parent.get_text().strip()
                    if len(desc_text) > len(text):
                        description = desc_text[len(text):].strip()[:200]
                
                results.append({
                    'title': text,
                    'url': href,
                    'description': description or 'Popis není dostupný',
                    'position': len(results) + 1
                })
                print(f"DEBUG: Fallback - přidán výsledek: {text[:30]}...")
        
        print(f"DEBUG: Fallback parsing našel {len(results)} výsledků")

searcher = GoogleSearcher()

@app.route('/api/search', methods=['POST'])
def search():
    """API endpoint pro vyhledávání"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'Zadejte vyhledávací dotaz'}), 400
        
        results = searcher.search(query)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<format>', methods=['POST'])
def export_results(format):
    """Export výsledků v různých formátech"""
    try:
        data = request.get_json()
        results = data.get('results', {})
        
        if format == 'json':
            output = io.StringIO()
            json.dump(results, output, ensure_ascii=False, indent=2)
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='application/json',
                as_attachment=True,
                download_name=f"search_results_{int(time.time())}.json"
            )
        
        elif format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow(['Position', 'Title', 'URL', 'Description'])
            
            # Data
            for result in results.get('results', []):
                writer.writerow([
                    result.get('position', ''),
                    result.get('title', ''),
                    result.get('url', ''),
                    result.get('description', '')
                ])
            
            output.seek(0)
            
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f"search_results_{int(time.time())}.csv"
            )
        
        else:
            return jsonify({'error': 'Nepodporovaný formát'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debug/<query>', methods=['GET'])
def debug_search(query):
    """Debug endpoint pro zobrazení raw HTML"""
    try:
        import urllib.parse
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}&num=10&hl=cs"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        return f"""
        <html>
        <head><title>Debug Google Search</title></head>
        <body>
        <h1>Debug pro dotaz: {query}</h1>
        <p>URL: {url}</p>
        <p>Status: {response.status_code}</p>
        <p>Content Length: {len(response.content)}</p>
        <hr>
        <pre>{response.text[:5000]}...</pre>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"Chyba: {str(e)}"

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'OK', 'message': 'Server is running'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)