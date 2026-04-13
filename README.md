# 🚀 AI Resume Enhancer Telegram Bot

The AI Resume Enhancer Bot is a powerful Telegram bot that helps job seekers easily optimize their resumes for a specific job description. Simply paste a Job Description and send your current resume, and the bot uses advanced AI (powered by Groq) to analyze, score, and rewrite your resume to be highly ATS-compliant. It then generates a freshly tailored PDF!

**Try it live here:** [https://t.me/ResumeEnhancerForRambot](https://t.me/ResumeEnhancerForRambot)

---

## 🏗 How It Works

1. **Start the Bot:** Send the `/start` command in Telegram.
2. **Send Job Description:** Paste the text of the job description you are aiming for.
3. **Upload Resume:** Send your current resume in PDF format.
4. **AI Processing:** 
   - The bot extracts text from your PDF and evaluates it against the job description.
   - It provides a **Match Score (Out of 10)** indicating your current suitability.
   - It enthusiastically rewrites your bullet points, integrating ATS keywords and aligning your experience to perfectly match the target role.
5. **Download the PDF:** The bot instantly generates a cleanly styled, professional PDF of your enhanced resume and sends it back to you!

---

## 🛠 Required Secrets & APIs (The "Hidden" Things)

To run this project on your own machine or deploy it to a server, you must set up two critical configuration keys. These should never be uploaded to GitHub directly (they stay safely inside a `.env` file).

1. **Telegram Bot Token:**
   - Open Telegram and search for the `@BotFather`.
   - Send the `/newbot` command, choose a name and a bot username.
   - BotFather will provide you with an **API Token**.

2. **Groq API Key:**
   - Go to the [Groq Console](https://console.groq.com/).
   - Sign up/Login and navigate to the "API Keys" section to generate a new secret key.
   - *Why Groq?* The bot uses Groq's lightning-fast inference for the `llama-3.1-8b-instant` LLM model to rewrite your resume with minimal wait times.

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RamBaranwal/Ai-Resume-Enhancer.git
   cd Ai-Resume-Enhancer
   ```

2. **Set up a Virtual Environment (Recommended):**
   ```bash
   python -m venv .venv
   
   # On Windows:
   .venv\Scripts\activate
   
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add Environment Variables:**
   Create a new file named `.env` in the root folder of the project. Add the following lines, replacing the placeholder text with your actual keys:
   ```env
   TELEGRAM_TOKEN=your_real_telegram_bot_token_here
   GROQ_API_KEY=your_real_groq_api_key_here
   ```

5. **Run the Bot:**
   ```bash
   python main.py
   ```
   You should see `🚀 Resume Enhancer Bot is starting...` in your terminal. You can now chat with your bot on Telegram!

---

## 📦 Tech Stack

* **Python 3**
* `pyTelegramBotAPI` - To handle interactions with the Telegram Bot API.
* `groq` - LLM connection for advanced resume tailoring.
* `pypdf` - To cleanly extract raw text from candidate PDF uploads.
* `markdown` & `xhtml2pdf` - To parse the AI's markdown response and convert it into the final formatted PDF.
