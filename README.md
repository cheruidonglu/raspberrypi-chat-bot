# Coach Qiuqiu: AI Soccer Assistant for Kids ⚽

Coach Qiuqiu is an interactive, voice-based AI toy built on **Raspberry Pi 5**. It is designed to engage children with soccer knowledge through humorous conversations, multiple-choice quizzes, and inspiring soccer stories. 

By leveraging **Doubao LLM** for intelligence and **Microsoft Edge-TTS** for smooth, streaming voice output, Coach Qiuqiu provides a natural and "fluid" conversational experience[cite: 2].

---


## ✨ Features
* **Intelligent Conversation**: Powered by Doubao for a witty and enthusiastic coaching persona.
* **Streaming Voice Output**: Uses a dual-worker pipeline (TTS & Player) to eliminate long pauses between sentences.
* **Soccer Knowledge Quizzes**: Automatically generates multiple-choice questions to test the user's soccer IQ.
* **Smart Mic Control**: Uses SoX for intelligent silence detection, automatically stopping the recording when the child finishes speaking.
* **Hardware Optimized**: Includes automatic microphone gain control via `amixer` to prevent audio clipping.

---

## 🛠️ Hardware Requirements
* **Raspberry Pi 5** (or Pi 4).
* **USB Microphone** (or a Respeaker HAT).
* **Speaker** (via 3.5mm jack or USB).
* **Internet Connection** (for API calls).

---

## 📦 Software Prerequisites
Before running the project, ensure you have the following system dependencies installed on your Raspberry Pi:

```bash
# Update system and install Git
sudo apt update && sudo apt install git -y 

# Install SoX for audio recording
sudo apt install sox libsox-fmt-all -y
```

---

## 🚀 Setup Guide

### 1. Clone the Repository
```bash
git clone [https://github.com/cheruidonglu/raspberrypi-chat-bot.git]
cd raspberrypi-chat-bot
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory to store your API keys securely. **Never share this file!**

```env
# Baidu Speech API (STT)
BAIDU_APP_ID=your_app_id
BAIDU_API_KEY=your_api_key
BAIDU_SECRET_KEY=your_secret_key

# Doubao API (LLM)
DOUBAO_API_KEY=your_api_key
```

### 3. Install Python Dependencies
It is recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🎮 How to Use
Simply run the main script to start the coach:

```bash
python main.py
```

* **To Talk**: Wait for the 🎤 icon, speak, and stop for 1 second; the coach will automatically respond.
* **To Exit**: Say "Goodbye" or "Exit" (in English or Chinese) to shut down the program safely.

---

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page if you want to help Coach Qiuqiu learn new soccer drills.

---

## 📜 License
[**MIT**]

