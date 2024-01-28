import streamlit
from bs4 import BeautifulSoup
from urllib.request import urlopen
from newspaper import Article
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pprint

nltk.download("punkt")
nltk.download("vader_lexicon")

streamlit.set_page_config(page_title='NEWS SOFTWARE 360', page_icon='./data/icon.png')

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

def categorize_article(article, tags_to_departments):
    article.nlp()
    keywords = article.keywords
    matched_departments = set()

    for keyword in keywords:
        for tag, departments in tags_to_departments.items():
            if keyword.lower() in tag.lower():
                matched_departments.update(departments)

    return list(matched_departments)

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
def categorize_article(article, tags_to_departments):
    article.nlp()
    keywords = article.keywords
    matched_departments = set()

    for keyword in keywords:
        for tag, departments in tags_to_departments.items():
            if keyword.lower() in [tag.lower()] + [dept.lower() for dept in departments]:
                matched_departments.add(tag)

    return list(matched_departments)

# def display_news(ls, an, tags_to_departments):
#     c = 0
#     for news in ls:
#         c += 1
#         streamlit.write('**({}) {}**'.format(c, news.title.text))
#         news_data = Article(news.link.text)
#         try:
#             news_data.download()
#             news_data.parse()
#             news_data.nlp()
#         except Exception as e:
#             print(e)

#         departments = categorize_article(news_data, tags_to_departments)
#         sentiment = perform_sentiment_analysis(news_data.text)

#         with streamlit.expander(news.title.text):
#             streamlit.markdown(
#                 '''<h6 style="text-align: justify;">{}</h6>'''.format(news_data.summary),
#                 unsafe_allow_html=True
#             )
#             streamlit.markdown("[Read more at {}...]({})".format(news.source.text, news.link.text))
#             streamlit.success("Published Date: " + news.pubDate.text)
#             #streamlit.info("Categorized Departments: {}".format(', '.join(departments)))
#             #streamlit.info("Sentiment Analysis: {}".format(sentiment))
#             visualize_sentiment(sentiment)
#         if c >= an:
#             break
def display_keywords(keywords):
    streamlit.info("Keywords: {}".format(', '.join(keywords)))

def display_news(ls, an, tags_to_departments):
    c = 0
    for news in ls:
        c += 1
        streamlit.write('**({}) {}**'.format(c, news.title.text))
        news_data = Article(news.link.text)
        try:
            news_data.download()
            news_data.parse()
            news_data.nlp()
        except Exception as e:
            print(e)

        departments = categorize_article(news_data, tags_to_departments)
        sentiment = perform_sentiment_analysis(news_data.text)

        with streamlit.expander(news.title.text):
            streamlit.markdown(
                '''<h6 style="text-align: justify;">{}</h6>'''.format(news_data.summary),
                unsafe_allow_html=True
            )
            display_keywords(news_data.keywords)  # New line to display keywords
            streamlit.markdown("[Read more at {}...]({})".format(news.source.text, news.link.text))
            streamlit.success("Published Date: " + news.pubDate.text)
            visualize_sentiment(sentiment)
        if c >= an:
            break

def visualize_sentiment(sentiment):
    # Visual representation of sentiment analysis using color-coded indicators
    if "Positive" in sentiment:
        color = "green"
    elif "Negative" in sentiment:
        color = "red"
    else:
        color = "yellow"

    sentiment_display = f"Sentiment Analysis: <font color='{color}'>{sentiment}</font>"
    streamlit.markdown(sentiment_display, unsafe_allow_html=True)

def run():
    streamlit.title("News Software - 360")
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
    category_options = streamlit.selectbox('Select your Category', category)
    
    if category_options == category[0]:
        streamlit.warning('Please select a category to get NEWS')
    elif category_options == category[1]:
        streamlit.subheader(" Here are some Top Trending News ")
        articles_per_page = streamlit.slider("Articles per Page", min_value=5, max_value=25, step=5)
        news_list = fetch_news_general()
        display_news(news_list, articles_per_page, tags_to_departments)
    elif category_options == category[2]:
        topics = ['--Choose Topics--', 'WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH']
        chosen_topic = streamlit.selectbox("Choose the Topic", topics)
        if chosen_topic == topics[0]:
            streamlit.warning("Please choose a topic to view NEWS")
        else:
            articles_per_page = streamlit.slider("Articles per Page", min_value=5, max_value=25, step=5)
            news_list = fetch_news_topic(chosen_topic)
            if news_list:
                streamlit.subheader(f"{chosen_topic} NEWS")
                display_news(news_list, articles_per_page, tags_to_departments)
            else:
                streamlit.error(f"No latest NEWS on {chosen_topic}")
    elif category_options == category[3]:
        user_topic = streamlit.text_input("Enter the topic you want to search NEWS for")
        articles_per_page = streamlit.slider("Articles per Page", min_value=5, max_value=25, step=5)
        if streamlit.button("Search") and user_topic != '':
            user_topic_pr = user_topic.replace(' ', '')
            news_list = fetch_news_topic(topic=user_topic_pr)
            if news_list:
                streamlit.subheader(f"{user_topic.capitalize()} NEWS")
                display_news(news_list, articles_per_page, tags_to_departments)
            else:
                streamlit.error(f"No NEWS for for the topic: {user_topic}")
        else:
            streamlit.warning("Please type the topic name to search NEWS")

if __name__ == "__main__":
    run()


