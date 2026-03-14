import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from fpdf import FPDF
import os

# --- SISTEM AYARLARI ---
st.set_page_config(page_title="Dijital Formül AI", layout="wide")

@st.cache_resource
def load_pose():
    return mp.solutions.pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

def turkce_duzelt(text):
    d = {"İ": "I", "ı": "i", "ş": "s", "Ş": "S", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in d.items(): text = str(text).replace(k, v)
    return text

# --- UI ---
st.title("🛡️ Dijital Formül: AI Karar Destek Sistemi")
st.sidebar.header("👤 Danışan Profili")
name = st.sidebar.text_input("Ad Soyad", "Ismail Akkus")
age = st.sidebar.number_input("Yaş", 15, 90, 25)
height = st.sidebar.number_input("Boy (cm)", 100, 230, 180)
weight = st.sidebar.number_input("Kilo (kg)", 40, 200, 75)
activity = st.sidebar.selectbox("Aktivite", ["Hareketsiz", "Az Hareketli", "Orta Hareketli", "Çok Hareketli", "Sporcu"])

col_analiz, col_sonuc = st.columns([3, 2])
ratio_val = 0.0

with col_analiz:
    st.subheader("📸 Vücut Analizi")
    file = st.file_uploader("Boy fotoğrafı yükleyin", type=['jpg', 'jpeg', 'png'])
    if file:
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pose = load_pose()
        res = pose.process(img_rgb)
        if res.pose_landmarks:
            annotated = img_rgb.copy()
            mp.solutions.drawing_utils.draw_landmarks(annotated, res.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)
            st.image(annotated, caption="Analiz Tamamlandı", use_container_width=True)
            lm = res.pose_landmarks.landmark
            s_w = abs(lm[11].x - lm[12].x)
            h_w = abs(lm[23].x - lm[24].x)
            ratio_val = round(s_w / h_w, 2)
            st.success(f"Omuz/Kalça Oranı: {ratio_val}")

with col_sonuc:
    st.subheader("📊 Metabolik Veriler")
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    st.metric("TDEE Tahmini", f"{int(bmr * 1.5)} kcal")
    if st.button("🚀 Raporu İndir"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(200, 10, txt=turkce_duzelt(f"ANALIZ: {name}"), ln=True, align='C')
        st.download_button("📄 PDF Kaydet", data=bytes(pdf.output()), file_name="analiz.pdf")
