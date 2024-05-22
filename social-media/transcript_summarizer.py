import pymongo
from transformers import pipeline
from tqdm import tqdm
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["dpp"]
youtube_collection = db["youtube"]

# Load summarization model
# summarizer = pipeline("summarization")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def split_text(text, max_length=1024):
    """Split the text into chunks of maximum max_length tokens."""
    sentences = text.split('. ')
    chunks = []
    chunk = ""

    for sentence in sentences:
        if len(chunk) + len(sentence) + 1 <= max_length:
            chunk += sentence + '. '
        else:
            chunks.append(chunk.strip())
            chunk = sentence + '. '

    if chunk:
        chunks.append(chunk.strip())

    return chunks


def summarize_transcript(transcript):
    """Summarize the transcript by splitting it into chunks and summarizing each chunk."""
    chunks = split_text(transcript)
    summaries = []
    for chunk in chunks:
        try:
            summary = summarizer(chunk, max_length=max(200, len(chunk)), min_length=50, do_sample=False)[0][
                'summary_text']
            summaries.append(summary)
        except Exception as e:
            logger.error(f"Error summarizing chunk: {e}")
            summaries.append(chunk)  # Fallback to using the original chunk

    return ' '.join(summaries)


# Function to generate summaries for video transcripts
def generate_complete_summaries():
    videos = youtube_collection.find()
    for video in tqdm(videos):
        updated_videos = []
        for vid in video.get('videos', []):
            transcript = vid.get('transcript', 'No transcript available')
            if transcript != 'No transcript available' and 'summary' not in vid:
                try:
                    # Generate summary
                    summary = summarize_transcript(transcript)
                    vid['summary'] = summary
                except Exception as e:
                    logger.error(f"Error summarizing transcript for video {vid['video_id']}: {e}")
                    vid['summary'] = "Summary generation failed."
            updated_videos.append(vid)

        # Update video document with new video data
        # youtube_collection.update_one({'_id': video['_id']}, {'$set': {'videos': updated_videos}})

        # Update video document with new video data
        result = youtube_collection.update_one({'_id': video['_id']}, {'$set': {'videos': updated_videos}})

        # Log success message
        if result.modified_count > 0:
            logger.info(f"Successfully updated video document with _id: {video['_id']}")
        else:
            logger.warning(f"No documents were updated for video with _id: {video['_id']}")


if __name__ == "__main__":
    generate_complete_summaries()
