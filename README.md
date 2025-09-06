# Komuna | Antifa Bot

> A local and private, uncensored llm repurposed by the people, for the people. Information should be freely shared and Komuna has a lot of useful information for you to explore! Type !komuna help to get started.

---

## 🚀 About the Bot
- This bot, regardless of interface, is instructed to answer queries as truthfully as possible. Due to quirks with the programming or the llm tech itself, it won't deliver good dialogue if you are not asking **specific** questions (avoid "can you explain that?", try "can you explain the steps to achieve communism?").
- If the bot responds to the wrong parts of your message, you can use the !komuna refine command to give it another shot. You can also do !komuna clear to erase the memory without restarting, and !komuna help for all commands.
- Komuna was trained on the sources listed in trained_data.txt
- Download Size: 2.7GB
- Expands to 10GB

---

## 🛠 Tech Stack
- **Language:** [Python]  
- **Framework:** [FastAPI, ngrok]  

---

## 📦 Installation

### Python
- Check Python Version
    - `python --version` or `python3 --version`
- Antifa Bot was made with Version 3.13.7

### Virtual Environment
- Navigate to Project Folder
    - `cd path/to/project`
- Create a Virtual Environment called 'name'
    - `python -m venv name` (or `python3`)
- Activate it
    - Linux/MacOS
    - `source name/bin/activate`
    - Windows (PowerShell)
    - `name\Scripts\Activate.ps1`
    
### Dependencies

#### Python Dependencies
- `pip install -r requirements.txt`

#### Other Dependencies
- [Ollama](https://ollama.com/download)
    - Run Ollama
    - Pull Model (mannix/llama3.1-8b-abliterated) (4.7GB)
- [The Vectorstore](https://drive.google.com/drive/folders/1qcSXrVgGhVh92Dt7AluAPb2Zqjg1x8ay?usp=drive_link)
    - Without this the bot won't have any of the trained data
    - Place next to main.py
- [ngrok (optional)](https://ngrok.com/)
    - Use ngrok to give your local FastAPI server a temporary public URL for testing or sharing

---

## 🔧 Running The Bot

### CLI - Main Interface
- `python main.py` (or `python3`)
- '!help' for list of commands

### Discord Bot
- Edit discord_bot.py for instructions on creating a discord bot
- `python discord_bot.py`
- Once it connects, the bot should go online in discord. Type "!komuna help" to test

### Web UI
- Run fastapp.py with `uvicorn fastapp:app --port 8000`, now you can connect in your browser at 127.0.0.1:8000
- (Optional) In another terminal, run `ngrok http 8000`, ngrok will display a web address you can share to allow other people to connect, or yourself from another device
