# 球球教练：少儿足球知识对话机器人 ⚽

球球教练是一款基于 **树莓派 5 (Raspberry Pi 5)** 开发的交互式语音人工智能玩具。它旨在通过幽默的对话、足球知识问答以及励志的足球故事来吸引孩子们。

通过整合 **豆包大模型 (Doubao LLM)** 提供智能大脑，并使用 **微软 Edge-TTS** 实现流畅的流式语音输出，球球教练能够提供自然且“丝滑”的对话体验。

---

## ✨ 项目特性
* **智能对话**：由豆包大模型提供支持，拥有风趣且热情的教练人设。
* **流式语音输出**：采用双工人流水线（TTS 合成与音频播放并行的模式）架构，有效消除了句子之间的长停顿。
* **足球知识竞赛**：自动生成单选题，全方位测试用户的足球知识储备。
* **智能麦克风控制**：利用 SoX 实现智能静音检测，在孩子说完话后自动停止录音。
* **硬件优化**：包含通过 `amixer` 实现的自动麦克风增益控制，防止音频录制过程中的爆音现象。

---

## 🛠️ 硬件需求
* **树莓派 5** (或树莓派 4)。
* **USB 麦克风** (或 Respeaker 扩展板)。
* **扬声器** (通过 3.5mm 音频口或 USB 连接)。
* **互联网连接** (用于调用各平台 API)。

---

## 📦 软件环境准备
在运行项目之前，请确保你的树莓派已安装以下系统依赖：

```bash
# 更新系统并安装 Git
sudo apt update && sudo apt install git -y

# 安装用于音频录制的 SoX
sudo apt install sox libsox-fmt-all -y
```

---

## 🚀 快速上手指南

### 1. 克隆仓库
```bash
git clone https://github.com/cheruidonglu/raspberrypi-chat-bot.git
cd raspberrypi-chat-bot
```

### 2. 配置环境变量
在项目根目录创建一个 `.env` 文件，用于安全地存储你的 API 密钥。**切记：永远不要将此文件上传到 GitHub！**

```env
# 百度语音识别 (STT) 密钥
BAIDU_APP_ID=你的_APP_ID
BAIDU_API_KEY=你的_API_KEY
BAIDU_SECRET_KEY=你的_SECRET_KEY

# 豆包大模型 (LLM) 密钥
DOUBAO_API_KEY=你的_API_KEY
```

### 3. 安装 Python 依赖库
建议使用虚拟环境进行安装：

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🎮 如何使用
执行主脚本即可启动球球教练：

```bash
python main.py
```

* **开始对话**：当终端出现 🎤 图标时即可说话，说完后停顿约 1 秒，教练会自动响应。
* **退出程序**：说出“再见”或“退出”，即可安全关闭程序。

---

## 🤝 参与贡献
我们非常欢迎任何形式的贡献、问题反馈（Issues）或功能建议！如果你想帮助球球教练学习新的足球战术，请随时在 Issues 页面留言。