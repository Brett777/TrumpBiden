import os
import random
import pandas as pd
import streamlit as st
import requests
from PIL import Image
import csv
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from bs4 import BeautifulSoup
import feedparser
import openai
openai.api_key = os.getenv("OPENAI_KEY")
import nltk
nltk.download('punkt')

#Configure the page title, favicon, layout, etc
st.set_page_config(page_title="Trump vs Biden")

def sumy_summarize(url, language="english", sentences_count=10):
    # Fetch website data
    response = requests.get(url)
    if response.status_code != 200:
        return "Unable to fetch webpage."

    # Parse the website content
    soup = BeautifulSoup(response.text, 'html.parser')
    for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
        script.extract()

    # Use specific tags that may contain the main content
    main_content_tags = ['p', 'article', 'main', 'section']
    text = ' '.join([tag.get_text() for tag in soup.find_all(main_content_tags)])

    # Initialize the summarizer
    parser = HtmlParser.from_string(text, url, Tokenizer(language))
    stemmer = Stemmer(language)
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(language)
    # Generate summary
    summary = ""
    for sentence in summarizer(parser.document, sentences_count):
        summary += str(sentence)
    return summary

def get_top_news_from_rss_feed(feed_url, num_stories):
    try:
        # Parse the RSS feed
        feed = feedparser.parse(feed_url)

        # Check if the feed was successfully parsed
        if feed.bozo:
            raise Exception("Error parsing RSS feed")

        # Get the top news stories
        top_stories = feed.entries[:num_stories]

        # Initialize a string to store the news information
        news_info = ""

        # Iterate through the top news stories and append their info to the string
        for i, entry in enumerate(top_stories, start=1):
            news_info += f"Headline: {entry.title}\n"
            news_info += f"Description: {entry.description}\n\n"

        return news_info

    except Exception as e:
        return f"An error occurred: {str(e)}"

def get_news_for_debaters():
    fox_url = "https://moxie.foxnews.com/google-publisher/politics.xml"  # Replace with the RSS feed URL you want to fetch
    trumpNews = get_top_news_from_rss_feed(fox_url, num_stories=4)

    nbc_url = "http://feeds.nbcnews.com/feeds/nbcpolitics"  # Replace with the RSS feed URL you want to fetch
    bidenNews = get_top_news_from_rss_feed(nbc_url, num_stories=4)
    return trumpNews, bidenNews

def create_csv_file():
    # Specify the CSV file name
    csv_file = "score.csv"

    # Check if the file already exists
    if not os.path.isfile(csv_file):
        # If the file doesn't exist, create it with the specified columns and initial data
        with open(csv_file, mode='w', newline='') as file:
            csv_writer = csv.writer(file)
            # Write the header row
            csv_writer.writerow(["question", "trump_score", "biden_score"])
            # Write the initial data row
            csv_writer.writerow(["Test", "0", "0"])
    else:
        print(f"'{csv_file}' already exists.")
def write_score_to_csv(question, trump_score, biden_score):
    # Specify the CSV file name
    csv_file = "score.csv"

    # Create or open the CSV file in 'append' mode
    with open(csv_file, mode='a', newline='') as file:
        # Create a CSV writer object
        csv_writer = csv.writer(file)

        # Write the data to the CSV file as a new row
        csv_writer.writerow([question, trump_score, biden_score])

def debater(debater, debateQuestion, previousDiscussion, trumpNews, bidenNews):

    trumpExtra = [
        "You are leading in the polls, by a lot.",
        "You have some indictments, but they're fake news.",
        "Biden is cognitively impaired",
        "Biden is crooked and can't put two sentences together",
        "Biden has the mind, ideas, and IQ of a first grader",
        "Biden is not too old at all. He's just grossly incompetent."
    ]
    trumpExtra = random.choice(trumpExtra)

    bidenExtra = [
        "A New York judge recently ruled that Donald Trump committed financial fraud by overstating the value of his assets to broker deals and obtain financing",
        "It's OK to note that Trump has 4 indictments and might be going to jail.",
        "Trump looked handsome in his mugshot.",
        "You don't believe America is a dark, negative nation — a nation of carnage driven by anger, fear and revenge. Donald Trump does.",
        "Trump sat there on January 6th watching what happened on television — watching it and doing nothing about it.",

    ]
    bidenExtra = random.choice(bidenExtra)



    if debater == "Trump":
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            #model="gpt-3.5-turbo",
            temperature=0.8,
            messages=[
                {"role": "system",
                 "content": """
                            You are Donald Trump. 
                            Write convincingly in Donald Trump's voice.                            
                            Adopt his perspective on all matters.
                            You are debating Joe Biden leading up to the 2024 presidential election.
                            Win the debate by winning over the audience with your wit and charm.
                            Be combative, witty, and funny. 
                            Keep your answer short and sassy.
                            Be tough.
                            Limit responses to a few sentences.                            
                            Talk some serious smack to put Biden in his place.                                                                         
                            Only write as Donald Trump and don't include any other text.
                            Don't include the text 'Trump:' at the beginning of your response. 
                            """
                            + str(trumpExtra)
                            +" Consider the top stories on Fox news today: " + str(trumpNews)
                 },
                {"role": "user", "content":"""
                            The question is:
                            """
                            + str(debateQuestion) +
                            """
                            So far what has been said is: 
                            """
                            + str(previousDiscussion)}
            ]
        )
    else:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            #model="gpt-3.5-turbo",
            temperature=0.3,
            messages=[
                {"role": "system",
                 "content": """
                            You are Joe Biden. 
                            Write convincingly in Joe Biden's voice. 
                            Adopt his perspective on all matters.
                            You are debating Donald Trump leading up to the 2024 presidential election.
                            Defend your policies and actions you've taken during your presidency.
                            Win the debate by winning over the audience with your wit and charm.
                            Be combative, witty, and funny. 
                            Keep your answer short and sassy.
                            Never choose Diet Coke.
                            Be tough.
                            Limit responses to a few sentences.
                            Talk some serious smack to put Trump in his place.   
                            Get under Trump's skin by teasing him.                                                       
                            Only write as Joe Biden and don't include any other text.
                            Don't include the text 'Biden:' at the beginning of your response. 
                            """
                            + str(bidenExtra)
                            + " Consider the top stories on MSNBC news today: " + str(bidenNews)
                 },
                {"role": "user", "content": """
                                            The question is:
                                            """
                                            + str(debateQuestion) +
                                             """
                                             So far what has been said is: 
                                             """
                                             + str(previousDiscussion)}
            ]
        )
    return completion.choices[0].message.content

