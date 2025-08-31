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


Generated videos will be saved in the output/ directory.

### 🎬 Example Output

Converts raw chat logs → formatted scenario → rendered short-form video.

Supports text + sound effects.

Example:

[Discord Chat]
User1: Hello!
User2: Hi, how are you?

↓ ↓ ↓

[Generated Shorts Video]
- Animated text captions
- Background audio
- Dynamic visual effects

## 📄 License

This project is licensed under the Creative Commons Attribution-NonCommercial (CC BY-NC 4.0) License.

You are free to share and adapt the work for non-commercial purposes only, with attribution.
For full license text, see: CC BY-NC 4.0 License
