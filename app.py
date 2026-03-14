import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from fpdf import FPDF
import google.generativeai as genai

# --- 1. AI & SİSTEM AYARLARI ---
st.set_page_config(page_title="Dijital Formül AI", layout="wide")

# Gemini Güvenli Kurulum
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ai_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ Secrets içinde GEMINI_API_KEY bulunamadı!")

def turkce_duzelt(text):
    d = {"İ": "I", "ı": "i", "ş": "s", "Ş": "S", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in d.items(): text = str(text).replace(k, v)
    return text

# --- 2. GİRİŞ ALANLARI ---
st.sidebar.header("👤 Danışan Profili")
name = st.sidebar.text_input("Ad Soyad", "Ismail Akkus")
age = st.sidebar.number_input("Yaş", 15, 90, 25)
height = st.sidebar.number_input("Boy (cm)", 100, 230, 180)
weight = st.sidebar.number_input("Kilo (kg)", 40, 200, 75)
activity = st.sidebar.selectbox("Aktivite", ["Hareketsiz", "Az Hareketli", "Orta Hareketli", "Çok Hareketli", "Sporcu"])

# --- 3. ANA PANEL ---
st.title("🛡️ Dijital Formül: Akıllı Diyet Asistanı")
st.markdown("---")

col_analiz, col_rapor = st.columns([3, 2])
ratio_val = 0.0

with col_analiz:
    st.subheader("📸 Vücut Analiz Motoru")
    file = st.file_uploader("Boydan fotoğraf yükleyin", type=['jpg', 'jpeg', 'png'])
    
    if file:
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        mp_pose = mp.solutions.pose
        with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
            results = pose.process(img_rgb)
            if results.pose_landmarks:
                annotated = img_rgb.copy()
                mp.solutions.drawing_utils.draw_landmarks(annotated, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                st.image(annotated, caption="Analiz Başarılı", use_container_width=True)
                
                lm = results.pose_landmarks.landmark
                s_w = abs(lm[11].x - lm[12].x)
                h_w = abs(lm[23].x - lm[24].x)
                ratio_val = round(s_w / h_w, 2)
                st.success(f"Omuz/Kalça Oranı: {ratio_val}")
            else:
                st.error("Vücut algılanamadı, lütfen daha net bir fotoğraf yükleyin.")

with col_rapor:
    st.subheader("📊 Metabolik Veriler")
    # Mifflin-St Jeor Formülü
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    st.metric("Bazal Enerji (BMR)", f"{bmr} kcal")
    
    if st.button("🚀 AI Diyet Analizi Oluştur"):
        if ratio_val > 0:
            with st.spinner("Gemini AI analiz yapıyor..."):
                prompt = f"Sen bir diyetisyensin. Danışan: {name}, {age} yaşında, {height}cm, {weight}kg. Omuz/Kalça Oranı: {ratio_val}. Bu verilere göre kısa bir analiz ve 3 öğünlük örnek menü yaz."
                response = ai_model.generate_content(prompt)
                st.session_state['ai_text'] = response.text
                st.markdown(response.text)
        else:
            st.warning("Lütfen önce bir fotoğraf analiz edin.")

# --- 4. PDF ÇIKTISI ---
if 'ai_text' in st.session_state:
    if st.button("📄 Profesyonel Raporu İndir"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(200, 10, txt=turkce_duzelt(f"AI ANALIZ RAPORU - {name}"), ln=True, align='C')
        pdf.set_font("Helvetica", size=10)
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=turkce_duzelt(st.session_state['ai_text']))
        st.download_button("PDF Kaydet", data=bytes(pdf.output()), file_name=f"{name}_rapor.pdf")
        st.balloons()
