from langchain_groq import ChatGroq
from dotenv import load_dotenv
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from urllib.parse import urlparse, parse_qs
import os

# Load .env variables
load_dotenv()

st.set_page_config(page_title="YouTube Video Summarizer", page_icon="🎥")
st.header('🎥 YouTube Video Summarizer')

# User input
url = st.text_input('Enter full YouTube video URL (e.g., https://www.youtube.com/watch?v=xxxx)')

def extract_video_id(url):
    try:
        query = urlparse(url)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ['www.youtube.com', 'youtube.com']:
            return parse_qs(query.query).get('v', [None])[0]
        return None
    except:
        return None

# Proxy setup
proxies = {
    "http": "http://nxpgclyy:v6vl9y7d2zkl@216.10.27.159:6837",
    "https": "http://nxpgclyy:v6vl9y7d2zkl@216.10.27.159:6837"
}
os.environ['http_proxy'] = proxies['http']
os.environ['https_proxy'] = proxies['https']

if st.button('Submit'):
    video_id = extract_video_id(url)

    if not video_id:
        st.error("❌ Invalid YouTube URL.")
    else:
        try:
            # Get transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

            # Prefer Hindi auto-generated → translated to English
            try:
                translated_transcript = transcript_list.find_transcript(['hi']).translate('en')
            except:
                st.warning("⚠️ Hindi transcript not found. Trying English transcript.")
                translated_transcript = transcript_list.find_transcript(['en'])

            transcript = translated_transcript.fetch()

            # Format to plain text
            formatter = TextFormatter()
            text_transcript = formatter.format_transcript(transcript)

            st.subheader("📝 Transcript")
            st.text_area("Transcript:", text_transcript, height=250)

            # LangChain Prompting
            template = PromptTemplate(
                template='Please write a detailed summary for the following transcript of a YouTube video:\n\n{text}',
                input_variables=['text']
            )
            parser = StrOutputParser()
            model = ChatGroq(model='llama3-8b-8192')  # Adjust to 70b if needed

            chain = template | model | parser
            result = chain.invoke({'text': text_transcript})

            st.subheader("🧠 Summary")
            st.write(result)

        except Exception as e:
            st.error(f"⚠️ Error: {e}")
