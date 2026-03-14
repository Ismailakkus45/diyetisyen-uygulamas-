import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from fpdf import FPDF
import google.generativeai as genai

# --- 1. AI YAPILANDIRMASI ---
st.set_page_config(page_title="Dijital Formül AI v3.0", layout="wide")

try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        ai_model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.warning("⚠️ API Key bulunamadı. Lütfen Secrets ayarlarını kontrol edin.")
except Exception as e:
    st.error(f"AI Kurulum Hatası: {e}")

def turkce_duzelt(text):
    d = {"İ": "I", "ı": "i", "ş": "s", "Ş": "S", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in d.items(): text = str(text).replace(k, v)
    return text

# --- 2. SIDEBAR ---
st.sidebar.header("👤 Danışan Profili")
name = st.sidebar.text_input("Ad Soyad", "Ismail Akkus")
age = st.sidebar.number_input("Yaş", 15, 90, 25)
height = st.sidebar.number_input("Boy (cm)", 100, 230, 180)
weight = st.sidebar.number_input("Kilo (kg)", 40, 200, 75)
activity = st.sidebar.selectbox("Aktivite", ["Hareketsiz", "Az Hareketli", "Orta Hareketli", "Çok Hareketli", "Sporcu"])

# --- 3. ANA EKRAN ---
st.title("🛡️ Dijital Formül: AI Karar Destek Paneli")
st.markdown("---")

col_analiz, col_rapor = st.columns([3, 2])
ratio_val = 0.0

with col_analiz:
    st.subheader("📸 Vücut Analizi")
    file = st.file_uploader("Boydan fotoğraf yükleyin", type=['jpg', 'jpeg', 'png'])
    
    if file:
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Mediapipe nesnesini her seferinde güvenli şekilde başlatıyoruz (HATA BURADAYDI)
        mp_pose = mp.solutions.pose
        with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
            results = pose.process(img_rgb)
            
            if results.pose_landmarks:
                annotated = img_rgb.copy()
                mp.solutions.drawing_utils.draw_landmarks(
                    annotated, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                st.image(annotated, caption="Analiz Tamamlandı", use_container_width=True)
                
                lm = results.pose_landmarks.landmark
                s_width = abs(lm[11].x - lm[12].x)
                h_width = abs(lm[23].x - lm[24].x)
                if h_width > 0:
                    ratio_val = round(s_width / h_width, 2)
                    st.success(f"Omuz/Kalça Oranı: {ratio_val}")
            else:
                st.error("Vücut algılanamadı.")

with col_rapor:
    st.subheader("📊 Metabolik Veriler")
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    act_map = {"Hareketsiz": 1.2, "Az Hareketli": 1.375, "Orta Hareketli": 1.55, "Çok Hareketli": 1.725, "Sporcu": 1.9}
    tdee = int(bmr * act_map[activity])
    
    st.metric("TDEE (Günlük Kalori)", f"{tdee} kcal")
    
    if st.button("🚀 AI Diyet Önerisi Oluştur"):
        if ratio_val > 0:
            with st.spinner("AI analiz yapıyor..."):
                prompt = f"""Diyetisyen rolünde cevap ver. Danışan: {name}, {age} yaşında, {height}cm boyunda, {weight}kg. 
                TDEE: {tdee} kcal. Vücut Oranı: {ratio_val}. Kısa bir analiz ve 3 öğünlük menü yaz."""
                try:
                    response = ai_model.generate_content(prompt)
                    st.session_state['ai_text'] = response.text
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI Hatası: {e}")
        else:
            st.warning("Lütfen önce fotoğraf analizi yapın.")

if 'ai_text' in st.session_state:
    if st.button("📄 Raporu PDF İndir"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(200, 10, txt=turkce_duzelt(f"AI ANALIZ RAPORU - {name}"), ln=True, align='C')
        pdf.set_font("Helvetica", size=10)
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=turkce_duzelt(st.session_state['ai_text']))
        st.download_button("Dosyayı Kaydet", data=bytes(pdf.output()), file_name="ai_rapor.pdf")
