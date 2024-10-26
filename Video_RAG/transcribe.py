import whisper

def load_whisper(model_name):
    '''Load the whisper model'''
    model = whisper.load_model(model_name)
    return model

def transcribe_audio(model, audio_file):
    '''Transcribe the audio file'''
    result = model.transcribe(audio_file)
    video_text = result["text"]
    return video_text