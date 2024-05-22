import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline
from pymongo import MongoClient
import re

# Download VADER lexicon
nltk.download('vader_lexicon')

# Initialize sentiment analyzers
vader_analyzer = SentimentIntensityAnalyzer()
bert_analyzer = pipeline('sentiment-analysis')

# List of relevant keywords
keywords = ['repair', 'healthy', 'battery', 'change', 'remove', 'removal', 'easy', 'hard', 'repair', 'repairability']


# Function to preprocess text
def preprocess_text(text):
    text = text.lower()
    text = ''.join(e for e in text if e.isalnum() or e.isspace())
    return text


# Function to extract key sentences based on keywords
def extract_key_sentences(text, keywords):
    sentences = text.split('. ')
    key_sentences = [sentence for sentence in sentences if any(keyword in sentence for keyword in keywords)]
    return ' '.join(key_sentences)


# Function to analyze sentiment using VADER
def analyze_sentiment_vader(text):
    return vader_analyzer.polarity_scores(text)


# Function to analyze sentiment using TextBlob
def analyze_sentiment_textblob(text):
    blob = TextBlob(text)
    return blob.sentiment.polarity


# Function to analyze sentiment using BERT
def analyze_sentiment_bert(text):
    result = bert_analyzer(text)
    return result[0]['label'], result[0]['score']


# Connect to MongoDB
def get_database():
    client = MongoClient("mongodb://localhost:27017/")
    return client['dpp']


# Perform sentiment analysis on transcripts and update MongoDB
def perform_sentiment_analysis_and_update():
    db = get_database()
    collection = db.youtube

    # Retrieve all documents
    documents = collection.find()

    for document in documents:
        print("hey")
        updated_videos = []

        for video in document['videos']:
            transcript = preprocess_text(video['transcript'])
            reduced_transcript = extract_key_sentences(transcript, keywords)

            vader_result = analyze_sentiment_vader(reduced_transcript)
            textblob_result = analyze_sentiment_textblob(reduced_transcript)
            # bert_result = analyze_sentiment_bert(reduced_transcript)

            # Add sentiment results to the video document
            video['sentiment_vader'] = vader_result
            video['sentiment_textblob'] = textblob_result
            #video['sentiment_bert'] = {
            #    'label': bert_result[0],
            #    'score': bert_result[1]
            #}
            updated_videos.append(video)

        print(updated_videos)
        # Update the document with the new video data
        collection.update_one(
            {'_id': document['_id']},
            {'$set': {'videos': updated_videos}}
        )


if __name__ == '__main__':
    perform_sentiment_analysis_and_update()
