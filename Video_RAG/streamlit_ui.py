import streamlit as st

def set_custom_style():
    st.markdown("""
        <style>
        .stApp {
            margin: 0 auto;
        }
        .main-header {
            text-align: center;
            padding: 0rem 0;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
        }
        .user-message {
            background-color: #e9ecef;
            margin-left: 2rem;
        }
        .bot-message {
            background-color: #f8f9fa;
            margin-right: 2rem;
        }
        .api-key-container {
            border: 1px solid #ddd;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
            background-color: #f8f9fa;
        }
        .video-container {
            border: 1px solid #ddd;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

def display_header():
    st.markdown("<h1 class='main-header'>🎥 VideoRAG</h1>", unsafe_allow_html=True)
    st.markdown("""
        <p style='text-align: center; color: #666;'>
            An intelligent video summarization and chat interface powered by AI
        </p>
    """, unsafe_allow_html=True)
    
def display_sidebar(models_dict):
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Model selection
        models = list(models_dict.keys())
        model = st.selectbox(
            "Select AI Model",
            models,
            index=0,
            help="Choose the AI model for video analysis"
        )

        requires_api_key = models_dict[model]        
        if requires_api_key:
            # API Key input
            st.markdown("### 🔑 API Configuration")
            api_key = st.text_input(
                "Enter API Key",
                type="password",
                help="Enter your API key for the selected model"
            )
            
            if api_key:
                st.session_state["api_key"] = api_key
        else:
            st.session_state["api_key"] = None
        
        st.markdown("### ℹ️ About")
        st.markdown("""
            VideoRAG uses advanced AI to:
            - 📝 Summarize video content
            - 🎯 Extract key insights  
            - 💬 Enable interactive Q&A
        """)
    
    return model

def display_video(video_url):
    # Create a container for the video with custom width
    with st.container():
        # Center-align the container
        col1, col2 = st.columns([1, 2])
        with col1:
            st.video(video_url)
    
def display_video_section(api_key_required):
    st.markdown("### 🎬 Video Input")
    
    # Create columns for URL input and process button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        video_url = st.text_input(
            "Enter YouTube URL",
            placeholder="https://youtu.be/...",
            help="Paste the URL of the YouTube video you want to analyze"
        )
    
    with col2:
        process_button = st.button("▶️ Process")
        
    if process_button:
        #reset the summary
        st.session_state["summary"] = None
        st.session_state["graph"] = None
        st.session_state["video_text"] = None
        st.session_state["history"] = []
        
    # Keep the video displayed if summary is available
    if not process_button and st.session_state.get("summary"):
        display_video(video_url)

    if video_url and process_button:
        if "youtu" in video_url:
            if api_key_required and not st.session_state.get("api_key"):
                st.error("Please enter your API key in the sidebar first!")
            else:   
                display_video(video_url)
                st.session_state["video_url"] = video_url
                return video_url
        else:
            st.error("Please enter a valid YouTube URL")
                  
def display_summary(summary):
    if summary:
        st.markdown("### 📋 Video Summary")
        with st.expander("View Summary", expanded=True):
            st.chat_message(name="Assistant").write(summary)

def display_chat_interface():
    # Display chat messages
    if "history" not in st.session_state:
        st.session_state["history"] = []
    else:
        for message in st.session_state["history"]:
            role = message["role"]
            content = message["content"]
        
            if role == "user":
                st.chat_message(name="User").write(content)
            elif role == "assistant":
                resp = content.replace('\n', '  \n')
                st.chat_message(name="Assistant").write(resp)   

def take_user_query():
    if st.session_state.get("graph"):
        # Take user query
        message = st.chat_input(placeholder="Message here")
        if message:
            st.session_state["history"].append({"role": "user", "content": message})
            # display the user input
            st.chat_message(name="User").write(message)
            return message

def display_response(response):
    if response:
        # display the response
        st.chat_message(name="Assistant").write(response)
    return