from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def get_mdc_info():
    # Placeholder implementation
    return {"info": "MDC Info not available"}

def generate_synopsis(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # will raise an HTTPError if the HTTP request returned an unsuccessful status code
        
        # Use BeautifulSoup to parse the page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract the main content text, here we just combine all paragraph texts
        # This should be replaced with your actual logic for synopsis generation
        paragraphs = soup.find_all('p')
        content = ' '.join([para.get_text() for para in paragraphs])
        synopsis = content[:500] + '...'  # Just a simple truncation for demonstration
        
        return synopsis
    except requests.RequestException as e:
        # Handle any requests exceptions here, like for HTTP errors, URL not found etc.
        return str(e)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data['message'].strip()
    if message.lower().startswith('fetch mdc info'):
        info = get_mdc_info()
        return jsonify(info)
    elif message.lower().startswith('generate synopsis'):
        url = message[18:].strip()  # Extract URL after 'generate synopsis'
        synopsis = generate_synopsis(url)
        return jsonify({"response": synopsis})
    else:
        return jsonify({"response": "Sorry, I don't understand. Please use a recognized command."})

if __name__ == '__main__':
    app.run(debug=True)
