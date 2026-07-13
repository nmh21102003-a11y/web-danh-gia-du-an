import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Bảng Đánh Giá Tổng Hợp")

file_name = "Du_Lieu_Danh_Gia.xlsx"

@st.cache_data
def load_data():
    # Đọc file, bỏ qua 2 dòng đầu nếu cần (dựa trên cấu trúc file của bạn)
    df = pd.read_excel(file_name, sheet_name=None)
    return df

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Chọn Tuần:", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]

    # --- DỌN DỮ LIỆU ---
    # 1. Bỏ tất cả cột có tên 'Unnamed'
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # 2. Tìm cột tên thành viên (cột đầu tiên thường là tên)
    col_thanh_vien = df.columns[0]
    df = df.set_index(col_thanh_vien)
    
    # 3. Chỉ giữ lại các cột chứa số (điểm)
    df = df.select_dtypes(include=['number'])

    st.header(f"Dữ liệu: {selected_sheet}")
    
    # 4. Dùng biểu đồ thanh mặc định (Rất nhanh và không lỗi)
    st.bar_chart(df)
    
    with st.expander("Xem bảng dữ liệu chi tiết"):
        st.dataframe(df)

except Exception as e:
    st.error(f"Lỗi: {e}. Hãy kiểm tra xem file Excel của bạn có bị để trống dòng đầu tiên không nhé!")
