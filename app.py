import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from wordcloud import WordCloud
import json

# Ignore all warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="ODPP",
    page_icon="🚀",
)

st.write("# Welcome to (Open) Digital Product Pass Social Media Analysis Results! 🚀")

with st.expander("ℹ️ - About this app", expanded=True):
    st.write(
        """     
   - This app is an easy-to-use interface built in Streamlit utilized to show EDA and Sentiment Analysis Results developed for analyzing YouTube transcript data.
        """
    )

    st.markdown("")


# Function to connect to the MongoDB
def get_database():
    client = MongoClient("mongodb://localhost:27017/")
    return client['odpp']


# Retrieve data from MongoDB
def load_ifixit_data():
    db = get_database()
    items = db.phones.find()
    data = list(items)
    df = pd.DataFrame(data)
    if '_id' in df.columns:
        df['_id'] = df['_id'].astype(str)
    return df


# Retrieve data from MongoDB
def load_youtube_data():
    db = get_database()
    items = db.youtube.find()
    data = list(items)
    df = pd.DataFrame(data)
    # Convert ObjectId to string
    if '_id' in df.columns:
        df['_id'] = df['_id'].astype(str)
    return df


def load_json(file):
    data = pd.read_json(file)
    return data


# Function to display data
def show_data(data):
    st.subheader("IFixIt")

    st.write("""
    - iFixit is a global community of people helping each other repair devices with a mission to make repair accessible and easy for as many people around the world as possible. Including the approach of “the easier it is to fix something; the more people will do it.“.
    - Aims to decrease electronic waste and the toxic legacy of our digital age.
    - IFixIt shows also an important engagement in the YouTube community with over 989K subscribers.
    """)

    st.subheader("Repairability Scores")
    st.write("""
    Based on if:
    - internal components are easy to open for access 
    - battery can be replaced without any tools
    - removing internal components requires specialty screwdrivers and knowledge of the adhesive removal technique.
    """)

    data = data.replace("N/A", pd.NA).dropna(subset=['repairability_score'])
    data['repairability_score'] = data['repairability_score'].astype(int)
    data['year'] = data['year'].astype(int)

    st.write("### Full Dataset", data)
    st.write("### Repairability Scores Distribution")
    score_count = data['repairability_score'].value_counts()
    st.bar_chart(score_count)

    st.write("### Number of Phones per Year")
    phones_per_year = data['year'].value_counts()
    st.bar_chart(phones_per_year)

    # Average Repairability Score per Year
    st.write("### Average Repairability Score per Year")
    avg_score_per_year = data.groupby('year')['repairability_score'].mean()

    fig, ax = plt.subplots(figsize=(8, 4))
    avg_score_per_year.plot(kind='line', marker='o', ax=ax)
    ax.set_title('Average Repairability Score per Year')
    ax.set_xlabel('Year')
    ax.set_ylabel('Average Repairability Score')
    st.pyplot(fig)

    # Correlation between Year and Repairability Score
    st.write("### Correlation between Year and Repairability Score")
    correlation = data[['year', 'repairability_score']].corr().iloc[0, 1]

    fig, ax = plt.subplots(figsize=(8, 4))
    sns.regplot(x='year', y='repairability_score', data=data, ax=ax)
    ax.set_title(f'Correlation between Year and Repairability Score: {correlation:.2f}')
    ax.set_xlabel('Year')
    ax.set_ylabel('Repairability Score')
    st.pyplot(fig)

    # Word Cloud for Pros and Cons
    st.write("### Word Cloud for Pros and Cons")
    pros_text = ' '.join(data['pros'].dropna().astype(str))
    cons_text = ' '.join(data['cons'].dropna().astype(str))

    pros_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(pros_text)
    cons_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(cons_text)

    fig, ax = plt.subplots(1, 2, figsize=(16, 8))
    ax[0].imshow(pros_wordcloud, interpolation='bilinear')
    ax[0].axis('off')
    ax[0].set_title('Pros Word Cloud')

    ax[1].imshow(cons_wordcloud, interpolation='bilinear')
    ax[1].axis('off')
    ax[1].set_title('Cons Word Cloud')

    st.pyplot(fig)


