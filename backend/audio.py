import os
import subprocess
import base64
import json
from dotenv import load_dotenv
from chat import query_database
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

eleven_labs_api_key = os.getenv("ELEVEN_LABS_API_KEY")

def exec_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode()
    except subprocess.CalledProcessError as e:
        return e.stderr.decode()

def lip_sync_message(message):
    print(f"Starting conversion for message {message}")
    
    subprocess.run(f"ffmpeg -y -i audios/message_{message}.mp3 audios/message_{message}.wav", shell=True, check=True)
    
    subprocess.run(f"./Rhubarb-Lip-Sync-1.13.0-Linux/rhubarb -f json -o audios/message_{message}.json audios/message_{message}.wav -r phonetic", shell=True, check=True)

def audio_file_to_base64(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

def read_json_transcript(file):
    with open(file, "r") as f:
        return json.load(f)

def get_audio(query):
    user_message = query

    message = query_database(user_message)

    file_name = "./audios/message_0.mp3"

    myobj = gTTS(text=message, lang='en', slow=False)
    myobj.save(file_name)

    lip_sync_message(0)
    audio_base64 = audio_file_to_base64(file_name)
    lipsync_data = read_json_transcript(f"audios/message_0.json")
    
    messages = {
        "text": message,
        "audio": audio_file_to_base64("audios/message_0.wav"),
        "lipsync": lipsync_data,
        "facialExpression": "neutral",
        "animation": "Talking"
    }

    return messages

def main(query):
    response = get_audio(query)
    print(json.dumps(response, indent=2))

if __name__ == "__main__":
    main("Whats your name")
