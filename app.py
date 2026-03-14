import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF

# --- 1. SİSTEM YAPILANDIRMASI ---
st.set_page_config(page_title="AI Sağlık Analizi", layout="wide")

# API Anahtarı Denetimi
if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # 404 HATASINI BİTİREN SATIR: Sadece model ismini yazıyoruz.
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Yapılandırma Hatası: {e}")
else:
    st.error("⚠️ Streamlit Secrets içine 'GEMINI_API_KEY' anahtarını eklemelisiniz!")

def turkce_duzelt(text):
    d = {"İ": "I", "ı": "i", "ş": "s", "Ş": "S", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    for k, v in d.items(): text = str(text).replace(k, v)
    return text

# --- 2. GİRİŞ PANELİ ---
st.sidebar.header("📋 Kullanıcı Bilgileri")
u_name = st.sidebar.text_input("Ad Soyad", "Ismail Akkus")
u_weight = st.sidebar.number_input("Kilo (kg)", 40, 200, 75)

# --- 3. ANA PANEL ---
st.title("👁️ AI Görüntü ve Beslenme Analizi")
st.markdown("---")

col_img, col_res = st.columns([1, 1])

with col_img:
    st.subheader("📸 Fotoğraf Yükle")
    file = st.file_uploader("Analiz için fotoğraf seçin", type=['jpg', 'jpeg', 'png'])
    if file:
        img = Image.open(file)
        st.image(img, caption="Yüklenen Görsel", use_container_width=True)

with col_res:
    st.subheader("🤖 AI Uzman Yorumu")
    if st.button("🚀 Analizi Başlat"):
        if file:
            with st.spinner("AI fotoğrafı inceliyor..."):
                prompt = f"Sen uzman bir diyetisyensin. {u_name} isimli danışanı analiz et. Ağırlık: {u_weight}kg. Fotoğrafa bakarak vücut tipi yorumu ve 3 öğünlük örnek menü yaz."
                try:
                    # Fotoğrafı ve metni modele gönderiyoruz
                    response = model.generate_content([prompt, img])
                    st.session_state['ai_output'] = response.text
                    st.markdown(response.text)
                except Exception as e:
                    # Hata mesajını temizleyip kullanıcıya gösteriyoruz
                    st.error(f"Bağlantı Hatası: {e}")
        else:
            st.warning("Lütfen önce bir fotoğraf yükleyin.")

# --- 4. PDF RAPOR ---
if 'ai_output' in st.session_state:
    if st.button("📄 Raporu PDF Olarak Al"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 10, txt=turkce_duzelt(st.session_state['ai_output']))
        st.download_button("Dosyayı Kaydet", data=bytes(pdf.output()), file_name=f"{u_name}_analiz.pdf")
        st.balloons()