def show_sentiment_analysis(data):
    st.subheader("Sentiment Analysis Results")
    st.write("""
    The sentiment analysis results for the YouTube video transcripts related to phone repairability are shown below. The analysis includes three sentiment analysis models: VADER, TextBlob, and roBERTa.
    """)

    # Subtitle for the models explanation
    st.header('Sentiment Analysis Models')

    # Explanation of the models
    st.markdown("""
    The sentiment analysis results for the YouTube video transcripts related to phone repairability are shown below. The analysis includes three sentiment analysis models: **VADER**, **TextBlob**, and **RoBERTa**.

    ### VADER
    **VADER** (Valence Aware Dictionary and sEntiment Reasoner) is a lexicon and rule-based sentiment analysis tool specifically attuned to sentiments expressed in social media. It provides a compound score that ranges from -1 (most negative) to +1 (most positive).

    ### TextBlob
    **TextBlob** is a simple library for processing textual data. It provides a polarity score ranging from -1 (most negative) to +1 (most positive) and classifies sentiment into three categories: positive, negative, and neutral.

    ### RoBERTa
    **RoBERTa** (Robustly optimized BERT approach) is a transformer-based model developed by Facebook AI. It improves on BERT by using more data and longer training. Fine-tuned for sentiment analysis, it classifies text into positive, negative, and neutral categories based on the probabilities derived from the model.
    """)

    sentiment_data = []

    for index, row in data.iterrows():
        for video in row['videos']:
            if video['sentiment_vader']['compound']:
                compound_score = video['sentiment_vader']['compound']
                if compound_score >= 0.05:
                    vader_label = "Positive"
                elif compound_score <= -0.05:
                    vader_label = "Negative"
                else:
                    vader_label = "Neutral"

                sentiment_data.append({
                    'phone_name': row['phone_name'],
                    'video_id': video['video_id'],
                    # 'video_title': video['title'],
                    'vader_compound': video['sentiment_vader']['compound'],
                    'vader_label': vader_label,
                    'textblob_label': video['sentiment_textblob'][0],
                    'textblob_polarity': video['sentiment_textblob'][1],
                    'roberta_label': video['sentiment_roberta'][0],
                    'roberta_score': video['sentiment_roberta'][1]
                })

    sentiment_df = pd.DataFrame(sentiment_data)
    st.write("### Sentiment Analysis Data", sentiment_df)

    # Analysis by Phone
    st.header('Sentiment Analysis by Phone')

    # Average sentiment scores per phone
    avg_sentiment_by_phone = sentiment_df.groupby('phone_name')[
        ['vader_compound', 'textblob_polarity', 'roberta_score']].mean().reset_index()

    # st.subheader('Average Sentiment Scores by Phone')
    # st.dataframe(avg_sentiment_by_phone)

    # Sentiment Label Distribution for VADER, TextBlob, and RoBERTa
    st.write("### Sentiment Label Distribution")

    fig, axes = plt.subplots(1, 3, figsize=(20, 5))

    # VADER sentiment label distribution
    sns.countplot(ax=axes[0], x='vader_label', data=sentiment_df, palette="viridis")
    axes[0].set_title('VADER Sentiment Label Distribution')
    axes[0].set_xlabel('VADER Label')
    axes[0].set_ylabel('Count')

    # TextBlob sentiment label distribution
    sns.countplot(ax=axes[1], x='textblob_label', data=sentiment_df, palette="viridis")
    axes[1].set_title('TextBlob Sentiment Label Distribution')
    axes[1].set_xlabel('TextBlob Label')
    axes[1].set_ylabel('Count')

    # RoBERTa sentiment label distribution
    sns.countplot(ax=axes[2], x='roberta_label', data=sentiment_df, palette="viridis")
    axes[2].set_title('RoBERTa Sentiment Label Distribution')
    axes[2].set_xlabel('RoBERTa Label')
    axes[2].set_ylabel('Count')

    st.pyplot(fig)

    # Box plots for sentiment scores
    st.write("### Distribution of Sentiment Scores")

    fig, ax = plt.subplots(1, 3, figsize=(18, 6))

    # VADER compound score
    sns.boxplot(ax=ax[0], y='vader_compound', data=sentiment_df, palette="viridis")
    ax[0].set_title('VADER Compound Score Distribution')

    # TextBlob polarity score
    sns.boxplot(ax=ax[1], y='textblob_polarity', data=sentiment_df, palette="viridis")
    ax[1].set_title('TextBlob Polarity Score Distribution')

    # RoBERTa sentiment score
    sns.boxplot(ax=ax[2], y='roberta_score', data=sentiment_df, palette="viridis")
    ax[2].set_title('RoBERTa Sentiment Score Distribution')

    st.pyplot(fig)

    # Top Videos with Highest Positive Sentiments
    st.write('### Videos with Highest Positive Sentiment')

    # Checkbox to select which analysis to show
    show_vader = st.checkbox('Show Top VADER Videos')
    show_textblob = st.checkbox('Show Top TextBlob Videos')
    show_roberta = st.checkbox('Show Top RoBERTa Videos')

    if show_vader:
        st.subheader('Top 5 Videos by VADER Compound Score')
        top_vader_videos = sentiment_df.nlargest(5, 'vader_compound')[['phone_name', 'video_id', 'vader_compound']]
        st.dataframe(top_vader_videos)

    if show_textblob:
        st.subheader('Top 5 Videos by TextBlob Polarity Score')
        top_textblob_videos = sentiment_df.nlargest(5, 'textblob_polarity')[
            ['phone_name', 'video_id', 'textblob_polarity']]
        st.dataframe(top_textblob_videos)

    if show_roberta:
        st.subheader('Top 5 Videos by RoBERTa Score')
        top_roberta_videos = sentiment_df.nlargest(5, 'roberta_score')[['phone_name', 'video_id', 'roberta_label', 'roberta_score']]
        st.dataframe(top_roberta_videos)

    # Top Videos with Lowest Positive Sentiments
    st.write('### Videos with Highest Negative Sentiment')

    # Checkbox to select which analysis to show
    show_vader = st.checkbox('Show Last VADER Videos')
    show_textblob = st.checkbox('Show Last TextBlob Videos')
    show_roberta = st.checkbox('Show Last RoBERTa Videos')

    if show_vader:
        st.subheader('Lowest 5 Videos by VADER Compound Score')
        top_vader_videos = sentiment_df.nsmallest(5, 'vader_compound')[['phone_name', 'video_id', 'vader_compound']]
        st.dataframe(top_vader_videos)

    if show_textblob:
        st.subheader('Lowest 5 Videos by TextBlob Polarity Score')
        top_textblob_videos = sentiment_df.nsmallest(5, 'textblob_polarity')[
            ['phone_name', 'video_id', 'textblob_polarity']]
        st.dataframe(top_textblob_videos)

    if show_roberta:
        st.subheader('Top 5 Videos by RoBERTa Score')
        top_roberta_videos = sentiment_df.nsmallest(5, 'roberta_score')[['phone_name', 'video_id', 'roberta_label', 'roberta_score']]
        st.dataframe(top_roberta_videos)

    # st.write("### VADER Sentiment Distribution")
    # vader_scores = sentiment_df['vader_compound']
    # st.bar_chart(vader_scores)
    #
    # st.write("### TextBlob Sentiment Distribution")
    # textblob_scores = sentiment_df['textblob_polarity']
    # st.bar_chart(textblob_scores)

    #######################
    # # Additional analysis: videos with highest positive sentiment
    # st.write("### Videos with Highest Positive Sentiment (VADER)")
    # top_positive_videos = sentiment_df.nlargest(5, 'vader_compound')[['phone_name', 'vader_compound']]
    # st.write(top_positive_videos)
    #
    # # Additional analysis: videos with most negative sentiment
    # st.write("### Videos with Most Negative Sentiment (VADER)")
    # top_negative_videos = sentiment_df.nsmallest(5, 'vader_compound')[['phone_name', 'vader_compound']]
    # st.write(top_negative_videos)
    #
    # # Additional analysis: Average sentiment scores for each phone model
    # st.write("### Average Sentiment Scores by Phone Model")
    # average_sentiments = sentiment_df.groupby('phone_name').mean(numeric_only=True)[
    #     ['vader_compound', 'textblob_polarity']]
    # st.write(average_sentiments)
    #
    # # Additional analysis: Median sentiment scores for each phone model
    # st.write("### Median Sentiment Scores by Phone Model")
    # median_sentiments = sentiment_df.groupby('phone_name').median(numeric_only=True)[
    #     ['vader_compound', 'textblob_polarity']]
    # st.write(median_sentiments)
    #
    # # Additional analysis: Standard deviation of sentiment scores for each phone model
    # st.write("### Standard Deviation of Sentiment Scores by Phone Model")
    # std_sentiments = sentiment_df.groupby('phone_name').std(numeric_only=True)[
    #     ['vader_compound', 'textblob_polarity']]
    # st.write(std_sentiments)

    ###########################
    # Calculate the average sentiment scores per phone
    avg_sentiment_by_phone = sentiment_df.groupby('phone_name')[
        ['vader_compound', 'textblob_polarity']].mean().reset_index()

    # Find the top 5 phones with the highest average sentiment scores
    top_5_positive_phones = avg_sentiment_by_phone.nlargest(5, 'vader_compound')

    # Find the bottom 5 phones with the lowest average sentiment scores
    bottom_5_negative_phones = avg_sentiment_by_phone.nsmallest(5, 'vader_compound')

    # Find the top 5 phones with the highest average sentiment scores for TextBlob
    top_5_positive_phones_textblob = avg_sentiment_by_phone.nlargest(5, 'textblob_polarity')

    # Find the bottom 5 phones with the lowest average sentiment scores for TextBlob
    bottom_5_negative_phones_textblob = avg_sentiment_by_phone.nsmallest(5, 'textblob_polarity')

    # # Display the results
    # st.subheader('Top 5 Phones with Highest Average Sentiment Scores (VADER)')
    # st.dataframe(top_5_positive_phones)
    #
    # st.subheader('Bottom 5 Phones with Lowest Average Sentiment Scores (VADER)')
    # st.dataframe(bottom_5_negative_phones)

    # Plotting top 5 positive phones
    st.subheader('Top 5 Phones with Highest Average Sentiment Scores (VADER)')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(y='phone_name', x='vader_compound', data=top_5_positive_phones, palette='viridis', ax=ax)
    ax.set_title('Top 5 Positive Phones (VADER)')
    ax.set_xlabel('Average VADER Compound Score')
    ax.set_ylabel('Phone Name')
    st.pyplot(fig)

    # Plotting bottom 5 negative phones
    st.subheader('Bottom 5 Phones with Lowest Average Sentiment Scores (VADER)')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(y='phone_name', x='vader_compound', data=bottom_5_negative_phones, palette='viridis', ax=ax)
    ax.set_title('Bottom 5 Negative Phones (VADER)')
    ax.set_xlabel('Average VADER Compound Score')
    ax.set_ylabel('Phone Name')
    st.pyplot(fig)

    # Plotting top 5 positive phones for TextBlob
    st.subheader('Top 5 Phones with Highest Average Sentiment Scores (TextBlob)')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(y='phone_name', x='textblob_polarity', data=top_5_positive_phones_textblob, palette='viridis', ax=ax)
    ax.set_title('Top 5 Positive Phones (TextBlob)')
    ax.set_xlabel('Average TextBlob Polarity Score')
    ax.set_ylabel('Phone Name')
    st.pyplot(fig)

    # Plotting bottom 5 negative phones for TextBlob
    st.subheader('Bottom 5 Phones with Lowest Average Sentiment Scores (TextBlob)')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(y='phone_name', x='textblob_polarity', data=bottom_5_negative_phones_textblob, palette='viridis', ax=ax)
    ax.set_title('Bottom 5 Negative Phones (TextBlob)')
    ax.set_xlabel('Average TextBlob Polarity Score')
    ax.set_ylabel('Phone Name')
    st.pyplot(fig)


