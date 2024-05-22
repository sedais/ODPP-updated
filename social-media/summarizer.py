import pymongo
from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def summarize_to_max_sentences(text, max_sentences=10):
    # Generate the summary
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    print("summary")
    print(summary)
    print("end summary")

    # Post-process to ensure the maximum number of sentences
    summary_text = summary[0]['summary_text']
    sentences = summary_text.split('. ')
    print("sentences")
    print(sentences)

    if len(sentences) > max_sentences:
        summary_text = '. '.join(sentences[:max_sentences]) + '.'
        print("joined")
        print(summary_text)
    return summary_text


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
    summaries = [summarizer(chunk, max_length=200, min_length=50, do_sample=False)[0]['summary_text'] for chunk in
                 chunks]
    return ' '.join(summaries)


article = """
In the iconic 2013 film Her, the protagonist develops an intense relationship — which morphs into a love affair — with a voice-enabled AI system.

The AI in Her is everything that today’s voice-enabled systems are not: emotive, funny, and able to intuit the subtleties of human conversation.

In a major announcement this morning, OpenAI announced the release of a new version of its ChatGPT system that natively integrates speech, transcription, and intelligence into a single model.

It’s powerful, intuitive, and disturbingly human-like. Essentially, OpenAI has built a real-life version of Her.

A Bad Conversationalist
ChatGPT has had voice capabilities for months now. Even today, you can open the ChatGPT app on your phone, press the headphones icon, and converse with the system using your voice.

The problem, though, was that ChatGPT was a terrible conversationalist.

Essentially, ChatGPT’s voice capabilities were a hack created by splicing together three different models.

When you would speak to the system, it would first use a transcription model to turn your voice into text. It would then feed that text into its intelligence model — basically, the same system that underpins GPT-4.

The intelligence system would generate text, which ChatGPT would feed back into a text-to-speech system to create a computerized voice that would respond to you.

This made the system nominally conversational, but actually speaking with it was clunky and awkward.

All the extra steps of sending content between different models meant that the system was laggy. In my own testing, I found it often took 3 to 5 seconds between speaking to the system and getting a response back.

Human conversation relies on subtleties that unfold over milliseconds. A system that takes up to five seconds to respond to speech feels clunky and robotic.

The previous system also lacked many fundamental aspects of human speech.

For example, you couldn’t interrupt it; you had to wait for it to finish speaking before you could respond.

Speaking with it often felt like talking to one of those un-interruptable people who blabbers on about a random topic 
with no awareness of the other people in the room. You often felt like bring up the Oscars’ orchestra in a desperate 
attempt to get the system to stop talking.

It was also constrained by its inability to interpret emotion in voices or to accurately mimic human emotion in its own responses.

Humans are excellent at reading between the lines, partially because we can pick up on subtle emotive cues in the speaker’s voice.

If I ask my friend, “How was your day?” and they respond, “It was fine,” but they insert a subtle pause between “was” and “fine” (or there’s a hint of exasperation in the final word), I’d know that they actually had a challenging day, and I should ask some follow-up questions.

ChatGPT couldn’t do these things, which made speaking to it feel like communicating with some kind of alien intelligence, not a human.

In short, the previous system fell squarely into the uncanny valley. It was good enough at conversing and had a 
convincing enough voice that parts of the conversation could feel human-like.

But the weird pauses, lack of emotive understanding, and lag ultimately shattered the illusion, making it come off as 
more unsettling than useful.

I tried using the previous system with my six-year-old son. He was so creeped out by it that he wouldn’t let me 
switch the audio back on again.

"""

