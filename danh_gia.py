import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Bảng Đánh Giá Tổng Hợp")

file_name = "Du_Lieu_Danh_Gia.xlsx"

@st.cache_data
def load_data():
    # Đọc file, ép mọi thứ về dạng chuỗi (string) để tránh lỗi ArrowTypeError
    df = pd.read_excel(file_name, sheet_name=None, dtype=str)
    return df

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Chọn Tuần:", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]

    # Dọn dẹp dữ liệu: loại bỏ cột 'Unnamed'
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Ép kiểu dữ liệu để hiển thị ổn định
    df = df.fillna("") # Thay giá trị trống bằng chuỗi rỗng
    
    st.header(f"Dữ liệu: {selected_sheet}")
    
    # Hiển thị bảng dữ liệu (Đây là cách an toàn nhất)
    st.dataframe(df, use_container_width=True)
    
    # Nếu muốn vẽ biểu đồ, ta chỉ vẽ từ các cột số (phải ép kiểu lại lần nữa)
    st.subheader("Biểu đồ điểm số")
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    st.bar_chart(df_numeric)

except Exception as e:
    st.error(f"Lỗi: {e}. Vui lòng kiểm tra file Excel.")
