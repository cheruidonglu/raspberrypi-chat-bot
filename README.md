# Coach Qiuqiu: AI Soccer Assistant for Kids ⚽

Coach Qiuqiu is an interactive, voice-based AI toy built on **Raspberry Pi 5**. It is designed to engage children with soccer knowledge through humorous conversations, multiple-choice quizzes, and inspiring soccer stories. 

[cite_start]By leveraging **Doubao LLM** for intelligence and **Microsoft Edge-TTS** for smooth, streaming voice output, Coach Qiuqiu provides a natural and "fluid" conversational experience.

---

## ✨ Features
* [cite_start]**Intelligent Conversation**: Powered by Doubao（doubao-1-5-pro-32k-250115）for a witty and enthusiastic coaching persona.
* [cite_start]**Streaming Voice Output**: Uses a dual-worker pipeline (TTS & Player) to eliminate long pauses between sentences.
* [cite_start]**Soccer Knowledge Quizzes**: Automatically generates multiple-choice questions to test the user's soccer IQ.
* [cite_start]**Smart Mic Control**: Uses SoX for intelligent silence detection, automatically stopping the recording when the child finishes speaking.
* [cite_start]**Hardware Optimized**: Includes automatic microphone gain control via `amixer` to prevent audio clipping.

---

## 🛠️ Hardware Requirements
* [cite_start]**Raspberry Pi 5** (or Pi 4).
* [cite_start]**USB Microphone** (or a Respeaker HAT).
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
