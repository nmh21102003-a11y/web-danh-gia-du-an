import streamlit as st
import pandas as pd

st.title("📊 Bảng Đánh Giá")

try:
    df = pd.read_excel("Du_Lieu_Danh_Gia.xlsx", sheet_name=0)
    
    # Tìm cột có chứa chữ "Thành viên"
    cols = df.columns.astype(str)
    col_thanh_vien = next((c for c in cols if 'Thành viên' in c), None)
    
    if col_thanh_vien:
        df = df.set_index(col_thanh_vien)
        st.bar_chart(df)
    else:
        st.write("Không tìm thấy cột 'Thành viên', hiển thị toàn bộ bảng:")
        st.dataframe(df)

except Exception as e:
    st.error(f"Lỗi đọc file: {e}")
