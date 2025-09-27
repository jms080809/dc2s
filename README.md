# **DC2S - Discord Chat To Shorts Video**

---

## 📖 Description
**DC2S** is a Python-based tool that converts Discord chat logs into short-form videos.  
It leverages **MoviePy**, **OpenAI APIs**, and other libraries to process chat data and render videos automatically.  

---

## ⚙️ Environment Setup
Install dependencies with:

```bash
pip install openai moviepy requests python-dotenv pillow numpy
```
> Note: ```requirements.txt``` is not included because dependencies may frequently change.
---
## 🖥️ System Requirements

Rendering requires **high memory (RAM)**.

⚠️ Not recommended for **WSL** due to limited RAM and swap memory.

✅ Best performance on native OS (Windows, macOS, Linux) with sufficient memory.

---
## 🚀 Usage

Prepare your Discord chat data (JSON export or API call).

Run the main script to generate a video:

python src/main.py

In this process, this program makes directories that are **essential** for working like chats/, scenarios/,output/, which are made for debugging so you don't have to care about them.

Generated videos will be saved in the output/ directory.

### 🎬 Example Output

Converts raw chat logs → formatted scenario → rendered short-form video.

Supports text + sound effects.

you can see many many examples of videos made from this program in this youtube channel, which is mine:
> https://www.youtube.com/@ho3_txle

## 📄 License

This project is licensed under the Creative Commons Attribution-NonCommercial (CC BY-NC 4.0) License.

You are free to share and adapt the work for non-commercial purposes only, with attribution.
For full license text, see: CC BY-NC 4.0 License
