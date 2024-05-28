import re, logging

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
# from youtube_transcript_api._errors import TranscriptsDisabled
from pymongo import MongoClient

# API_KEY = "<API_KEY>"
API_KEY = "<API_KEY>"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_database():
    # Connect to your MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    return client['odpp']  # Return the relevant database


def is_too_short(transcript_text, min_length=30):
    words = transcript_text.split()
    return len(words) < min_length


def query_by_phone(phone_name):
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    search_query = phone_name + " repair"

    # Define repairability keywords
    repair_keywords = ["repair", "restore", "restoration", "fix", "disassemble", "replace", "teardown", "troubleshoot",
                       "service", "replacement"]

    # Search for videos by phone name
    search_response = youtube.search().list(
        q=search_query,
        part='id,snippet',
        type='video',
        maxResults=20  # Increase maxResults to get more videos in one call
    ).execute()

    videos = []

    for item in search_response.get('items', []):
        if len(videos) >= 5:
            break

        video_id = item['id']['videoId']
        video_title = item['snippet']['title']
        logging.info(f"Checking video: {video_title}")

        # Check if the title contains any of the repairability keywords and the phone name
        phone_name_lower = phone_name.lower()
        video_title_lower = video_title.lower()

        # Check if the title contains the phone name and at least one of the repairability keywords
        # and does not include "ASMR"
        if ("asmr" in video_title_lower or
                phone_name_lower not in video_title_lower or
                not any(keyword in video_title_lower for keyword in repair_keywords)):
            logging.info(f"Skipping video: {video_title}")
            continue

        try:
            # Fetch transcript for the video
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])

            # Joining transcript into a single string for simplicity
            transcript_text = ' '.join(
                [entry['text'] for entry in transcript if not re.search(r'\[.*?\]', entry['text'].lower())])

            # Skip if transcript is empty after filtering
            if not transcript_text.strip() or is_too_short(transcript_text):
                logging.info(f"Skipping video due to short or empty transcript: {video_title}")
                continue

            logging.info(f"Extracting required information from video: {video_title}")

            video_data = {
                'video_id': video_id,
                'title': item['snippet']['title'],
                'transcript': transcript_text,
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'channel_title': item['snippet']['channelTitle']
            }
            videos.append(video_data)

        except TranscriptsDisabled:
            logging.warning(f"Transcripts are disabled for video: {video_id}")
        except Exception as e:
            logging.error(f"Failed to fetch transcript for video {video_id}: {str(e)}")

    return videos


def process_all_phones(db):
    phones = db.phones.find()
    for phone in phones:
        phone_name = phone.get('name')  # Adjust the key based on your schema
        if phone_name:
            logging.info(f"Processing phone: {phone_name}")
            videos = query_by_phone(phone_name)
            if videos:
                db.youtube.insert_one({"phone_name": phone_name, "videos": videos})
            logging.info(f"Processed videos for {phone_name}")


def main():
    db = get_database()
    process_all_phones(db)


if __name__ == '__main__':
    main()
