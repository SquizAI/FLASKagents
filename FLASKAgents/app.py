from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter

app = Flask(__name__)

@app.route('/')
def index():
    # Renders the main HTML page.
    return render_template('index.html')

def get_keywords(content, number_of_keywords):
    # Tokenize the content and filter out stopwords and non-alphanumeric words.
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(content.lower())
    filtered_words = [word for word in word_tokens if word.isalnum() and not word in stop_words]

    # Count and return the most common words.
    most_common_words = Counter(filtered_words).most_common(number_of_keywords)
    keywords = [word for word, count in most_common_words]
    return keywords

def format_synopsis(text, tone):
    # Splits the text into sentences.
    sentences = text.split('. ')
    num_sentences = len(sentences)

    # Adjusts the format based on the tone.
    if tone == "technical":
        formatted_text = "Technical Overview:\n" + "\n".join(["- " + sentence for sentence in sentences[:min(3, num_sentences)]])
    elif tone == "school_report":
        intro = "Introduction: " + " ".join(sentences[:max(1, num_sentences // 5)]) + "."
        body = "Body: " + " ".join(sentences[max(1, num_sentences // 5):-max(1, num_sentences // 5)]) + "."
        conclusion = "Conclusion: " + " ".join(sentences[-max(1, num_sentences // 5):]) + "."
        formatted_text = f"{intro}\n\n{body}\n\n{conclusion}"
    elif tone == "blog":
        opener = "Let's talk about something interesting today. Did you know?"
        main_content = " ".join(sentences[:max(1, num_sentences - 1)])
        closer = "What are your thoughts on this? Share your views below."
        formatted_text = f"{opener}\n\n{main_content}\n\n{closer}"
    else:  # General tone
        formatted_text = ". ".join(sentences[:num_sentences]) + "."

    return formatted_text

def generate_synopsis(url, word_count, tone, keywords_count):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extracts all text from <p> tags.
        text = ' '.join(p.get_text() for p in soup.find_all('p'))
        # Limit the text to the requested word count approximately.
        limited_text = ' '.join(text.split()[:word_count])
        formatted_text = format_synopsis(limited_text, tone)
        keywords = get_keywords(formatted_text, keywords_count)
        return formatted_text, keywords
    except requests.RequestException as e:
        return f"Error fetching URL: {str(e)}", []

@app.route('/generate_synopsis', methods=['POST'])
def handle_generate_synopsis():
    # Extracts data from the request.
    data = request.get_json()
    url = data.get('url')
    word_count = int(data.get('word_count', 500))
    tone = data.get('tone', 'general')
    keywords_count = int(data.get('keywords_count', 10))

    synopsis, keywords = generate_synopsis(url, word_count, tone, keywords_count)
    if synopsis:
        return jsonify({"synopsis": synopsis, "keywords": keywords})
    else:
        return jsonify({"error": synopsis}), 500

if __name__ == '__main__':
    app.run(debug=True)
