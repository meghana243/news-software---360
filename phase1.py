import streamlit 
from bs4 import BeautifulSoup
from urllib.request import urlopen
from newspaper import Article
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pprint
import pandas as pd
#6CT9BWHQVNBR3XAFT6CW2B8G
#+17655363728
import streamlit as st
from twilio.rest import Client
#https://www.youtube.com/watch?v=3l0i4BQzz20&pp=ygUEbmV3cw%3D%3D
# Define tags_to_departments dictionary and other necessary functions...
nltk.download("punkt")
nltk.download("vader_lexicon")
def fetch_news(endpoint):
    webpage = urlopen(endpoint)
    content = webpage.read()
    webpage.close()
    scrapped_data = BeautifulSoup(content, 'xml')
    news_list = scrapped_data.find_all('item')
    return news_list

def fetch_news_topic(topic):
    endpoint = 'https://news.google.com/rss/search?q={}'.format(topic)
    return fetch_news(endpoint)

def fetch_news_general():
    endpoint = 'https://news.google.com/rss'
    return fetch_news(endpoint)
# Define function to fetch news from a given endpoint
def fetch_news(endpoint):
    webpage = urlopen(endpoint)
    content = webpage.read()
    webpage.close()
    scrapped_data = BeautifulSoup(content, 'xml')
    return scrapped_data.find_all('item')

# Define function to categorize article based on keywords
def categorize_article(article, tags_to_departments):
    article.nlp()
    keywords = article.keywords
    matched_departments = set()

    for keyword in keywords:
        for tag, departments in tags_to_departments.items():
            if keyword.lower() in [tag.lower()] + [dept.lower() for dept in departments]:
                matched_departments.add(tag)

    return list(matched_departments)

# Define function to perform sentiment analysis
def perform_sentiment_analysis(text):
    sia = SentimentIntensityAnalyzer()
    sentiment_score = sia.polarity_scores(text)

    compound_score = sentiment_score['compound']
    if compound_score >= 0.05:
        return 'Favorable (Positive)'
    elif compound_score > -0.05 and compound_score < 0.05:
        return 'Neutral'
    else:
        return 'Not Favorable (Negative)'

# Define function to display news content
def display_news(ls, an, tags_to_departments):
    c = 0
    for news in ls:
        c += 1
        st.write('**({}) {}**'.format(c, news.title.text))
        news_data = Article(news.link.text)
        try:
            news_data.download()
            news_data.parse()
            news_data.nlp()
        except Exception as e:
            print(e)

        departments = categorize_article(news_data, tags_to_departments)
        sentiment = perform_sentiment_analysis(news_data.text)

        with st.expander(news.title.text):
            # Display news image if available
            if news_data.top_image:
                st.image(news_data.top_image, caption="News Image", use_column_width=True)
            st.markdown(
                '''<h6 style="text-align: justify;">{}</h6>'''.format(news_data.summary),
                unsafe_allow_html=True
            )
            st.markdown("[Read more at {}...]({})".format(news.source.text, news.link.text))
            st.success("Published Date: " + news.pubDate.text)
            visualize_sentiment(sentiment)
            if "Not Favorable (Negative)" in sentiment:
                st.error("This article has negative sentiment.")
                notify_pib_officers(news.title.text, news_data.summary, news.source.text, news.link.text)
        if c >= an:
            break

# Define function to visualize sentiment
def visualize_sentiment(sentiment):
    # Visual representation of sentiment analysis using color-coded indicators
    if "Positive" in sentiment:
        color = "green"
    elif "Negative" in sentiment:
        color = "red"
    else:
        color = "yellow"

    sentiment_display = f"Sentiment Analysis: <font color='{color}'>{sentiment}</font>"
    st.markdown(sentiment_display, unsafe_allow_html=True)


# Define function to notify PIB officers about negative stories
def notify_pib_officers(title, summary, source, link):
    # Write the negative article details to a file
    with open("negative_articles.txt", "a") as file:
        file.write(f"Title: {title}\n")
        file.write(f"Summary: {summary}\n")
        file.write(f"Source: {source}\n")
        file.write(f"Link: {link}\n\n")

    # Send SMS notification
    #send_sms_notification(title, summary, source, link)

