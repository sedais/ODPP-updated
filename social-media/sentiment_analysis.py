import nltk
import torch
import logging

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline, RobertaTokenizer, RobertaForSequenceClassification
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download VADER lexicon
nltk.download('vader_lexicon')

# Initialize sentiment analyzers
vader_analyzer = SentimentIntensityAnalyzer()
bert_analyzer = pipeline('sentiment-analysis')

# Load the tokenizer and model
tokenizer = RobertaTokenizer.from_pretrained('cardiffnlp/twitter-roberta-base-sentiment')
model = RobertaForSequenceClassification.from_pretrained('cardiffnlp/twitter-roberta-base-sentiment')


# Connect to MongoDB
def get_database():
    client = MongoClient("mongodb://localhost:27017/")
    return client['odpp']


def get_sentiment_label_textblob(polarity):
    if polarity < 0:
        return "Negative"
    elif polarity == 0:
        return "Neutral"
    else:
        return "Positive"


# Function to analyze sentiment using VADER
def analyze_sentiment_vader(text):
    return vader_analyzer.polarity_scores(text)


# Function to analyze sentiment using TextBlob
def analyze_sentiment_textblob(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    label = get_sentiment_label_textblob(polarity)
    return label, polarity


# Perform sentiment analysis on transcripts and update MongoDB
def analyze_sentiment_roberta(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.nn.functional.softmax(logits, dim=-1)
    max_prob, sentiment = torch.max(probabilities, dim=-1)

    labels = ['negative', 'neutral', 'positive']
    return labels[sentiment.item()], max_prob.item()


def perform_sentiment_analysis(db):
    youtube_collection = db.youtube

    # Retrieve all documents
    documents = youtube_collection.find()

    for document in documents:
        phone_name = document.get('phone_name')
        logging.info(f'Analyzing sentiments for phone: {phone_name}')

        for video in document['videos']:
            try:
                summary = video['summary']

                vader_result = analyze_sentiment_vader(summary)
                textblob_result = analyze_sentiment_textblob(summary)
                roberta_result = analyze_sentiment_roberta(summary)

                # Log the results
                logger.info(
                    f"Video ID: {video['video_id']} - Vader: {vader_result}, TextBlob: {textblob_result}, RoBERTa: {roberta_result}")

                # Update the video document with the new sentiment data
                update_result = youtube_collection.update_one(
                    {
                        '_id': document['_id'],
                        'videos.video_id': video['video_id']
                    },
                    {
                        '$set': {
                            'videos.$.sentiment_vader': vader_result,
                            'videos.$.sentiment_textblob': textblob_result,
                            'videos.$.sentiment_roberta': roberta_result
                        }
                    }
                )
                # Log the update result
                if update_result.modified_count > 0:
                    logger.info(f"Successfully updated video ID: {video['video_id']}")
                else:
                    logger.warning(f"No update needed for video ID: {video['video_id']}")

            except Exception as e:
                logger.error(f"Error processing video ID: {video['video_id']} - {e}")

        logging.info(f'Analyzed sentiments for phone: {phone_name}')


def main():
    db = get_database()
    perform_sentiment_analysis(db)


if __name__ == '__main__':
    main()