import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from fpdf import FPDF
import google.generativeai as genai

# --- 1. AI & SISTEM YAPILANDIRMASI ---
st.set_page_config(page_title="Dijital Formül AI v3.0", layout="wide")

# Gemini Kurulumu
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # Model ismini tam yol (models/...) vererek 'NotFound' hatasını fixliyoruz
    ai_model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"⚠️ AI Yapılandırma Hatası: {e}. Lütfen Streamlit Secrets ayarlarını kontrol et.")

# MediaPipe Pose Modelini Önbelleğe Alıyoruz (Performans için)
@st.cache_resource
def get_pose_model():
    return mp.solutions.pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

# Türkçe Karakter Düzenleyici (PDF ve AI Raporu için)
def turkce_duzelt(text):
    d = {"İ": "I", "ı": "i", "ş": "s", "Ş": "S", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in d.items(): text = str(text).replace(k, v)
    return text

# --- 2. SIDEBAR (VERI GIRISI) ---
st.sidebar.header("👤 Danışan Profili")
name = st.sidebar.text_input("Ad Soyad", "Ismail Akkus")
age = st.sidebar.number_input("Yaş", 15, 90, 25)
height = st.sidebar.number_input("Boy (cm)", 100, 230, 180)
weight = st.sidebar.number_input("Kilo (kg)", 40, 200, 75)
activity = st.sidebar.selectbox("Aktivite Seviyesi", ["Hareketsiz", "Az Hareketli", "Orta Hareketli", "Çok Hareketli", "Sporcu"])

# --- 3. ANA EKRAN TASARIMI ---
st.title("🛡️ Dijital Formül: AI Diyetisyen Karar Destek Paneli")
st.markdown("---")

col_analiz, col_rapor = st.columns([3, 2])
ratio_val = 0.0

with col_analiz:
    st.subheader("📸 Görüntü İşleme ve Vücut Analizi")
    file = st.file_uploader("Boydan bir fotoğraf yükleyin", type=['jpg', 'jpeg', 'png'])
    
    if file:
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        with st.spinner("AI vücut hatlarını analiz ediyor..."):
            pose = get_pose_model()
            results = pose.process(img_rgb)
            
            if results.pose_landmarks:
                annotated = img_rgb.copy()
                mp.solutions.drawing_utils.draw_landmarks(
                    annotated, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)
                st.image(annotated, caption="AI Iskelet Analizi Tamamlandı", use_container_width=True)
                
                lm = results.pose_landmarks.landmark
                # Omuz genişliği (11-12) / Kalça genişliği (23-24)
                s_width = abs(lm[11].x - lm[12].x)
                h_width = abs(lm[23].x - lm[24].x)
                if h_width > 0:
                    ratio_val = round(s_width / h_width, 2)
                    st.success(f"Ölçülen Omuz/Kalça Oranı: {ratio_val}")
            else:
                st.error("Vücut algılanamadı. Lütfen daha net bir fotoğraf yükleyin.")

with col_rapor:
    st.subheader("📊 Metabolik Veriler")
    # Mifflin-St Jeor Denklem Mühendisliği
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    act_map = {"Hareketsiz": 1.2, "Az Hareketli": 1.375, "Orta Hareketli": 1.55, "Çok Hareketli": 1.725, "Sporcu": 1.9}
    tdee = int(bmr * act_map[activity])
    
    st.metric("Günlük Enerji İhtiyacı (TDEE)", f"{tdee} kcal")
    
    st.markdown("---")
    st.subheader("🤖 AI Diyetisyen Görüşü")
    
    if st.button("🚀 AI Analizi ve Menü Oluştur"):
        with st.spinner("Gemini AI verileri yorumluyor..."):
            prompt = f"""
            Sen uzman bir diyetisyensin. Danışan verileri şunlar:
            Ad: {name}, Yaş: {age}, Boy: {height}cm, Kilo: {weight}kg.
            Hesaplanan Günlük Kalori İhtiyacı: {tdee} kcal.
            AI Görüntü Analizi Omuz/Kalça Oranı: {ratio_val}.
            
            Lütfen şu 3 şeyi yap:
            1. Vücut oranına ve kilosuna göre kısa bir profesyonel analiz yap.
            2. Bu kaloriye uygun 3 ana öğünden oluşan bir günlük menü taslağı yaz.
            3. Bir endüstri mühendisi disipliniyle öneriler sun.
            """
            try:
                response = ai_model.generate_content(prompt)
                ai_output = response.text
                st.markdown(ai_output)
                # PDF için raporu session_state'e kaydediyoruz
                st.session_state['ai_text'] = ai_output
            except Exception as e:
                st.error(f"AI Yanıt Hatası: {e}")

# --- 4. PDF RAPORLAMA ---
st.markdown("---")
if 'ai_text' in st.session_state:
    if st.button("📄 Profesyonel Analiz Raporunu PDF Al"):
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", 'B', 16)
            pdf.cell(200, 10, txt=turkce_duzelt(f"DIJITAL FORMUL AI RAPORU - {name}"), ln=True, align='C')
            
            pdf.set_font("Helvetica", size=11)
            pdf.ln(10)
            # AI metnini PDF'e uygun formata getiriyoruz
            pdf.multi_cell(0, 8, txt=turkce_duzelt(st.session_state['ai_text']))
            
            pdf_bytes = bytes(pdf.output())
            st.download_button(
                label="📁 PDF İndirmeyi Başlat",
                data=pdf_bytes,
                file_name=f"{turkce_duzelt(name)}_Analiz_Raporu.pdf",
                mime="application/pdf"
            )
            st.balloons()
        except Exception as e:
            st.error(f"PDF Oluşturma Hatası: {e}")
