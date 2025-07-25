from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '')
    if not query:
        return jsonify({'error': 'Query is empty'}), 400

    search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    response = requests.get(search_url, headers=HEADERS)

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []

    for result in soup.select('.result'):
        link_tag = result.select_one('.result__a')
        snippet_tag = result.select_one('.result__snippet')
        if link_tag:
            results.append({
                'title': link_tag.text,
                'link': link_tag['href'],
                'snippet': snippet_tag.text if snippet_tag else ''
            })

    return jsonify({'results': results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
