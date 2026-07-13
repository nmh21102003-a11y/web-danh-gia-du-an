import streamlit as st
import pandas as pd

st.title("📊 Bảng Dữ Liệu")

try:
    # Đọc file
    df = pd.read_excel("Du_Lieu_Danh_Gia.xlsx", sheet_name=0)
    
    # Hiển thị bảng đơn giản
    st.write("Dữ liệu đã được tải lên:")
    st.dataframe(df)

except Exception as e:
    st.error(f"Lỗi hệ thống: {e}")