article_second = """
OpenAI’s recent unveiling of GPT-4o has set the stage for a new era in AI language models and how we interact with them.

The most impressive part was the support of live interaction with ChatGPT with conversational interruptions.

Despite some hiccups during the live demo, I cannot feel other than amazed at what the team has accomplished.

Best of all, right after the demo, OpenAI allowed access to the GPT-4o API.

In this article, I will present my independent analysis measuring the classification abilities of GPT-4o vs. GPT 4 vs. Google’s Gemini and Unicorn models using an English dataset I created.

Which of these models are strongest in English understanding?
Official Evaluation
OpenAI’s blog post includes evaluation scores of known datasets, such as MMLU and HumanEval.


OpenAI’s blog post includes evaluation scores of known datasets, such as MMLU.
As we can derive from the graph, GPT-4o’s performance can be classified as state-of-the-art in this space — which sounds very promising considering the new model is cheaper and faster.

However, during the last year, I have seen multiple models that claim to have state-of-the-art language performance across known datasets. In reality, some of these models have been partially trained (or overfit) on these open datasets resulting in unrealistic scores on leadboards.

Therefore, it is important to do independent analyses of the performance of these models using lesser-known datasets — such as the one that I created 😄

My Evaluation Dataset 🔢
As I have explained in previous articles, I have created a topic dataset that we can use to measure classification performance across different LLMs.

The dataset consists of 200 sentences categorized under 50 topics, where some closely relate intending to make classification tasks harder.

I manually created and labeled the entire dataset in English.

I then used GPT4 (gpt-4–0613) to translate the dataset into multiple languages.

However, during this evaluation, we will only evaluate the English version of the dataset — meaning that the results should not be affected by potential biases originating from using the same language model for dataset creation and topic prediction.

Go and check out the dataset for yourself: topic dataset.

Performance Results 📊
I decided to evaluate the following models:

GPT-4o: gpt-4o-2024–05–13
GPT-4: gpt-4–0613
GPT-4-Turbo: gpt-4-turbo-2024–04–09
Gemini 1.5 Pro: gemini-1.5-pro-preview-0409
Gemini 1.0: gemini-1.0-pro-002
Palm 2 Unicorn: text-unicorn@001
The task given to the language models is to match each sentence in the dataset with the correct topic. This allows us to calculate an accuracy score per language and each model's error rate.

Since the models mostly classify correctly, I am plotting the error rate for each model.

Remember that a lower error rate indicates better model performance.


Barplot of the Error Rate for each model
As we can derive from the graph, GPT-4o has the lowest error rate of all the models with only 2 mistakes.

We can also see that GPT-4, Gemini 1.5, and Palm 2 Unicorn only had one more mistake than GPT-4o — showcasing their strong performance. Interestingly, GPT-4 Turbo performs slightly worse than GPT-4–0613, which is counter to what OpenAI writes on their model page.

Lastly, Gemini 1.0 is lagging behind, which should be expected given its price range.

Bonus: I have written another article on this topic that evaluates how GPT-4o and Gemini 1.5 remember their context using the “needle in the haystack” framework. Check it out using the link below!

OpenAI’s GPT-4o vs. Gemini 1.5 ⭐ Context Memory Evaluation
https://medium.com/@lars.chr.wiik/openais-gpt-4o-vs-gemini-1-5-context-memory-evaluation-1f2da3e15526

Conclusion 💡
This analysis using a uniquely crafted English dataset reveals insights into the state-of-the-art capabilities of these advanced language models.

GPT-4o, OpenAI’s latest offering, stands out with the lowest error rate among the tested models, which affirms OpenAI’s claims regarding its performance.

The AI community and users alike must continue performing independent evaluations using diverse datasets, as these help in providing a clearer picture of a model’s practical effectiveness, beyond what is suggested by standardized benchmarks alone.

Note that the dataset is fairly small and results might vary depending on the dataset. The performance was done using the English dataset only, while a multilingual comparison will have to wait for another time.
"""

# summary = summarizer(article, min_length=40, do_sample=False)
summary = summarize_transcript(article_second)
print(summary)

# Summarize to the maximum of given sentences
# summary = summarize_to_max_sentences(article_second, max_sentences=2)
# print(summary)
