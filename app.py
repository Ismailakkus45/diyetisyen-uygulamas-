import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF
import io

# --- SİSTEM AYARLARI ---
st.set_page_config(page_title="Akıllı Sağlık Analizi", layout="wide")

# Yeni API Anahtarını Tanımlama
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # 404 hatasını önlemek için stabil model ismini kullanıyoruz
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Sistem Yapılandırma Hatası: {e}")
else:
    st.error("⚠️ Lütfen Streamlit Secrets kısmına yeni API Key'i ekleyin!")

def turkce_duzelt(text):
    d = {"İ": "I", "ı": "i", "ş": "s", "Ş": "S", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in d.items(): text = str(text).replace(k, v)
    return text

# --- UI TASARIMI ---
st.title("👁️ Gelişmiş AI Analiz ve Beslenme Sistemi")
st.sidebar.header("📋 Kullanıcı Bilgileri")
u_name = st.sidebar.text_input("Ad Soyad", "Ismail Akkus")
u_weight = st.sidebar.number_input("Kilo (kg)", 40, 200, 75)

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📸 Analiz Fotoğrafı")
    uploaded_file = st.file_uploader("Fotoğraf yükleyin", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)

with col_right:
    st.subheader("🤖 Uzman AI Raporu")
    if st.button("🚀 Analizi Başlat"):
        if uploaded_file:
            with st.spinner("Yeni API Key ile analiz yapılıyor..."):
                prompt = f"""
                Sen uzman bir diyetisyen ve postür analistisin. 
                Danışan: {u_name}, Ağırlık: {u_weight}kg.
                Fotoğrafa bakarak; vücut tipi, omuz-kalça yapısı ve beslenme önerileri içeren detaylı bir rapor yaz.
                """
                try:
                    response = model.generate_content([prompt, img])
                    st.session_state['report_text'] = response.text
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"🚨 Analiz sırasında hata oluştu: {e}")
        else:
            st.warning("Lütfen bir fotoğraf seçin.")

# PDF MODÜLÜ
if 'report_text' in st.session_state:
    if st.button("📄 Raporu PDF Olarak İndir"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 10, txt=turkce_duzelt(st.session_state['report_text']))
        st.download_button("Dosyayı Kaydet", data=bytes(pdf.output()), file_name="analiz_sonucu.pdf")
        st.balloons()
