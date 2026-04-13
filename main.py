import os
import telebot
import time
from io import BytesIO
from pypdf import PdfReader          # ← Changed to pypdf
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ================== ENVIRONMENT VARIABLES (for Render) ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise ValueError("❌ TELEGRAM_TOKEN and GROQ_API_KEY must be set in environment variables!")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

user_data = {}  # user_id -> {"jd": text}

# ===========================================

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message,
        "👋 Welcome to Resume Enhancer Bot!\n\n"
        "How to use:\n"
        "1. Send the **Job Description** first (paste text)\n"
        "2. Send your **Resume as PDF**\n\n"
        "Commands:\n"
        "/restart - Clear and start over\n"
        "/exit or /cancel - Clear session"
    )

@bot.message_handler(commands=['restart', 'exit', 'cancel'])
def handle_clear(message):
    user_id = message.from_user.id
    user_data.pop(user_id, None)
    bot.reply_to(message, "✅ Session cleared! Send a new Job Description to begin.")

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_job_description(message):
    if message.text.startswith('/'):
        return

    user_id = message.from_user.id
    user_data[user_id] = {"jd": message.text.strip()}

    bot.reply_to(message, 
        "✅ Job Description saved!\n\n"
        "Now send your **resume as PDF** file."
    )

@bot.message_handler(content_types=['document'])
def handle_pdf(message):
    user_id = message.from_user.id

    if user_id not in user_data or "jd" not in user_data[user_id]:
        bot.reply_to(message, "⚠️ Please send the Job Description first.\nUse /restart or /exit.")
        return

    if not message.document.file_name.lower().endswith('.pdf'):
        bot.reply_to(message, "❌ Please send a valid PDF resume.")
        return

    processing_msg = bot.reply_to(message, "⏳ Processing your resume with AI... (10-40 seconds)")

    try:
        # Download PDF as bytes
        file_info = bot.get_file(message.document.file_id)
        downloaded_bytes = bot.download_file(file_info.file_path)

        # IMPORTANT FIX: Wrap bytes with BytesIO (fixes 'bytes' object has no attribute 'seek')
        pdf_stream = BytesIO(downloaded_bytes)

        # Use pypdf
        reader = PdfReader(pdf_stream)
        resume_text = "\n".join([page.extract_text() or "" for page in reader.pages]).strip()

        if len(resume_text) < 30:
            raise ValueError("Could not extract enough text from the PDF. Please use a text-selectable PDF.")

        jd = user_data[user_id]["jd"]

        # Safety: prevent very large inputs
        if len(resume_text) > 10000:
            resume_text = resume_text[:9500]

        prompt = f"""You are an expert ATS-friendly resume writer and evaluator.

Job Description:
{jd}

Original Resume:
{resume_text}

Task 1: Evaluate CV to JD Suitability Match
Analyze how well the candidate's skills and experience in the original resume match the requirements of the job description. On the very first line of your response, provide a suitability match score out of 10 in this exact format:
SCORE: X/10

Task 2: Tailor and Optimize the Resume
Your goal is to rewrite the resume to be a 9/10 or 10/10 match for this job summary:
- Aggressively integrate all exact keywords from the JD into the skills and professional experience.
- Powerfully rewrite bullet points to directly address JD requirements, adding implied missing skills into the Technical Skills section if reasonably connected.
- Transform the resume to be the perfect candidate profile for this job.
- Keep it concise (ideally 1 page).
- Professional tone, standard sections only.

IMPORTANT MARKDOWN FORMATTING RULES:
- Output the enhanced resume in clean Markdown format immediately after the score.
- The Name MUST be an <h1> tag or `# Name` at the very beginning.
- Contact info and role MUST be regular text, separated by `|`, each on a new line. Space before the new line is not necessary.
- Section headers MUST be `## Section Name` (e.g., `## Professional Summary`, `## Technical Skills`, `## Professional Experience`, `## Projects`, `## Education`).
- Job titles/Roles MUST be `**Role** | Company/Project` or `### Role`.
- For Technical Skills, use the format: `**Category:** Skill 1, Skill 2`
- Ensure there is NO extra conversational text."""

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=4000
        )

        enhanced_md = completion.choices[0].message.content.strip()

        # Parse the alignment score
        score = "N/A"
        if "SCORE:" in enhanced_md:
            import re
            score_match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?/10)', enhanced_md)
            if score_match:
                score = score_match.group(1)
            # Remove the score line from the markdown
            enhanced_md = re.sub(r'SCORE:.*?\n', '', enhanced_md, count=1).strip()

        # Generate visually styled PDF
        import markdown
        from xhtml2pdf import pisa
        
        html_content = markdown.markdown(enhanced_md)
        css = """
        <style>
            @page { size: letter; margin: 0.6in 0.8in; }
            body { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 10.5pt; color: #000; line-height: 1.4; }
            h1 { font-size: 20pt; text-align: center; color: #000; padding-bottom: 2px; margin-bottom: 12px; font-weight: bold; }
            h2 { font-size: 12pt; color: #000; margin-top: 16px; margin-bottom: 6px; font-weight: bold; border-bottom: none; }
            h3 { font-size: 10.5pt; color: #000; margin-top: 10px; margin-bottom: 4px; font-weight: bold; }
            ul { margin: 0 0 10px 0; padding-left: 20px; }
            li { margin-bottom: 4px; }
            p { margin: 5px 0; }
            strong { color: #000; font-weight: bold; }
        </style>
        """
        full_html = f"<html><head>{css}</head><body>{html_content}</body></html>"
        
        pdf_path = f"enhanced_{user_id}_{int(time.time())}.pdf"
        with open(pdf_path, "wb") as dest_pdf:
            pisa.CreatePDF(full_html, dest=dest_pdf)

        # Send enhanced resume
        caption_text = f"✅ Your tailored resume is ready!\n\n🎓 **Job Match Score:** {score}\n\nPlease review it before submitting."
        with open(pdf_path, 'rb') as f:
            bot.send_document(
                message.chat.id,
                f,
                caption=caption_text,
                parse_mode="Markdown"
            )

        os.remove(pdf_path)
        user_data.pop(user_id, None)

    except Exception as e:
        error_str = str(e).lower()
        if "429" in error_str or "rate limit" in error_str:
            user_msg = "❌ Groq rate limit reached. Wait 30-60 seconds and try again."
        elif "413" in error_str or "too large" in error_str:
            user_msg = "❌ Input too long. Shorten your JD or use a smaller PDF."
        else:
            user_msg = f"❌ Error: {str(e)[:180]}\n\nUse /restart or /exit and try again."

        bot.edit_message_text(
            chat_id=processing_msg.chat.id,
            message_id=processing_msg.message_id,
            text=user_msg
        )

if __name__ == "__main__":
    import traceback
    import sys

    # Fix UnicodeEncodeError for Windows console when printing emojis
    if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    
    print("🚀 Resume Enhancer Bot is starting...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print("Fatal error while running bot:")
        traceback.print_exc()
        # Keep the process alive for inspection in development
        time.sleep(1)