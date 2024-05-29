# ODPP-updated

# Sentiment Analysis of YouTube Video Transcripts on Phone Repairability

This Streamlit app performs sentiment analysis on YouTube video transcripts related to phone repairability. The analysis uses three sentiment analysis models: **VADER**, **TextBlob**, and **RoBERTa**.

## Features

- Upload a JSON file containing the video transcripts.
- Analyze the sentiment of each video transcript.
- Visualize the results using bar plots.

## Models Used

### facebook/bart-large-cnn
**facebook/bart-large-cnn**: This is a pre-trained language model from Facebook, designed to generate concise summaries of longer pieces of text. More information on https://huggingface.co/facebook/bart-large-cnn

### VADER
**VADER** (Valence Aware Dictionary and sEntiment Reasoner) is a lexicon and rule-based sentiment analysis tool specifically attuned to sentiments expressed in social media. It provides a compound score that ranges from -1 (most negative) to +1 (most positive).

### TextBlob
**TextBlob** is a simple library for processing textual data. It provides a polarity score ranging from -1 (most negative) to +1 (most positive) and classifies sentiment into three categories: positive, negative, and neutral.

### RoBERTa
**RoBERTa** (Robustly optimized BERT approach) is a transformer-based model developed by Facebook AI. It improves on BERT by using more data and longer training. Fine-tuned for sentiment analysis, it classifies text into positive, negative, and neutral categories based on the probabilities derived from the model.

## Prerequisites

- Python 3.8 or higher (3.11 preferred)

## How to Use

### GitHub
1. Clone the repository:

    ```bash
    git clone https://github.com/sedais/ODPP-updated.git
    cd ODPP-updated
    ```

2. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    venv\Scripts\activate  # On Mac, use `source venv/bin/activate`
    ```

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```


4. Run the App: To run the Streamlit app, use the following command:

   ```bash
   streamlit run app.py
   ```

### Accessing the App on Streamlit Cloud
The app is also deployed on Streamlit Cloud and can be accessed at the following URL:
https://odpp-sentiment-analysis.streamlit.app/ 
