import streamlit as st
import pandas as pd

st.set_page_config(page_title="Đánh giá dự án", layout="wide")
st.title("📊 Bảng Điều Khiển Đánh Giá Tổng Hợp")

@st.cache_data
def load_data(file_path):
    # Đọc file với encoding utf-8, nếu lỗi thì dùng latin1 (rất bền bỉ)
    try:
        df = pd.read_csv(file_path, skiprows=2, encoding='utf-8')
    except:
        df = pd.read_csv(file_path, skiprows=2, encoding='latin1')
    
    df = df.head(4) # Chỉ lấy đúng 4 câu hỏi
    df.columns = [str(c).strip() for c in df.columns]
    df = df.fillna(0)
    df = df.set_index(df.columns[0])
    return df

file_name = "Phieu_Danh_Gia_Tong_Hop_10_Nguoi.xlsx"

try:
    df = load_data(file_name)
    
    st.subheader(f"📈 {df.index[0]}")
    st.bar_chart(df.iloc[0])
    
    st.subheader(f"🚀 {df.index[1]}")
    st.bar_chart(df.iloc[1])
    
    st.subheader("⚠️ Tổng hợp Câu 3 & 4")
    st.bar_chart(df.iloc[2:4].T) # Vẽ cột gộp

except Exception as e:
    st.error(f"Lỗi hệ thống: {e}")
