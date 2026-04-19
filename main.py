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

# doubao LLM Configuration
DOUBAO_API_KEY = os.getenv('DOUBAO_API_KEY')
doubao_client = OpenAI(api_key=DOUBAO_API_KEY, base_url="https://ark.cn-beijing.volces.com/api/v3")

# Hardware & File Paths
MIC_ID = "plughw:2,0" 
TEMP_WAV = "input.wav"
TEMP_MP3 = "output.mp3"

# ==========================================
# 2. Functional Modules: Listen & Speak
# ==========================================
def listen():
    """Captures audio from the microphone and converts it to text via Baidu ASR."""
    print("\n🎤 球球教练正在听... (说完后停顿1.2秒会自动结束录音)")
    
    # Using SoX (rec) for intelligent silence detection
    cmd = (
        f"AUDIODEV={MIC_ID} timeout 10 rec -q -c 1 -r 16000 {TEMP_WAV} "
        f"silence 1 0.1 3% 1 1.2 3%"
    )
    
    os.system(cmd)
    
    if not os.path.exists(TEMP_WAV):
        return ""
        
    print("✅ 听到你结束说话了，正在识别...")
    
    with open(TEMP_WAV, 'rb') as f:
        audio_data = f.read()
        
    # Language ID 1737 represents English
    result = baidu_client.asr(audio_data, 'wav', 16000, {'dev_pid': 1537})

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
            print(f"⚠️ 文字转音频合成失败: {e}")
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
            print(f"⚠️ 音频播放错误: {file_path} - {e}")
            
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
        你是一个幽默、热情的足球知识对话机器人，名字叫‘球球’。你正在和一个小球迷进行语音聊天。
        你的任务是：
        1. 出足球相关的选择题,或者讲个足球故事。
        2. 如果出题的话,请出选择题,包含3个选项,题目不要过于简单。
        3. 回复不要超过60个字。
        """
    }
]

async def chat_with_memory_and_speak(user_input):
    """Handles LLM interaction and manages the concurrent TTS/Playback pipeline."""
    global chat_history
    chat_history.append({"role": "user", "content": user_input})
    print("🧠 球球教练正在急速思考...")
    
    # Initialize background workers
    player_task = asyncio.create_task(player_worker()) 
    tts_task = asyncio.create_task(tts_worker()) 
    
    try:
        response = doubao_client.chat.completions.create(
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
        print(f"\n发生错误: {e}")
        await text_queue.put("STOP") 
        await tts_task
        await player_task

def initialize_hardware():
    """Initializes Speaker and Microphone volumes to 85%"""
    print("🔧 初始化硬件的音量...")
    
    # 1. Set (Playback) volume to 85%
    os.system("amixer -c 2 sset PCM 85% --quiet")
    
    # 2. Set (Mic) volume to 85%
    os.system("amixer -c 2 sset Mic 85% --quiet")
    
    print("✅ 麦克风和扬声器音量设置到80%.")

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

    print("⚽ 足球机器人已进入【流式丝滑模式】")
    
    # Initial Welcome Message
    welcome_task = asyncio.create_task(player_worker())
    await speak_to_queue("你好月月！我是你的足球小助手球球，今天你想让我给你讲个足球故事，还是考考你？", 0)
    await audio_queue.put("STOP") 
    await welcome_task            
    
    while True:
        user_input = listen()
        
        if not user_input: 
            continue
            
        if any(word in user_input for word in ["再见", "退出"]):
            exit_task = asyncio.create_task(player_worker())
            await speak_to_queue("今天的训练很愉快！记得多去操场上跑跑哦，下次见！", 99)
            await audio_queue.put("STOP") 
            await exit_task               
            break
            
        await chat_with_memory_and_speak(user_input)

if __name__ == "__main__":
    asyncio.run(main())