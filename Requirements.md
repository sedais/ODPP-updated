# Project Requirements

This document lists the prerequisites, dependencies, and setup instructions for the project.

## Prerequisites

- **Python Version**: Python 3.8 or higher

## Furniture Database
    
Contains details about different furniture items.

You can create the furniture database by collecting data from various sources or using publicly available datasets. Some potential sources include:
- **Furniture Retail Websites**: Scrape data from websites of furniture retailers.
- **Public Datasets**: Search for publicly available datasets on platforms like Kaggle, Data.gov, or other open data repositories.
- **Manual Entry**: Compile data manually by creating a CSV/JSON file with the required information.


## Querying YouTube for Repair Videos

To query YouTube for repair videos related to furniture items, Google API credentials needs to be set and use the YouTube Data API. 

API used is Youtube data api v3: https://developers.google.com/youtube/v3

### Setting Up Google API
1. **Create a Google API Project**: Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2. **Enable YouTube Data API**: In the API Library, enable the YouTube Data API for your project.
3. **Create API Credentials**: Create an API key under the "Credentials" section.
4. **Store API Key**: Store your API key securely. (It will be used in the example function below as `API_KEY`.)

### Quota and Pricing for YouTube Data API
**Free Quota**: Each project is allocated 10,000 units of quota per day for free. This should be sufficient for the scale of this project.

Below is an example function to query YouTube using the Google API from **social-media-analysis/youtube_api_search.py**: (adjusted)


```python
    def query_by_furniture(furniture_name):
        youtube = build('youtube', 'v3', developerKey=API_KEY)
    
        search_query = furniture_name + " repair"
```

### Data Interaction and Display Explanation
1. **Writing Data to MongoDB:**

The app collects and processes data, such as phone details and YouTube video queries. This data is then stored in collections within a local MongoDB database.

2. **Extracting Collections for Streamlit:**

To display the results in the Streamlit app, the necessary collections are extracted from the MongoDB database in JSON format.

The extracted data in the JSON format is then used within the Streamlit application to generate visualizations and insights.

(This approach ensures the collections are accessed safely without relying on MongoDB Cloud Atlas, where clusters can become inactive after periods of inactivity, which was the case from the initial development)

3. **Writing Data to JSON for Easier Use:**

To make it easier to use and share the data, the app can also adjusted to write the data directly to JSON files. (This can be done by the contributors of the main project)

These JSON files can then be easily loaded into the Streamlit app for further analysis and visualization.

This approach is particularly useful for users who prefer working with file-based data or when sharing data across different environments without requiring a MongoDB setup.

### Further Steps
The rest of the steps will follow similarly to the main project, including:

- **Transcript Extraction:** Extract transcripts from the retrieved YouTube videos.
- **Summary of Transcripts:** Generate summaries of the extracted transcripts.
- **Sentiment Analysis:** Perform sentiment analysis on the summaries or transcripts.
- **Interpretation of Results:** Analyze and interpret the results from the sentiment analysis.


