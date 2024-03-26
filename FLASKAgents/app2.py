from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def get_mdc_info():
    url = 'https://www.mdc.edu/academics/programs/bachelors.aspx'
    programs_info = []
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find each program category and its programs
            categories = soup.select('div.col-sm-6 h4 em, div.col-sm-6 h4')  # Adjust this selector based on actual content
            for category in categories:
                category_name = category.get_text(strip=True)
                ul = category.find_next_sibling("ul")
                if ul:
                    programs = ul.find_all("li")
                    for program in programs:
                        program_name = program.get_text(strip=True)
                        program_url = program.find("a")["href"] if program.find("a") else "No URL"
                        programs_info.append({
                            "category": category_name,
                            "program": program_name,
                            "url": f"https://www.mdc.edu{program_url}"  # Assuming relative URLs need to be completed
                        })
        else:
            return 'Failed to retrieve content, status code: ' + str(response.status_code)
    except Exception as e:
        return 'Error: ' + str(e)

    return programs_info

# Route to handle chat messages
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data['message'].lower()
    if message == 'fetch mdc info':
        info = get_mdc_info()
        if isinstance(info, list):  # Check if the result is a list (expected for successful scraping)
            return jsonify(info)
        else:
            return jsonify({"response": info})  # Return error info if not a list
    else:
        return jsonify({"response": "Sorry, I don't understand. Please use the 'fetch mdc info' command to retrieve information from MDC."})

if __name__ == '__main__':
    app.run(debug=True)
