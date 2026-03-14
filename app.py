import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF
import io

# --- 1. AI KURULUMU ---
st.set_page_config(page_title="AI Sağlık Analiz Paneli", layout="wide")

try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Multimodal modelimizi tanımlıyoruz
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("Secrets içinde API KEY eksik!")
except Exception as e:
    st.error(f"Sistem Hatası: {e}")

def turkce_duzelt(text):
    d = {"İ": "I", "ı": "i", "ş": "s", "Ş": "S", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in d.items(): text = str(text).replace(k, v)
    return text

# --- 2. GİRİŞ PANELİ ---
st.sidebar.header("📋 Danışan Profili")
u_name = st.sidebar.text_input("Ad Soyad", "Ismail Akkus")
u_age = st.sidebar.number_input("Yaş", 15, 90, 25)
u_height = st.sidebar.number_input("Boy (cm)", 100, 230, 180)
u_weight = st.sidebar.number_input("Kilo (kg)", 40, 200, 75)

# Metabolik Hesaplama (Mifflin-St Jeor)
# $$BMR = 10 \times \text{weight} + 6.25 \times \text{height} - 5 \times \text{age} + 5$$
bmr = (10 * u_weight) + (6.25 * u_height) - (5 * u_age) + 5

# --- 3. ANA PANEL ---
st.title("👁️ Multimodal AI: Görüntü ve Beslenme Analizi")
st.markdown("---")

col_img, col_res = st.columns([1, 1])

with col_img:
    st.subheader("📸 Vücut Analiz Fotoğrafı")
    uploaded_file = st.file_uploader("Boydan fotoğraf yükleyin", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, caption="Yüklenen Görsel", use_container_width=True)

with col_res:
    st.subheader("🤖 AI Uzman Analizi")
    if st.button("🚀 Fotoğrafı Analiz Et ve Raporla"):
        if uploaded_file:
            with st.spinner("Yapay zeka fotoğrafı inceliyor ve ölçüm yapıyor..."):
                # Gemini'ye fotoğrafı ve komutu gönderiyoruz
                prompt = f"""
                Sen bir antropometri uzmanı ve diyetisyensin. Fotoğraftaki kişiyi analiz et.
                Kullanıcı Bilgileri: {u_name}, {u_age} yaş, {u_height}cm boy, {u_weight}kg ağırlık.
                Bazal Metabolizma (BMR): {bmr} kcal.
                
                Lütfen şu analizleri yap:
                1. Fotoğrafa bakarak kişinin 'Omuz/Kalça Oranı' hakkında profesyonel bir tahminde bulun.
                2. Vücut tipi (Ektomorf, Mezomorf, Endomorf) analizi yap.
                3. Bu kişiye özel günlük 2200 kalorilik 3 ana öğün menü hazırla.
                4. Endüstri mühendisi titizliğiyle veriye dayalı 3 gelişim tavsiyesi ver.
                """
                try:
                    # Fotoğrafı modele gönderiyoruz
                    response = model.generate_content([prompt, img])
                    st.session_state['ai_final_report'] = response.text
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI Analiz Hatası: {e}")
        else:
            st.warning("Lütfen önce bir fotoğraf yükleyin.")

# --- 4. PDF RAPORLAMA ---
if 'ai_final_report' in st.session_state:
    if st.button("📄 Profesyonel Raporu PDF Olarak Al"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(200, 10, txt=turkce_duzelt(f"AI ANALIZ SONUCU - {u_name}"), ln=True, align='C')
        pdf.set_font("Helvetica", size=10)
        pdf.ln(10)
        pdf.multi_cell(0, 10, txt=turkce_duzelt(st.session_state['ai_final_report']))
        st.download_button("PDF İndir", data=bytes(pdf.output()), file_name=f"{u_name}_rapor.pdf")
        st.balloons()
