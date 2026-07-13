import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Bảng Đánh Giá Tổng Hợp")

file_name = "Du_Lieu_Danh_Gia.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(file_name, sheet_name=None, dtype=str)
    return df

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Chọn Tuần:", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]

    # Dọn rác file Excel
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Thiết lập cột tên thành viên
    col_thanh_vien = df.columns[0]
    df = df.set_index(col_thanh_vien)
    
    # Ép kiểu sang số học
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    st.header(f"Dữ liệu: {selected_sheet}")

    # --- TẠO BỘ LỌC ĐỂ BIỂU ĐỒ HẾT RỐI MẮT ---
    danh_sach_cau_hoi = df_numeric.columns.tolist()
    cau_hoi_duoc_chon = st.selectbox("📌 Chọn tiêu chí đánh giá để xem biểu đồ:", danh_sach_cau_hoi)

    # --- VẼ BIỂU ĐỒ NGANG ---
    st.subheader(f"Kết quả: {cau_hoi_duoc_chon}")
    # Thuộc tính horizontal=True giúp tên người nằm ngang, dễ đọc tuyệt đối
    st.bar_chart(df_numeric[[cau_hoi_duoc_chon]], horizontal=True)

    # --- BẢNG DỮ LIỆU TỔNG ---
    with st.expander("👀 Bấm vào đây để xem toàn bộ bảng điểm chi tiết"):
        st.dataframe(df)

except Exception as e:
    st.error(f"Lỗi: {e}. Vui lòng kiểm tra file Excel.")