# Define function to run the Streamlit application
def run():
    st.title("News Software - 360")
    tags_to_departments = {
        "Home Affairs": ["police", "security", "borders", "immigration"],
        "Education": ["schools", "universities", "teachers"],
        "Health": ["hospitals", "doctors", "medicine"],
        "Defense": ["military", "armed forces", "national security"],
        "Finance": ["economy", "budget", "taxes", "investments"],
        "Foreign Affairs": ["diplomacy", "international relations", "trade"],
        "Justice": ["courts", "law enforcement", "legal system"],
        "Environment": ["climate change", "pollution", "conservation"],
        "Infrastructure": ["roads", "railways", "airports", "energy"],
        "Social Welfare": ["poverty", "education", "healthcare", "housing"],
        "Urban Development": ["cities", "planning", "transportation"],
        "Rural Development": ["agriculture", "villages", "infrastructure"],
        "Agriculture": ["farmers", "crops", "irrigation"]
        # Add more departments and associated tags
    }

    category = ['--Select--', 'Top Trending News', 'News by Topic', 'News by Topic Search']
    category_options = st.selectbox('Select your Category', category)
    
    if category_options == category[0]:
        st.warning('Please select a category to get NEWS')
    elif category_options == category[1]:
        st.subheader(" Here are some Top Trending News ")
        articles_per_page = st.slider("Articles per Page", min_value=5, max_value=25, step=5)
        news_list = fetch_news_general()
        display_news(news_list, articles_per_page, tags_to_departments)
    elif category_options == category[2]:
        topics = ['--Choose Topics--', 'WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH']
        chosen_topic = st.selectbox("Choose the Topic", topics)
        if chosen_topic == topics[0]:
            st.warning("Please choose a topic to view NEWS")
        else:
            articles_per_page = st.slider("Articles per Page", min_value=5, max_value=25, step=5)
            news_list = fetch_news_topic(chosen_topic)
            if news_list:
                st.subheader(f"{chosen_topic} NEWS")
                display_news(news_list, articles_per_page, tags_to_departments)
            else:
                st.error(f"No latest NEWS on {chosen_topic}")
    elif category_options == category[3]:
        user_topic = st.text_input("Enter the topic you want to search NEWS for")
        articles_per_page = st.slider("Articles per Page", min_value=5, max_value=25, step=5)
        if st.button("Search") and user_topic != '':
            user_topic_pr = user_topic.replace(' ', '')
            news_list = fetch_news_topic(topic=user_topic_pr)
            if news_list:
                st.subheader(f"{user_topic.capitalize()} NEWS")
                display_news(news_list, articles_per_page, tags_to_departments)
            else:
                st.error(f"No NEWS for for the topic: {user_topic}")
        else:
            st.warning("Please type the topic name to search NEWS")

# Run the Streamlit application
if __name__ == "__main__":
    run()
import streamlit as st


import streamlit as st
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from google.cloud import speech_v1p1beta1 as speech
from textblob import TextBlob

# YouTube API Key and Service
YOUTUBE_API_KEY = "AIzaSyBf5Qckl5CJNHXxXPLKA_BVSIpPaPlaMKc"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Google Cloud Speech-to-Text API Key and Service
GOOGLE_CLOUD_API_KEY = "AIzaSyAnyhh8AQPjVgIYaQqDMf-mfLg44akBbG8"
GOOGLE_CLOUD_PROJECT_ID = "big-command-407503"
GOOGLE_CLOUD_REGION = "YOUR_REGION"

def get_video_details(video_id):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=YOUTUBE_API_KEY)
    request = youtube.videos().list(part="snippet,contentDetails", id=video_id)
    response = request.execute()
    return response

# Function to get transcript using closed captioning
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = ' '.join([entry['text'] for entry in transcript])
        return text
    except Exception as e:
        st.error(f"Error getting transcript: {str(e)}")
        return None


