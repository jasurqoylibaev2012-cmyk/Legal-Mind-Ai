# main.py - Yakuniy Backend KODI (Barcha funksiyalar va JSON integratsiyasi)

from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
import json

# .env faylini yuklash
load_dotenv()

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ====================================================================
# Ma'lumotlarni JSON fayldan yuklash
# ====================================================================
DATA_FILE = 'data.json'
NOTARY_DATA = {}
QUICK_ANSWERS = {}

try:
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        NOTARY_DATA = data.get('notary_info', {})
        QUICK_ANSWERS = data.get('quick_answers', {})
    if not NOTARY_DATA or not QUICK_ANSWERS:
        raise ValueError("data.json faylida notarius_info yoki quick_answers ma'lumotlari bo'sh.")
    logging.info("Ma'lumotlar (Notarius/Chat) data.json'dan muvaffaqiyatli yuklandi.")
except FileNotFoundError:
    logging.error(f"Xato: {DATA_FILE} fayli topilmadi. Iltimos, fayl strukturasini tekshiring.")
except json.JSONDecodeError:
    logging.error(f"Xato: {DATA_FILE} fayl formati noto'g'ri (JSON sintaksis xatosi).")
except Exception as e:
    logging.error(f"Ma'lumotlarni yuklashda kutilmagan xato: {e}")

# ====================================================================
# AI Klientini Initsializatsiya Qilish
# ====================================================================
client = None
MODEL = 'gpt-4o-mini'
API_KEY = os.getenv("OPENAI_API_KEY")

try:
    if not API_KEY:
        raise ValueError(
            "API kaliti topilmadi. Iltimos, uni .env fayliga OPENAI_API_KEY deb kiriting.")

    client = OpenAI(api_key=API_KEY)
    logging.info("OpenAI mijoziga ulanish muvaffaqiyatli.")
except Exception as e:
    error_message = f"AI Ulanish Xatosi: {e}. AI funksiyalari o'chirilgan. Kalitni tekshiring."
    logging.error(error_message)
    client = None
    MODEL = None


# ====================================================================


def call_openai_api(prompt):
    """OpenAI API ga murojaat qilish uchun yordamchi funksiya."""
    if not client:
        return "AI xizmatiga ulanib bo'lmadi. Iltimos, API kalitingizni tekshiring."
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful legal assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Xato: AI so'rovida xato yuz berdi: {e}. Kalitni yoki savolni tekshiring."


# --- YORDAMCHI FUNKSIYALAR ---
def generate_document_python(data):
    turi = data.get('type', 'Shartnoma')
    client_info = data.get('client', 'Noma\'lum mijozlar')
    prompt = (
        f"Siz O'zbekiston qonunchiligini biladigan yuridik AI assistentsiz. Iltimos, '{turi}' uchun rasmiy yuridik shablonini generatsiya qiling. Hujjatda tomonlar ({client_info}) ko'rsatilsin. Shablonni faqat O'zbek tilida yozing.")
    document_content = call_openai_api(prompt)
    return {"status": "success", "document": document_content}


def analyze_contract_python(file):
    filename = file.filename if file else "Fayl yuklanmadi, namuna tahlili:"
    return {"status": "success", "fileName": filename,
            "risks": ["Band 3: noaniq majburiyatlar (DEMO).", "Band 7: bir tomonlama jarima belgilangan (DEMO).",
                      "Band 9: Majburiyatni bajarmaslik uchun jazo yozilmagan (DEMO)."]}


def legal_chat_python(question):
    prompt = (
        f"Siz professional yuridik AI konsultantsiz. Savol: '{question}'. Javobni O'zbek tilida, sodda, ammo yuridik jihatdan aniq tilda bering. Faqat javobni qaytaring.")
    answer = call_openai_api(prompt)
    return {"answer": answer}


def find_notary_python(location):
    """Notarius qidiruvi (Ma'lumotni NOTARY_DATA dan oladi)."""
    loc_lower = location.lower().strip() if location else ""
    search_key = loc_lower if loc_lower in NOTARY_DATA else "default"

    found_data = NOTARY_DATA.get(search_key, NOTARY_DATA["default"])

    return {
        "nearest": found_data["nearest"],
        "wait_time": found_data["wait_time"],
        "state_fee": found_data["state_fee"],
    }


def get_predefined_answer(key):
    """Tezkor savollar uchun javoblarni qaytarish (Ma'lumotni QUICK_ANSWERS dan oladi)."""
    return QUICK_ANSWERS.get(key, {"title": "Xato", "answer": "Tanlangan savol turi topilmadi."})


# ---------------- API YO'NALISHLARI (ROUTES) ----------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/api/generate-document", methods=['POST'])
def generate_document_route():
    data = request.json
    if not data or 'type' not in data or 'client' not in data:
        return jsonify({"status": "error", "message": "Hujjat turi va mijoz ma'lumotlari talab qilinadi."}), 400
    return jsonify(generate_document_python(data))


@app.route("/api/risk-analysis", methods=['POST'])
def risk_analysis_route():
    file = request.files.get('file')
    return jsonify(analyze_contract_python(file))


@app.route("/api/legal-chat", methods=['POST'])
def legal_chat_route():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"status": "error", "message": "Savol matni talab qilinadi."}), 400
    return jsonify(legal_chat_python(question))


@app.route("/api/quick-chat", methods=['POST'])
def quick_chat_route():
    data = request.json
    key = data.get('key')
    if not key:
        return jsonify({"status": "error", "message": "Savol kaliti talab qilinadi."}), 400

    result = get_predefined_answer(key)
    return jsonify(result)


@app.route("/api/notary", methods=['POST'])
def notary_route():
    data = request.json
    location = data.get('location')
    return jsonify(find_notary_python(location))


if __name__ == '__main__':
    app.run(port=5500, debug=True)