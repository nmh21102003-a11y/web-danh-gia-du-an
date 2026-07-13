import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Bảng Đánh Giá Tổng Hợp")

file_name = "Du_Lieu_Danh_Gia.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_name, sheet_name=None)

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Chọn Tuần:", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]

    # Dọn dẹp dữ liệu
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    col_thanh_vien = df.columns[0]
    df = df.set_index(col_thanh_vien)
    
    # Chỉ lấy các cột số để vẽ biểu đồ
    df_numeric = df.select_dtypes(include=['number'])

    st.subheader(f"Dữ liệu tuần: {selected_sheet}")
    
    # --- VẼ BIỂU ĐỒ BẰNG ẢNH TĨNH (KHÔNG BAO GIỜ SẬP) ---
    st.write("📈 Biểu đồ điểm số:")
    fig, ax = plt.subplots(figsize=(10, 6))
    df_numeric.plot(kind='barh', ax=ax) # Vẽ thanh ngang
    plt.tight_layout()
    st.pyplot(fig) # Hiển thị bức ảnh lên web
    
    # --- HIỂN THỊ BẢNG AN TOÀN ---
    st.write("📋 Bảng điểm chi tiết:")
    st.table(df.fillna(""))

except Exception as e:
    st.error(f"Lỗi: {e}")
