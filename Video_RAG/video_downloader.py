import re
import os
from pytube import cipher, YouTube
from pytube.innertube import _default_clients
from pydub import AudioSegment

from pytubefix import YouTube
from pytubefix.cli import on_progress

_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]


def get_throttling_function_name(js: str) -> str:
    """Extract the name of the function that computes the throttling parameter.

    :param str js:
        The contents of the base.js asset file.
    :rtype: str
    :returns:
        The name of the function used to compute the throttling parameter.
    """
    function_patterns = [
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]
    #logger.debug('Finding throttling function name')
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            #logger.debug("finished regex search, matched: %s", pattern)
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        nfunc=re.escape(function_match.group(1))),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]

    raise RegexMatchError(
        caller="get_throttling_function_name", pattern="multiple"
    )

cipher.get_throttling_function_name = get_throttling_function_name


def download_audio(url, output_path='.'):
    try:
        # Use Pytube
        # # Create a YouTube object 
        # yt = YouTube(url)
        
        # # Get the audio stream
        # audio_stream = yt.streams.filter(only_audio=True).first()
        
        # # Download the audio
        # output_file = audio_stream.download(output_path=output_path)
        
        # # Convert to MP3
        # name, ext = os.path.splitext(output_file)
        # new_file = name + '.mp3'
        # AudioSegment.from_file(output_file).export(new_file, format="mp3")
        
        # # Remove the original file
        # os.remove(output_file)
        
        # Use Pytubefix 
        yt = YouTube(url, on_progress_callback=on_progress)
        print(yt.title)
        
        ys = yt.streams.get_audio_only()
        new_file = ys.download(mp3=True)
        
        print(f"Audio downloaded successfully: {new_file}")
        return new_file
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# # Example usage
# video_url = "https://youtu.be/lH74gNeryhQ?si=B2jVhyzquuwZKnxA"
# download_audio(video_url)