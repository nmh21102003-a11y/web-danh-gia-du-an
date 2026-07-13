import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Hệ thống Đánh giá Hiệu suất Horizon")

file_name = "Du_Lieu_Danh_Gia.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_name, sheet_name=None)

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Tuần Đánh Giá:", list(all_sheets.keys()))
    df_raw = all_sheets[selected_sheet]

    # --- 1. XỬ LÝ DỮ LIỆU ĐỂ GIỮ NGUYÊN THỨ TỰ ---
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    
    # Quan trọng: Lấy danh sách tên theo đúng thứ tự cột từ Excel
    danh_sach_thanh_vien = df_raw.columns[1:].tolist()
    
    # Chuyển đổi dữ liệu
    df = df_raw.set_index(col_cau_hoi).T
    df.index.name = "Thành viên"
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Ép thứ tự index theo đúng danh sách gốc
    df = df.reindex(danh_sach_thanh_vien)

    # --- 2. GIAO DIỆN ---
    st.header(f"📌 Tuần: {selected_sheet}")
    st.write("---")

    # Hiển thị Câu 1 & 2
    st.subheader(f"1️⃣ {df_raw.iloc[0, 0]}")
    st.bar_chart(df.iloc[:, [0]], use_container_width=True)

    st.subheader(f"2️⃣ {df_raw.iloc[1, 0]}")
    st.bar_chart(df.iloc[:, [1]], use_container_width=True)

    # Hiển thị Câu 3 & 4 gộp chung
    st.subheader("3️⃣ & 4️⃣ Tiêu chí tiêu cực")
    st.warning(f"⚠️ {df_raw.iloc[2, 0]} & {df_raw.iloc[3, 0]}")
    # Đảm bảo giữ nguyên thứ tự khi vẽ biểu đồ gộp
    st.bar_chart(df.iloc[:, [2, 3]], use_container_width=True)

    # --- 3. BẢNG CHI TIẾT ---
    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}. Vui lòng kiểm tra lại cấu trúc file dữ liệu.")
