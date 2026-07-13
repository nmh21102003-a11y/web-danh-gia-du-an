import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Bảng Đánh Giá Tổng Hợp (Chế độ An Toàn)")

file_name = "Du_Lieu_Danh_Gia.xlsx"

@st.cache_data
def load_data():
    # Đọc file an toàn nhất có thể
    return pd.read_excel(file_name, sheet_name=None, dtype=str)

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Chọn Tuần:", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]

    # Dọn dẹp cột rác
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.fillna("") 
    
    st.subheader(f"Dữ liệu tuần: {selected_sheet}")
    
    # SỬ DỤNG st.table() THAY VÌ st.dataframe()
    # st.table vẽ bảng dạng HTML tĩnh, bỏ qua hoàn toàn công cụ PyArrow hay bị sập
    st.table(df)

except Exception as e:
    st.error(f"Lỗi đọc file: {e}")
