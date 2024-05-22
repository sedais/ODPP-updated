import streamlit as st
from pymongo import MongoClient
import pandas as pd

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


# Function to connect to the MongoDB
def get_database():
    client = MongoClient("mongodb://localhost:27017/")
    return client['dpp']


# Retrieve data from MongoDB
def load_data():
    db = get_database()
    items = db.youtube.find()
    data = list(items)

    # Convert ObjectId to string
    for item in data:
        item['_id'] = str(item['_id'])

    return pd.DataFrame(data)


# Function to display data
def show_data(data):
    st.write("### Full Dataset", data)

    st.write("### Repairability Scores Distribution")
    score_count = data['repairability_score'].value_counts()
    st.bar_chart(score_count)

    st.write("### Number of Phones per Year")
    phones_per_year = data['year'].value_counts()
    st.bar_chart(phones_per_year)


def show_sentiment_analysis(data):
    st.subheader("Sentiment Analysis Results")
    st.write("""
    The sentiment analysis results for the YouTube video transcripts related to phone repairability are shown below. The analysis includes three sentiment analysis models: VADER, TextBlob, and BERT.
    """)

    sentiment_data = []
    for index, row in data.iterrows():
        for video in row['videos']:
            if video[
                'transcript'] != 'No transcript available' and 'sentiment_vader' in video:  # Ensure transcript is available and sentiment analysis has been done
                sentiment_data.append({
                    'phone_name': row['phone_name'],
                    'video_id': video['video_id'],
                    # 'video_title': video['title'],
                    'vader_compound': video['sentiment_vader']['compound'],
                    'textblob_polarity': video['sentiment_textblob'],
                    # 'bert_label': video['sentiment_bert']['label'],
                    # 'bert_score': video['sentiment_bert']['score']
                })

    sentiment_df = pd.DataFrame(sentiment_data)
    st.write("### Sentiment Analysis Data", sentiment_df)

    st.write("### VADER Sentiment Distribution")
    vader_scores = sentiment_df['vader_compound']
    st.bar_chart(vader_scores)

    st.write("### TextBlob Sentiment Distribution")
    textblob_scores = sentiment_df['textblob_polarity']
    st.bar_chart(textblob_scores)

    # Additional analysis: videos with highest positive sentiment
    st.write("### Videos with Highest Positive Sentiment (VADER)")
    top_positive_videos = sentiment_df.nlargest(5, 'vader_compound')[['phone_name', 'vader_compound']]
    st.write(top_positive_videos)

    # Additional analysis: videos with most negative sentiment
    st.write("### Videos with Most Negative Sentiment (VADER)")
    top_negative_videos = sentiment_df.nsmallest(5, 'vader_compound')[['phone_name', 'vader_compound']]
    st.write(top_negative_videos)

    # Additional analysis: Average sentiment scores for each phone model
    st.write("### Average Sentiment Scores by Phone Model")
    average_sentiments = sentiment_df.groupby('phone_name').mean(numeric_only=True)[
        ['vader_compound', 'textblob_polarity']]
    st.write(average_sentiments)

    # Additional analysis: Median sentiment scores for each phone model
    st.write("### Median Sentiment Scores by Phone Model")
    median_sentiments = sentiment_df.groupby('phone_name').median(numeric_only=True)[
        ['vader_compound', 'textblob_polarity']]
    st.write(median_sentiments)

    # Additional analysis: Standard deviation of sentiment scores for each phone model
    st.write("### Standard Deviation of Sentiment Scores by Phone Model")
    std_sentiments = sentiment_df.groupby('phone_name').std(numeric_only=True)[
        ['vader_compound', 'textblob_polarity']]
    st.write(std_sentiments)


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
                st.write(f"### Video ID: {video['video_id']}")
                st.write(f"**Title:** {video.get('title', 'N/A')}")

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

                st.write(f"**VADER Sentiment Score ({sentiment_label}):**")
                st.markdown(f"""
                    <div style="background-color: #e0e0e0; border-radius: 25px; padding: 5px; width: 100%;">
                        <div style="width: {(compound_score + 1) / 2 * 100}%; background-color: {sentiment_color}; height: 20px; border-radius: 25px;"></div>
                    </div>
                """, unsafe_allow_html=True)

                st.write("**TextBlob Polarity:**")
                textblob_score = video['sentiment_textblob']
                if textblob_score >= 0.05:
                    textblob_color = "green"
                elif textblob_score <= -0.05:
                    textblob_color = "red"
                else:
                    textblob_color = "yellow"
                st.markdown(f"""
                    <div style="background-color: #e0e0e0; border-radius: 25px; padding: 5px; width: 100%;">
                        <div style="width: {(textblob_score + 1) / 2 * 100}%; background-color: {textblob_color}; height: 20px; border-radius: 25px;"></div>
                    </div>
                """, unsafe_allow_html=True)

                # st.write(f"**Keywords:** {', '.join(video['sentiment_vader']['keywords'])}")
                st.write("---")

# Streamlit layout
def load_ifixit_data():
    db = get_database()
    items = db.phones.find()
    data = list(items)
    return pd.DataFrame(data)


def main():
    # Create tabs
    tab1, tab2, tab3 = st.tabs(
        ["Exploratory Analysis", "YouTube Sentiment Analysis", "Summary and Sentiment Analysis by Phone"])

    data = load_data()
    ifixit_data = load_ifixit_data()

    # Exploratory Analysis Tab
    with tab1:
        # st.header("Exploratory Analysis")
        st.write("### Phone Repairability Analytics")
        show_data(ifixit_data)

    # YouTube Sentiment Analysis Tab
    with tab2:
        st.header("YouTube Sentiment Analysis")
        show_sentiment_analysis(data)

    # Summary and Sentiment Analysis by Phone
    with tab3:
        st.header("YouTube Sentiment Analysis")
        show_analysis_by_phone(data)


if __name__ == '__main__':
    main()