# Function to show transcript summaries and key sentiments
def show_analysis_by_phone(data):
    st.subheader("Summary and Sentiment Analysis by Phone")

    phone_names = data['phone_name'].unique()
    selected_phone = st.selectbox("Select a Phone", phone_names)

    selected_data = data[data['phone_name'] == selected_phone]

    for index, row in selected_data.iterrows():
        st.write(f"## {row['phone_name']}")

        for video in row['videos']:
            if 'summary' in video and 'sentiment_vader' in video:
                st.write(f"### Title: {video.get('title', 'N/A')}")
                st.write(f"**Video ID:** {video['video_id']}")
                # st.write(f"### Video ID: {video['video_id']}")
                # st.write(f"**Title:** {video.get('title', 'N/A')}")

                show_summary = st.checkbox(f"Show Summary for Video ID: {video['video_id']}", value=False)
                if show_summary:
                    st.write(f"**Summary:** {video['summary']}")

                compound_score = video['sentiment_vader']['compound']
                if compound_score >= 0.05:
                    sentiment_color = "green"
                    sentiment_label = "Positive"
                elif compound_score <= -0.05:
                    sentiment_color = "red"
                    sentiment_label = "Negative"
                else:
                    sentiment_color = "yellow"
                    sentiment_label = "Neutral"

                st.write(f"**VADER Sentiment Score ({sentiment_label}): {compound_score}**")
                st.markdown(f"""
                    <div style="background-color: #e0e0e0; border-radius: 25px; padding: 5px; width: 100%;">
                        <div style="width: {(compound_score + 1) / 2 * 100}%; background-color: {sentiment_color}; height: 20px; border-radius: 25px;"></div>
                    </div>
                """, unsafe_allow_html=True)

                textblob_label = video['sentiment_textblob'][0]
                textblob_score = video['sentiment_textblob'][1]

                st.write(f"**TextBlob Polarity ({textblob_label}): {textblob_score}**")
                if textblob_label == "Positive":
                    textblob_color = "green"
                elif textblob_label == "Negative":
                    textblob_color = "red"
                else:
                    textblob_color = "yellow"

                st.markdown(f"""
                    <div style="background-color: #e0e0e0; border-radius: 25px; padding: 5px; width: 100%;">
                        <div style="width: {(textblob_score + 1) / 2 * 100}%; background-color: {textblob_color}; height: 20px; border-radius: 25px;"></div>
                    </div>
                    """, unsafe_allow_html=True)

                roberta_label = video['sentiment_roberta'][0]
                roberta_score = video['sentiment_roberta'][1]
                if roberta_label == "positive":
                    roberta_color = "green"
                elif roberta_label == "negative":
                    roberta_color = "red"
                else:
                    roberta_color = "yellow"

                st.write(f"**roBERTa Score ({roberta_label}): {roberta_score}**")
                st.markdown(f"""
                    <div style="background-color: #e0e0e0; border-radius: 25px; padding: 5px; width: 100%;">
                        <div style="width: {roberta_score * 100}%; background-color: {roberta_color}; height: 20px; border-radius: 25px;"></div>
                    </div>
                    """, unsafe_allow_html=True)

                # st.write(f"**Keywords:** {', '.join(video['sentiment_vader']['keywords'])}")
                st.write("---")


def main():
    # Create tabs
    tab1, tab2, tab3 = st.tabs(
        ["Exploratory Analysis", "YouTube Sentiment Analysis", "Summary and Sentiment Analysis by Phone"])
    # ifixit_data = load_ifixit_data()
    # youtube_data = load_youtube_data()

    ifixit_data = load_json("data/odpp.phones.json")
    youtube_data = load_json("data/odpp.youtube.json")

    # Exploratory Analysis Tab
    with tab1:
        # st.header("Exploratory Analysis")
        st.write("### Phone Repairability Analytics")
        show_data(ifixit_data)

    # YouTube Sentiment Analysis Tab
    with tab2:
        # st.header("YouTube Sentiment Analysis")
        show_sentiment_analysis(youtube_data)

    # Summary and Sentiment Analysis by Phone
    with tab3:
        st.header("YouTube Sentiment Analysis")
        show_analysis_by_phone(youtube_data)


if __name__ == '__main__':
    main()
