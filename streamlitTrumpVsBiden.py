import random

import streamlit as st
import requests
from PIL import Image
import openai
openai.api_key = "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"

#Configure the page title, favicon, layout, etc
st.set_page_config(page_title="Trump vs Biden")

def debater(debater, debateQuestion, previousDiscussion):
    if debater == "Trump":
        completion = openai.ChatCompletion.create(
            #model="gpt-4",
            model="gpt-3.5-turbo",
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
                            Be tough.
                            Limit responses to a few sentences.
                            Talk some serious smack to put Biden in his place.                            
                            Only write as Donald Trump and don't include any other text.
                            """},
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
            #model="gpt-4",
            model="gpt-3.5-turbo",
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
                            Be tough.
                            Limit responses to a few sentences.
                            Talk some serious smack to put Trump in his place.   
                            Get under Trump's skin by teasing him.
                            It's OK to note that Trump has 4 indictments and might be going to jail. 
                            Only write as Joe Biden and don't include any other text.
                            """},
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

#This is a multipage app. Pages are defined as functions, but you can also setup pages as separate .py files.
def introPage():
    st.title("This is my first app!")
    st.subheader("Choose a page from the sidebar.")
    logo = Image.open(
        requests.get('https://whataftercollege.com/wp-content/uploads/2020/05/cartoon-machine-learning-class.jpg',
                     stream=True).raw)
    st.image(logo, width=600, caption="https://whataftercollege.com/machine-learning/is-machine-learning-fun/")


#Second page
def page2():
    container1 = st.container()
    col1, col2, col3 = container1.columns([1,3,1])
    container2 = st.container()
    col4, col5, col6, col7 = container2.columns([1.7,1,1,1])
    with col2:
        st.image("trump-biden-2024-2.png")

    debateQuestion = st.text_input('Debate Question', 'How will your policies help the middle class?')
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

    with col5:
        trumpMetric = st.metric(label="Trump", value=st.session_state["trumpScore"])


    with col6:
        bidenMetric = st.metric(label="Biden", value=st.session_state["bidenScore"])

    st.session_state["startButton"] = st.button("Debate!", type="primary")
    if st.session_state["startButton"]:
        st.session_state["questionsAnswered"] += 1
        for i in range(0, maxRounds):
            if whoGoesFirst =="Trump":
                st.subheader("Trump:")
                with st.spinner("Trump formulating response..."):
                    trumpResponse = debater(debater="Trump", debateQuestion=debateQuestion, previousDiscussion=previousDiscussion)
                    st.write(trumpResponse)
                    previousDiscussion = previousDiscussion + "Trump: \\n" + trumpResponse

                st.subheader("Biden:")
                with st.spinner("Biden formulating response..."):
                    bidenResponse = debater(debater="Biden", debateQuestion=debateQuestion, previousDiscussion=previousDiscussion)
                    st.write(bidenResponse)
                    previousDiscussion = previousDiscussion + "Biden: \\n" + bidenResponse
            else:
                st.subheader("Biden:")
                with st.spinner("Biden formulating response..."):
                    bidenResponse = debater(debater="Biden", debateQuestion=debateQuestion, previousDiscussion=previousDiscussion)
                    st.write(bidenResponse)
                    previousDiscussion = previousDiscussion + "Biden: \\n" + bidenResponse

                st.subheader("Trump:")
                with st.spinner("Trump formulating response..."):
                    trumpResponse = debater(debater="Trump", debateQuestion=debateQuestion, previousDiscussion=previousDiscussion)
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
                        st.session_state["trumpScore"] += 1
                    elif winner == "Biden":
                        st.session_state["bidenScore"] += 1
                    st.session_state["winner"] = ""
                    st.session_state["questionsAnswered"] = 0
                    scorebox.empty()

    with col5:
        trumpMetric.metric(label="Trump", value=st.session_state["trumpScore"])

    with col6:
        bidenMetric.metric(label="Biden", value=st.session_state["bidenScore"])




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

    # Navigation to the different pages in the app
    page_names_to_funcs = {
        #"Welcome": introPage,
        "Debate": page2
    }

    page_name = st.sidebar.selectbox("Choose a Page", page_names_to_funcs.keys())
    page_names_to_funcs[page_name]()

if __name__ == "__main__":
    _main()

