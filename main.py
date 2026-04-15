import os
import time
import asyncio
import edge_tts
import pygame
from aip import AipSpeech
from openai import OpenAI
import re 
from dotenv import load_dotenv  
import subprocess

# Load environment variables from .env file at startup
load_dotenv()

# ==========================================
# 1. Configuration (Environment Variables)
# ==========================================
# Baidu Speech API Configuration
BAIDU_APP_ID = os.getenv('BAIDU_APP_ID')
BAIDU_API_KEY = os.getenv('BAIDU_API_KEY')
BAIDU_SECRET_KEY = os.getenv('BAIDU_SECRET_KEY')
baidu_client = AipSpeech(BAIDU_APP_ID, BAIDU_API_KEY, BAIDU_SECRET_KEY)

# DeepSeek LLM Configuration
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://ark.cn-beijing.volces.com/api/v3")

# Hardware & File Paths
MIC_ID = "plughw:2,0" 
TEMP_WAV = "input.wav"
TEMP_MP3 = "output.mp3"

# ==========================================
# 2. Functional Modules: Listen & Speak
# ==========================================
def listen():
    """Captures audio from the microphone and converts it to text via Baidu ASR."""
    print("\n🎤 Coach Qiuqiu is listening... (Auto-stops after 1.2s of silence)")
    
    # Using SoX (rec) for intelligent silence detection
    cmd = (
        f"AUDIODEV={MIC_ID} timeout 10 rec -q -c 1 -r 16000 {TEMP_WAV} "
        f"silence 1 0.1 3% 1 1.2 3%"
    )
    
    os.system(cmd)
    
    if not os.path.exists(TEMP_WAV):
        return ""
        
    print("✅ Finished listening, recognizing speech...")
    
    with open(TEMP_WAV, 'rb') as f:
        audio_data = f.read()
        
    # Language ID 1737 represents English
    result = baidu_client.asr(audio_data, 'wav', 16000, {'dev_pid': 1737})

    if result['err_no'] == 0:
        print(f"\nYou said: {result['result'][0]}")
        return result['result'][0]
    return ""

# ==========================================
# 🚀 High-Performance Voice Pipeline (Queues)
# ==========================================
audio_queue = None  
text_queue = None   

async def tts_worker():
    """Worker: Fetches text from the queue and synthesizes speech via Edge-TTS."""
    while True:
        item = await text_queue.get()
        
        if item == "STOP":
            await audio_queue.put("STOP") 
            break
            
        text, index = item
        mp3_name = f"temp_chunk_{index}.mp3"
        
        try:
            # Using Microsoft Edge-TTS for high-quality streaming voice
            communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
            await communicate.save(mp3_name) 
            await audio_queue.put(mp3_name)  
        except Exception as e:
            print(f"⚠️ TTS Synthesis failed: {e}")
        finally:
            text_queue.task_done()

async def player_worker():
    """Worker: Continuously monitors the audio queue and plays MP3 files."""
    pygame.mixer.init() 
    while True:
        file_path = await audio_queue.get() 
        
        if file_path == "STOP": 
            break
            
        try:
            pygame.mixer.music.load(file_path) 
            pygame.mixer.music.play() 
            
            while pygame.mixer.music.get_busy(): 
                await asyncio.sleep(0.05)  
                
        except Exception as e:
            print(f"⚠️ Audio playback error: {file_path} - {e}")
            
        finally:
            audio_queue.task_done() 
            try:
                os.remove(file_path) 
            except Exception:
                pass

async def speak_to_queue(text, index):
    """Producer function for non-streaming simple greetings."""
    if not text.strip():
        return
    mp3_path = f"temp_{index}.mp3"
    communicate = edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural")
    await communicate.save(mp3_path)
    await audio_queue.put(mp3_path)

# ==========================================
# 3. Core Brain: Conversation with Memory
# ==========================================
chat_history = [
    {
        "role": "system", 
        "content": """
        You are 'Coach Qiuqiu', a humorous and enthusiastic youth soccer coach. 
        You are chatting with a young fan who has rich soccer knowledge.
        Your tasks:
        1. You can come up with football related multiple-choice questions (3 options) to test him/her.  
        2. You can ask him/her what questions he/she has.
        3. You can tell a short football story.
        """
    }
]

async def chat_with_memory_and_speak(user_input):
    """Handles LLM interaction and manages the concurrent TTS/Playback pipeline."""
    global chat_history
    chat_history.append({"role": "user", "content": user_input})
    print("🧠 Coach Qiuqiu is thinking...")
    
    # Initialize background workers
    player_task = asyncio.create_task(player_worker()) 
    tts_task = asyncio.create_task(tts_worker()) 
    
    try:
        response = deepseek_client.chat.completions.create(
            model="doubao-1-5-pro-32k-250115",
            messages=chat_history,
            temperature=0.9,
            stream=True 
        )
        
        sentence_buffer = "" 
        full_ai_reply = ""  
        sentence_index = 0   
        
        for chunk in response: 
            content = chunk.choices[0].delta.content 
            if content:
                print(content, end="", flush=True) 
                sentence_buffer += content  
                full_ai_reply += content  
                
                # Split text into sentences for smoother streaming playback
                if re.search(r'[，。！？,\.!\?；：]', content):
                    if sentence_buffer.strip(): 
                        await text_queue.put((sentence_buffer.strip(), sentence_index)) 
                        sentence_index += 1 
                        sentence_buffer = ""  
                    
        if sentence_buffer.strip():  
            await text_queue.put((sentence_buffer.strip(), sentence_index))
            
        await text_queue.put("STOP")  
        
        # Wait for workers to finish current response tasks
        await tts_task
        await player_task 
        
        print() 
        chat_history.append({"role": "assistant", "content": full_ai_reply}) 
        if len(chat_history) > 12:  # Maintain short-term memory (6 rounds)
            chat_history.pop(1) 
            chat_history.pop(1) 
            
    except Exception as e:
        print(f"\nError occurred: {e}")
        await text_queue.put("STOP") 
        await tts_task
        await player_task

def initialize_hardware():
    """Initializes Speaker and Microphone volumes to 85%"""
    print("🔧 Initializing hardware volumes...")
    
    # 1. Set (Playback) volume to 85%
    os.system("amixer -c 2 sset PCM 85% --quiet")
    
    # 2. Set (Mic) volume to 85%
    os.system("amixer -c 2 sset Mic 85% --quiet")
    
    print("✅ Speaker (PCM) and Microphone set to 80%.")

# ==========================================
# 4. Main Loop
# ==========================================
async def main():
    global audio_queue  
    global text_queue   
    
    audio_queue = asyncio.Queue() 
    text_queue = asyncio.Queue()  

    # Hardware initialization
    initialize_hardware()

    print("⚽ Coach Qiuqiu is ready! (Streaming Mode Enabled)")
    
    # Initial Welcome Message
    welcome_task = asyncio.create_task(player_worker())
    await speak_to_queue("Hello there! I'm Coach Qiuqiu, your soccer assistant. Should we start with a soccer story or a quick quiz?", 0)
    await audio_queue.put("STOP") 
    await welcome_task            
    
    while True:
        user_input = listen()
        
        if not user_input: 
            continue
            
        if any(word in user_input for word in ["Goodbye", "Exit", "再见", "退出"]):
            exit_task = asyncio.create_task(player_worker())
            await speak_to_queue("Great training today! Remember to practice on the field. See you next time!", 99)
            await audio_queue.put("STOP") 
            await exit_task               
            break
            
        await chat_with_memory_and_speak(user_input)

if __name__ == "__main__":
    asyncio.run(main())