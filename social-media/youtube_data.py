from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled
from pymongo import MongoClient

api_key = 'AIzaSyCbz3QLXtcftCKtFYnxpeOS6sYbZaUHw0Y'


def get_database():
    # Connect to your MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    return client['dpp']  # Return the relevant database


def get_videos_by_phone_name(api_key, phone_name, db):
    youtube = build('youtube', 'v3', developerKey=api_key)

    search_query = phone_name + " repair"

    # Search for videos by phone name
    search_response = youtube.search().list(
        q=search_query,
        part='id,snippet',
        type='video',
        maxResults=5
    ).execute()

    videos = []

    for item in search_response.get('items', []):
        video_id = item['id']['videoId']
        try:
            # Fetch transcript for the video
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            # Joining transcript into a single string for simplicity
            transcript_text = ' '.join([entry['text'] for entry in transcript])
            video_data = {
                'video_id': video_id,
                'title': item['snippet']['title'],
                'transcript': transcript_text,
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'channel_title': item['snippet']['channelTitle']
                # 'tags': item['snippet'].get('tags', [])
            }
            videos.append(video_data)

            # videos.append({
            #    'video_id': video_id,
            #    'transcript': transcript_text
            # })
        except TranscriptsDisabled:
            print(f"Transcripts are disabled for video: {video_id}")
            videos.append({
                'video_id': video_id,
                'transcript': "No transcript available"
            })
        except Exception as e:
            print(f"Failed to fetch transcript for video {video_id}: {str(e)}")
            videos.append({
                'video_id': video_id,
                'transcript': "Error retrieving transcript"
            })

    # Insert into MongoDB
    # if videos:
    #    db.youtube.insert_one({"phone_name": phone_name, "videos": videos})

    return videos


def process_all_phones(api_key, db):
    phones = db.phones.find()  # Assuming phone names are stored in this collection
    for phone in phones:
        phone_name = phone.get('name')  # Adjust the key based on your schema
        if phone_name:
            print(phone_name)
            videos = get_videos_by_phone_name(api_key, phone_name, db)
            if videos:
                db.youtube.insert_one({"phone_name": phone_name, "videos": videos})
            #    db.youtube.update_one(
            #        {"phone_name": phone_name},
            #        {"$set": {"videos": videos}},
            #        upsert=True
            #    )
            print(f"Processed videos for {phone_name}")


db = get_database()
process_all_phones(api_key, db)

# Replace 'YOUR_API_KEY' with your actual YouTube Data API key

# phone_name = 'iPhone 11'  # Change to the desired phone name to search for
# db = get_database()

# videos = get_videos_by_phone_name(api_key, phone_name, db)
# if videos:
#    db.youtube.insert_one({"phone_name": phone_name, "videos": videos})

# for video in videos:
#    print(video)
