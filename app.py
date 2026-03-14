import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF

# --- SISTEM AYARLARI ---
st.set_page_config(page_title="AI Analiz Sistemi", layout="wide")

# API KONTROLÜ
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # EN KRITIK NOKTA: Model ismini doğrudan yazıyoruz.
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Yapılandırma Hatası: {e}")
else:
    st.error("⚠️ Streamlit Secrets içinde 'GEMINI_API_KEY' bulunamadı!")

def turkce_duzelt(text):
    d = {"İ": "I", "ı": "i", "ş": "s", "Ş": "S", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in d.items(): text = str(text).replace(k, v)
    return text

# --- UI ---
st.title("🤖 Yeni Nesil AI Analiz Paneli")
st.sidebar.header("📋 Kullanıcı Verileri")
u_name = st.sidebar.text_input("Ad Soyad", "Ismail Akkus")
u_weight = st.sidebar.number_input("Kilo (kg)", 40, 200, 75)

uploaded_file = st.file_uploader("Analiz edilecek fotoğrafı yükleyin", type=['jpg', 'jpeg', 'png'])

if st.button("🚀 Analizi Başlat"):
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Analiz Edilen Görsel", width=400)
        
        with st.spinner("AI fotoğrafı görüyor ve yorumluyor..."):
            prompt = f"Sen bir uzman diyetisyensin. {u_name} isimli danışanın fotoğrafını ve {u_weight}kg ağırlığını analiz et. Vücut tipi ve beslenme önerileri sun."
            try:
                # 404 hatasını bypass eden en sade çağırma şekli
                response = model.generate_content([prompt, img])
                st.session_state['report'] = response.text
                st.markdown(response.text)
            except Exception as e:
                st.error(f"⚠️ AI Yanıt Vermedi (Hata Kodu): {e}")
    else:
        st.warning("Lütfen bir fotoğraf seçin.")

# PDF ÇIKTISI
if 'report' in st.session_state:
    if st.button("📄 Raporu PDF Al"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(0, 10, txt=turkce_duzelt(st.session_state['report']))
        st.download_button("İndir", data=bytes(pdf.output()), file_name="analiz_raporu.pdf")
