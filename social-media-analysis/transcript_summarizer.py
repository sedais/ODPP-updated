import logging
import textwrap

from pymongo import MongoClient
from transformers import pipeline
from transformers import BartForConditionalGeneration, BartTokenizer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_database():
    # Connect to your MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    return client['odpp']  # Return the relevant database


def split_text(text, chunk_size=1024):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        current_length = sum(len(w) + 1 for w in current_chunk)  # Include space
        if current_length + len(word) + 1 <= chunk_size:
            current_chunk.append(word)
        else:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def summarize_chunk(chunk, model, tokenizer):
    inputs = tokenizer.encode(chunk, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(
        inputs,
        max_length=150,
        min_length=5,
        length_penalty=1.5,
        num_beams=4,
        early_stopping=True
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary


def summarize_transcript(text):
    model_name = "facebook/bart-large-cnn"
    model = BartForConditionalGeneration.from_pretrained(model_name)
    tokenizer = BartTokenizer.from_pretrained(model_name)

    # Split the text into manageable chunks
    chunks = split_text(text, chunk_size=1024)
    # Summarize each chunk
    summaries = []
    for chunk in chunks:
        summary = summarize_chunk(chunk, model, tokenizer)
        summaries.append(summary)

    # Combine the summaries into a final summary
    final_summary = ' '.join(summaries)
    formatted_summary = " ".join(textwrap.wrap(final_summary, width=80))
    return formatted_summary


# Function to generate summaries for video transcripts
def generate_summaries(db):
    youtube_collection = db.youtube

    for document in youtube_collection.find():
        phone_name = document.get('phone_name')
        logging.info(f'Processing document for phone: {phone_name}')
        videos = document.get('videos', [])

        for video in videos:
            if 'summary' not in video or not video['summary']:  # Check if summary is missing or empty
                transcript = video.get('transcript')
                if transcript:
                    try:
                        # Generate summary
                        summary = summarize_transcript(transcript)
                        video['summary'] = summary
                        logging.info(f'Updated summary for video: {video.get("title")}')

                        # Update the database for this video
                        youtube_collection.update_one(
                            {'_id': document['_id'], 'videos.video_id': video['video_id']},
                            {'$set': {'videos.$.summary': summary}}
                        )
                        logging.info(f'Successfully updated summary for video {video.get("title")}')
                    except Exception as e:
                        logging.error(f"Error summarizing transcript for video {video['video_id']}: {e}")


def main():
    db = get_database()
    generate_summaries(db)


if __name__ == "__main__":
    main()
