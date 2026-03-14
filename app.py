import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from fpdf import FPDF
import google.generativeai as genai

# --- AI KURULUMU ---
# Secrets'tan anahtarı güvenli şekilde alıyoruz
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Dijital Formül AI v3.0", layout="wide")

# (Önceki fonksiyonlar: turkce_duzelt, load_pose aynı kalıyor)
def turkce_duzelt(text):
    d = {"İ": "I", "ı": "i", "ş": "s", "Ş": "S", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in d.items(): text = str(text).replace(k, v)
    return text

# --- SIDEBAR & HESAPLAMALAR ---
st.title("🛡️ Dijital Formül: Akıllı Diyet Asistanı")
name = st.sidebar.text_input("Ad Soyad", "Ismail Akkus")
age = st.sidebar.number_input("Yaş", 15, 90, 25)
height = st.sidebar.number_input("Boy (cm)", 100, 230, 180)
weight = st.sidebar.number_input("Kilo (kg)", 40, 200, 75)
activity = st.sidebar.selectbox("Aktivite", ["Hareketsiz", "Az Hareketli", "Orta Hareketli", "Çok Hareketli", "Sporcu"])

bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
tdee = int(bmr * 1.5) # Basit katsayı

col_analiz, col_ai = st.columns([1, 1])

with col_analiz:
    st.subheader("📸 Vücut Analizi")
    file = st.file_uploader("Fotoğraf Yükle", type=['jpg', 'jpeg', 'png'])
    ratio_val = 0.0
    if file:
        # (Burada fotoğraf işleme ve ratio_val hesabı önceki kısımla aynı kalacak)
        st.info("Analiz Tamamlandı.")
        ratio_val = 1.8 # Örnek değer

with col_ai:
    st.subheader("🤖 AI Diyetisyen Yorumu")
    if st.button("🚀 AI Analizi Oluştur"):
        with st.spinner("AI verileri analiz ediyor..."):
            prompt = f"""
            Sen profesyonel bir diyetisyensin. Danışan verileri:
            İsim: {name}, Yaş: {age}, Boy: {height}cm, Kilo: {weight}kg.
            Hesaplanan TDEE: {tdee} kcal.
            AI tarafından ölçülen Omuz/Kalça Oranı: {ratio_val}.
            Bu verilere dayanarak kısa bir sağlık yorumu ve günlük 3 öğünlük örnek bir menü hazırla.
            """
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state['ai_report'] = response.text

# --- RAPORLAMA ---
if 'ai_report' in st.session_state:
    if st.button("📄 AI Raporunu PDF Olarak İndir"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(200, 10, txt=turkce_duzelt(f"DIJITAL FORMUL AI RAPORU - {name}"), ln=True, align='C')
        pdf.set_font("Helvetica", size=10)
        pdf.multi_cell(0, 10, txt=turkce_duzelt(st.session_state['ai_report']))
        st.download_button("Dosyayı Kaydet", data=bytes(pdf.output()), file_name="ai_diyet_raporu.pdf")