# # # Function to perform sentiment analysis using TextBlob
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    return sentiment


import io
import pytube
from pytube import YouTube
from google.cloud import speech_v1p1beta1 as speech

# Function to extract audio content from YouTube video
def get_audio_content(video_id):
    try:
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        stream = yt.streams.filter(only_audio=True).first()
        audio_file = stream.download(output_path="./", filename=f"{video_id}_audio")
        with open(audio_file, "rb") as audio_file:
            audio_content = audio_file.read()
        return audio_content
    except Exception as e:
        st.error(f"Error extracting audio content: {str(e)}")
        return None

# Function to transcribe audio to text using Google Cloud Speech-to-Text API
def audio_to_text(audio_content):
    client = speech.SpeechClient(credentials=GOOGLE_CLOUD_API_KEY)
    audio = speech.RecognitionAudio(content=audio_content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    return ' '.join([result.alternatives[0].transcript for result in response.results])

# Streamlit UI
st.title("YouTube Video Transcipt")
video_url = st.text_input("Enter YouTube video URL:")

if st.button("Extract transcript"):
    video_id = video_url.split("v=")[1] if "v=" in video_url else None
    if video_id:
        video_details = get_video_details(video_id)
        if video_details:
            transcript = get_transcript(video_id)
            if transcript:
                st.success("Transcript successfully extracted.")
                st.write(transcript)
                
                sentiment = analyze_sentiment(transcript)
                if sentiment > 0:
                    st.write("Sentiment towards Government of India: Positive")
                elif sentiment < 0:
                    st.write("Sentiment towards Government of India: Negative")
                else:
                    st.write("Sentiment towards Government of India: Neutral")
            else:
                st.info("Closed captioning not available. Trying audio-to-text.")
                audio_content = get_audio_content(video_id)
                if audio_content:
                    transcribed_text = audio_to_text(audio_content)
                    st.write(transcribed_text)
        else:
            st.error("Error fetching video details.")
    else:
        st.error("Invalid YouTube video URL.")

from pytube import YouTube
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi

# Function to fetch and process the transcript from a YouTube video URL
def fetch_transcript(video_url):
    try:
        # Extract video ID from the URL
        video_id = video_url.split("v=")[1] if "v=" in video_url else None
        
        if video_id:
            # Get the transcript using YouTubeTranscriptApi
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            
            # Extract text from each caption entry and concatenate them
            transcript_text = ' '.join([entry['text'] for entry in transcript])
            
            return transcript_text
        else:
            st.error("Invalid YouTube video URL.")
            return None
    except Exception as e:
        st.error(f"Error fetching transcript: {str(e)}")
        return None
# Import necessary libraries
from googletrans import Translator

# Function to translate text
def translate_text(text, target_language):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_language)
    return translated_text.text

# Streamlit UI
st.title("YouTube Video Transcript Translation")
#video_url = st.text_input("Enter YouTube video URL:")
target_language = st.selectbox("Select target language:", ["Select Language", "French", "Spanish", "German", "Italian", "Japanese", "Chinese (Simplified)", "Russian", "Hindi", "Bengali", "Telugu", "Marathi", "Tamil", "Urdu", "Gujarati", "Kannada", "Odia", "Punjabi", "Malayalam"])

if st.button("Translate"):
    if target_language != "Select Language":
        # Fetch and process the transcript
        transcript = fetch_transcript(video_url)
        
        if transcript:
            # Call the translate_text function to translate the transcript
            translated_text = translate_text(transcript, target_language.lower())
            
            # Display the translated text
            st.success("Translation successful.")
            st.write(f"Translated text ({target_language}):")
            st.write(translated_text)
    else:
        st.warning("Please select a target language.")
# Import necessary libraries for sending notifications (e.g., for SMS or Android notifications)
# Example: You can use Twilio for sending SMS notifications
import streamlit as st

# def mod11_app():
#     st.title("Mod11 App")
#     # Your Mod11 app code here

# if __name__ == "__main__":
#     mod11_app()
