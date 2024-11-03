# VideoRAG

**VideoRAG** is an AI-powered tool designed for video summarization and interaction. Using OpenAI's Whisper for transcription, GraphRAG for knowledge graph creation, and Streamlit for a user-friendly interface, VideoRAG enables you to interact with videos dynamically and ask questions about their content.

## Installation

1. Install FFmpeg (required for video and audio processing):

   ```bash
   # For Ubuntu/Debian
   sudo apt update && sudo apt install ffmpeg -y
   
   # For macOS using Homebrew
   brew install ffmpeg
   
   # For Windows using Chocolatey
   choco install ffmpeg
   ```

2. Clone the repository:

   ```bash
   git clone https://github.com/rayanalsubbahi/Nano-GraphRAG.git
   cd Video_RAG
   ```

3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Launch the Streamlit app:

   ```bash
   streamlit run videorag_app.py
   ```
