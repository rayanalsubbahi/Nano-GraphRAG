import asyncio
import streamlit as st
from video_downloader import download_audio
from transcribe import load_whisper, transcribe_audio
from graph_rag import execute_rag_summarization, model_chat
from streamlit_ui import *

from langchain_community.chat_models import ChatOllama
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_openai.chat_models import ChatOpenAI


MODELS = { #model name: requires API key
    'llama3.1': False,
    'llama3.2': False,
    'mistral': False,
    'gemma2': False,
    'qwen2.5': False,
    'claude-3-haiku-20240307': True,
    'claude-3-5-haiku-20241022': True,
    'gpt-4o-mini-2024-07-18': True
}

def setup_llm(model, api_key=None):
    try:
        if 'claude' in model:
            llm = ChatAnthropic(model=model, anthropic_api_key=api_key, max_tokens_to_sample=4096, temperature=0.2)
        elif 'gpt' in model:
            llm = ChatOpenAI(model=model, openai_api_key=api_key)
        else:
            llm = ChatOllama(model=model)
        return llm
    
    except Exception as e:
        if api_key:
            st.error(f"Error setting up the model: {e}")
        return None

def process_video(llm, video_url):
    # Download the audio 
    if not st.session_state.get("audio_file"):
        with st.spinner('Downloading Audio ...'):
            audio_file = download_audio(video_url)
            print(f"Audio file: {audio_file}")
            st.session_state["audio_file"] = audio_file

    # Transcribe the audio
    if not st.session_state.get("video_text"):
        with st.spinner('Processing Video ...'):
            whisper_model = load_whisper('turbo')
            video_text = transcribe_audio(whisper_model, audio_file)
            st.session_state["video_text"] = video_text
        
    # Execute GraphRAG
    if not st.session_state.get("graph") and llm:
        with st.spinner('Summarizing video...'):
            summary, graph = asyncio.run(execute_rag_summarization(llm, video_text))

        st.session_state["graph"] = graph
        st.session_state["summary"] = summary
    return  

def process_query(llm, graph, query):
    response = asyncio.run(model_chat(llm, graph, query=query))
    st.session_state["history"].append({"role": "assistant", "content": response})
    return response


def main():
    st.set_page_config(page_title="VideoRAG", page_icon="🎥", layout="wide")
    set_custom_style()
    display_header()
    
    model = display_sidebar(MODELS)
    if model:
        llm = setup_llm(model, st.session_state["api_key"])

    # Main content area
    video_url = display_video_section(api_key_required=MODELS.get(model, True))
    
    if st.session_state.get("video_url"):
        process_video(llm, video_url)
        summary = st.session_state.get("summary")
        if summary:
            display_summary(summary)
            display_chat_interface()
                
            query = take_user_query()
            if query:
                with st.spinner('Thinking ...'):
                    response = process_query(llm, st.session_state["graph"], query)
                display_response(response)
    return
    

# main function
if __name__ == '__main__':
    main()