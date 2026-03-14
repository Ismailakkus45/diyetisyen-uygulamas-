import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from fpdf import FPDF

# Türkçe Karakter Fix
def turkce_duzelt(text):
    d = {"İ": "I", "ı": "i", "ş": "s", "Ş": "S", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in d.items(): text = str(text).replace(k, v)
    return text

def metabolizma_motoru(w, h, age, act):
    bmr = (10 * w) + (6.25 * h) - (5 * age) + 5
    katsayilar = {"Hareketsiz": 1.2, "Az Hareketli": 1.375, "Orta Hareketli": 1.55, "Çok Hareketli": 1.725, "Sporcu": 1.9}
    tdee = bmr * katsayilar[act]
    p = (tdee * 0.30) / 4
    c = (tdee * 0.40) / 4
    f = (tdee * 0.30) / 9
    return round(bmr), round(tdee), round(p), round(c), round(f)

st.set_page_config(page_title="Dijital Formül AI v2.0", layout="wide")
st.title("🛡️ Dijital Formül: AI Diyetisyen Karar Destek Paneli")

st.sidebar.header("👤 Danışan Profili")
name = st.sidebar.text_input("Ad Soyad", "Ismail Akkus")
age = st.sidebar.number_input("Yaş", 15, 90, 25)
height = st.sidebar.number_input("Boy (cm)", 100, 230, 180)
weight = st.sidebar.number_input("Kilo (kg)", 40, 200, 75)
activity = st.sidebar.selectbox("Aktivite Seviyesi", ["Hareketsiz", "Az Hareketli", "Orta Hareketli", "Çok Hareketli", "Sporcu"])
blood_sugar = st.sidebar.number_input("Açlık Kan Şekeri", 50, 300, 95)

col_analiz, col_sonuc = st.columns([3, 2])
ratio_val = 0.0

with col_analiz:
    st.subheader("📸 Vücut Analizi")
    file = st.file_uploader("Boy fotoğrafı yükleyin", type=['jpg', 'jpeg', 'png'])
    if file:
        img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_pose = mp.solutions.pose
        with mp_pose.Pose(static_image_mode=True) as pose:
            res = pose.process(img_rgb)
            if res.pose_landmarks:
                annotated = img_rgb.copy()
                mp.solutions.drawing_utils.draw_landmarks(annotated, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                st.image(annotated, caption="AI Analizi", use_container_width=True)
                lm = res.pose_landmarks.landmark
                s_w = abs(lm[11].x - lm[12].x)
                h_w = abs(lm[23].x - lm[24].x)
                ratio_val = round(s_w / h_w, 2)
                st.success(f"Oran: {ratio_val}")

with col_sonuc:
    st.subheader("📊 Metabolik Rapor")
    bmr, tdee, p, c, f = metabolizma_motoru(weight, height, age, activity)
    st.metric("Günlük Harcama (TDEE)", f"{tdee} kcal")
    st.info(f"🥩 P: {p}g | 🍞 C: {c}g | 🥑 F: {f}g")

if st.button("🚀 PDF Raporu İndir"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(200, 10, txt=turkce_duzelt("DIJITAL FORMUL AI ANALIZI"), ln=True, align='C')
    pdf_bytes = bytes(pdf.output())
    st.download_button("📄 Kaydet", data=pdf_bytes, file_name=f"{name}_rapor.pdf")
