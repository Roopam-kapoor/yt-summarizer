from langchain_groq import ChatGroq
from dotenv import load_dotenv
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api.proxies import WebshareProxyConfig

load_dotenv()
st.header('🎥 YouTube Video Summarizer')

# User input
url = st.text_input('Enter full YouTube video URL (e.g., https://www.youtube.com/watch?v=xxxx)')

# Submit button
if st.button('Submit'):

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

    video_id = extract_video_id(url)

    if not video_id:
        st.error("❌ Invalid YouTube URL.")
    else:
        try:
            # Get and translate transcript
            ytt_api = YouTubeTranscriptApi(
                proxy_config=WebshareProxyConfig(
                proxy_username="nxpgclyy",
                proxy_password="v6vl9y7d2zkl",
                )
            )
            transcript_list = ytt_api.list_transcripts(video_id)
            translated_transcript = transcript_list.find_transcript(['hi']).translate('en')
            transcript = translated_transcript.fetch()

            # Format as plain text
            formatter = TextFormatter()
            text_transcript = formatter.format_transcript(transcript)

            # Display transcript
            st.subheader("📝 Translated Transcript")
            st.text_area("Transcript:", text_transcript, height=250)

            # LangChain prompt
            template = PromptTemplate(
                template='Please write a detailed summary for the following transcript of a YouTube video:\n\n{text}',
                input_variables=['text']
            )
            parser = StrOutputParser()
            model = ChatGroq(model='llama-3.3-70b-versatile')

            chain = template | model | parser
            result = chain.invoke({'text': text_transcript})

            # Display summary
            st.subheader("🧠 Summary")
            st.write(result)

        except Exception as e:
            st.error(f"⚠️ Error: {e}")
