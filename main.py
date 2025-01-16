import os
import time
import shutil
import whisper
import subprocess
from ollama import Client

AI = Client(host='http://127.0.0.1:11434')

def MCQ(q, items, d=None):
    print(q)
    for n, i in enumerate(items):
        if d and len(d) >= (n+1): print(f"{n+1}) {i} ({d[n]})")
        else: print(f"{n+1}) {i}")
    try:
        ans = int(input(": "))
    except:
        print("Invalid Selection!")
        return None
    if ans > (n+1) or ans <= 0:
        print("Invalid Selection!")
        return None
    return items[ans-1]

def tempFilename():
    timestamp = int(time.time())
    return f"temp_audio_{timestamp}.mp3"

def downloadYoutube(url, fn):
    try:
        subprocess.run([
            "yt-dlp", 
            "-x", 
            "--audio-format", "mp3", 
            "--force-overwrites",
            "-o", fn, 
            url
        ])
    except Exception as e:
        print("Error downloading!")
        return
    return True

def validAudio(fn):
    return os.path.isfile(fn) and os.path.splitext(fn)[1].lower() == ".mp3"

def copyFile(filePath, fn):
    if not validAudio(filePath): print("Invalid file path or invalid file type!"); return
    try:
        shutil.copy(filePath, fn)
    except Exception as e:
        print(f"Error copying file!")
    return True

def getTranscription(fn, model_):
    model = whisper.load_model(model_)
    transcript = model.transcribe(fn)
    return transcript["text"]

def feedAI(transcript, model):
    try:
        response = AI.chat(
            model=model,
            messages=[{
                'role': 'user',
                'system':'You are a summarizing assistant responsible for analyzing the content of YouTube videos. The user will feed you transcriptions but you should always refer to the content in your response as "the video". Focus on accurately summarizing the main points and key details of the videos. Do not comment on the style of the video (e.g., whether it is a voiceover or conversational). Do never mention or imply the existence of text, transcription, or any written format. Use phrases like "The video discusses..." or "According to the video...". Strive to be the best summarizer possible, providing clear, and informative summaries that exclusively reference the video content.',
                'content': 'Transcript: ' + transcript
                }],
            )
        return response
    except AI.ResponseError as e:
        print('Error:', e.error)

def main():
    print("\nVASS (Video Ai Summary Something)")
    print("--------------------------------------------------------")
    videoType = MCQ("\nVideo source:", ["Youtube","File"])
    fn = tempFilename()
    if not videoType: return
    if videoType == "Youtube": 
        o = downloadYoutube(input("\nEnter Youtube URL: "), fn)
        if not o: return
    else:
        filePath = input("\nEnter file path: ")
        o = copyFile(filePath, fn)
        if not o: return
    whisperModel = MCQ("\nWhisper models:", ["tiny","base","small","medium","large","turbo"])
    if not whisperModel: return
    transcript = getTranscription(fn, whisperModel)
    os.remove(fn)
    ollamaModel = MCQ("\nAI model:", [m.model for m in AI.list()['models']], [m.details.parameter_size for m in AI.list()['models']])
    if not ollamaModel: return
    summary = feedAI(transcript, ollamaModel)
    if not summary: return
    print("\nSummary:\n" + summary['message']['content'])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        pass