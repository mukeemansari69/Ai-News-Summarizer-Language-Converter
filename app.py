# from tts_output import speak_text
from googletrans import Translator
from flask import Flask, request, render_template, flash, redirect, url_for  # Import flash
import nltk
from textblob import TextBlob
from newspaper import Article
from datetime import datetime
from urllib.parse import urlparse
import validators
import requests

nltk.download('punkt')

app = Flask(__name__)

def get_website_name(url):
    # Extract the website name from the URL
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain

def translate_text(text, target_lang='hi'):
    translator = Translator()
    translated = translator.translate(text, dest=target_lang)
    return translated.text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        language = request.form.get('language', 'en')  # Get selected language

        if not validators.url(url):
            flash('Please enter a valid URL.')
            return redirect(url_for('index'))
        
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException:
            flash('Failed to download the content of the URL.')
            return redirect(url_for('index'))
        
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()

        title = article.title
        authors = ', '.join(article.authors)
        if not authors:
            authors = get_website_name(url)
        publish_date = article.publish_date.strftime('%B %d, %Y') if article.publish_date else "N/A"

        article_text = article.text
        sentences = article_text.split('.')
        max_summarized_sentences = 5
        summary = '.'.join(sentences[:max_summarized_sentences])

        translated_summary = translate_text(summary, target_lang=language)

        top_image = article.top_image

        analysis = TextBlob(article.text)
        polarity = analysis.sentiment.polarity

        if summary == "":
            flash('Please enter a valid URL.')
            return redirect(url_for('index'))

        if polarity > 0:
            sentiment = 'happy 😊'
        elif polarity < 0:
            sentiment = 'sad 😟'
        else:
            sentiment = 'neutral 😐'

        return render_template('index.html', title=title, authors=authors,
                               publish_date=publish_date, summary=summary,
                               translated_summary=translated_summary,
                               top_image=top_image, sentiment=sentiment)

    return render_template('index.html')

app.secret_key = 'your_secret_key'

if __name__ == '__main__':
    app.run(debug=True)