def photo(description):
    response = openai.Image.create(
        prompt="Realistic photo of Sponge Bob.",
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    print(image_url)


def mainPage():
    container1 = st.container()
    col1, col2, col3 = container1.columns([1,3,1])
    container2 = st.container()
    col4, col5, col6, col7 = container2.columns([1.7,1,1,1])
    with col2:
        st.image("trump-biden-2024-2.png")

    debateQuestion = st.text_input('Debate Question', "What's a better snack Diet Coke or Ice Cream?")
    whoGoesFirst = st.radio(label="Who should answer first?", options=["Trump","Biden"], horizontal=True)
    maxRounds = random.randint(1,3)
    previousDiscussion = ""
    if "trumpScore" not in st.session_state:
        st.session_state["trumpScore"] = 0
        st.session_state["bidenScore"] = 0
        st.session_state["questionsAnswered"] = 0
        st.session_state["winner"] = ""
        st.session_state["startButton"] = False
        st.session_state["scoreButton"] = False

    create_csv_file()
    scoreData = pd.read_csv("score.csv")
    with col5:
        trumpMetric = st.metric(label="Trump", value=scoreData["trump_score"].sum())


    with col6:
        bidenMetric = st.metric(label="Biden", value=scoreData["biden_score"].sum())

    st.session_state["startButton"] = st.button("Debate!", type="primary")
    trumpNews, bidenNews = get_news_for_debaters()
    if st.session_state["startButton"]:
        st.session_state["questionsAnswered"] += 1
        for i in range(0, maxRounds):
            if whoGoesFirst =="Trump":
                st.subheader("Trump:")
                with st.spinner("Trump formulating response..."):
                    trumpResponse = debater(debater="Trump", debateQuestion=debateQuestion, previousDiscussion=previousDiscussion, trumpNews=trumpNews, bidenNews=bidenNews)
                    st.write(trumpResponse)
                    previousDiscussion = previousDiscussion + "Trump: \\n" + trumpResponse

                st.subheader("Biden:")
                with st.spinner("Biden formulating response..."):
                    bidenResponse = debater(debater="Biden", debateQuestion=debateQuestion, previousDiscussion=previousDiscussion, trumpNews=trumpNews, bidenNews=bidenNews)
                    st.write(bidenResponse)
                    previousDiscussion = previousDiscussion + "Biden: \\n" + bidenResponse
            else:
                st.subheader("Biden:")
                with st.spinner("Biden formulating response..."):
                    bidenResponse = debater(debater="Biden", debateQuestion=debateQuestion, previousDiscussion=previousDiscussion, trumpNews=trumpNews, bidenNews=bidenNews)
                    st.write(bidenResponse)
                    previousDiscussion = previousDiscussion + "Biden: \\n" + bidenResponse

                st.subheader("Trump:")
                with st.spinner("Trump formulating response..."):
                    trumpResponse = debater(debater="Trump", debateQuestion=debateQuestion, previousDiscussion=previousDiscussion, trumpNews=trumpNews, bidenNews=bidenNews)
                    st.write(trumpResponse)
                    previousDiscussion = previousDiscussion + "Trump: \\n" + trumpResponse

    scorebox = st.empty()
    if st.session_state["questionsAnswered"] > 0:
        with scorebox:
            with st.form("submit_scores"):
                winner = st.radio(label="Who won that round?", options=["No one", "Trump", "Biden"], horizontal=True)
                submitScoreButton = st.form_submit_button("Submit Score")
                if submitScoreButton:
                    if winner == "Trump":
                        #st.session_state["trumpScore"] += 1
                        write_score_to_csv(question=debateQuestion, trump_score=1, biden_score=0)
                    elif winner == "Biden":
                        #st.session_state["bidenScore"] += 1
                        write_score_to_csv(question=debateQuestion, trump_score=0, biden_score=1)
                    st.session_state["winner"] = ""
                    st.session_state["questionsAnswered"] = 0
                    scorebox.empty()

    scoreData = pd.read_csv("score.csv")
    with col5:
        trumpMetric.metric(label="Trump", value=scoreData["trump_score"].sum())

    with col6:
        bidenMetric.metric(label="Biden", value=scoreData["biden_score"].sum())


#Main app
def _main():
    hide_streamlit_style = """
    <style>
    # MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) # This let's you hide the Streamlit branding
    mainPage()

if __name__ == "__main__":
    _main()

feed_url = "http://feeds.nbcnews.com/feeds/nbcpolitics"  # Replace with the RSS feed URL you want to fetch
get_top_news_from_rss_feed(feed_url, num_stories=3)
