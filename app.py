import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pandas as pd
from datetime import datetime

# --- ARAYÜZ ---
st.set_page_config(page_title="ABP TDS QR Motor", layout="centered")

if 'kayitlar' not in st.session_state:
    st.session_state.kayitlar = []
if 'kamera_acik' not in st.session_state:
    st.session_state.kamera_acik = False

st.markdown("""
    <style>
    .stCamera { border: 5px solid #00c8ff; border-radius: 20px; }
    .stButton>button { width: 100%; height: 3.5em; background-color: #00c8ff; color: white; font-weight: bold; border-radius: 15px; }
    .qr-box { background-color: #0e1117; padding: 25px; border-radius: 15px; border: 3px solid #00c8ff; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔳 ABP TDS - QR İş Emri Terminali")

# --- AYARLAR ---
if not st.session_state.kamera_acik:
    if st.button("🔵 QR TARAYICIYI AÇ"):
        st.session_state.kamera_acik = True
        st.rerun()
else:
    if st.button("🔴 KAMERAYI KAPAT"):
        st.session_state.kamera_acik = False
        st.rerun()

# --- STANDART OPENCV QR MOTORU (Hata Vermez) ---
def qr_coz(img_file):
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    opencv_img = cv2.imdecode(file_bytes, 1)
    
    # OpenCV'nin dahili QR dedektörü
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(opencv_img)
    
    if data:
        return data.strip()
    return None

# --- AKIŞ ---
if st.session_state.kamera_acik:
    img_file = st.camera_input("QR Kodu ekrana ortalayın")
    
    if img_file:
        kod = qr_coz(img_file)
        
        if kod:
            st.markdown(f"""
                <div class="qr-box">
                    <h3 style="color: #00c8ff;">✅ QR KOD OKUNDU</h3>
                    <h1 style="font-size: 3rem;">{kod}</h1>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"📥 {kod} Kodunu Listeye Kaydet"):
                st.session_state.kayitlar.append({
                    "Tarih": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "İş Emri No": kod
                })
                st.toast("Kayıt Başarılı!", icon="🚀")
        else:
            st.warning("QR Kod okunamadı. Lütfen ışığı ve mesafeyi ayarlayın.")

# --- RAPORLAMA ---
if st.session_state.kayitlar:
    st.divider()
    df = pd.DataFrame(st.session_state.kayitlar)
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button("📥 Günlük Veriyi Excel'e Aktar", data=csv, file_name="ABP_QR_Rapor.csv")
