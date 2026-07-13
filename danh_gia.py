import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Hệ thống Theo dõi & Đánh giá Thành viên")

file_name = "Du_Lieu_Danh_Gia.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_name, sheet_name=None)

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Tuần Đánh Giá:", list(all_sheets.keys()))
    df_raw = all_sheets[selected_sheet]

    # --- XỬ LÝ DỮ LIỆU ---
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    
    # Chuyển đổi để lấy các cột dữ liệu theo đúng thứ tự
    df = df_raw.set_index(col_cau_hoi).T
    df.index.name = "Thành viên"
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    st.header(f"📌 Tuần: {selected_sheet}")
    st.write("---")

    # --- HIỂN THỊ CÁC BẢNG ---
    
    # Bảng 1: Hiển thị đúng tiêu đề + biểu đồ
    st.subheader(f"1️⃣ {df_raw.iloc[0, 0]}")
    st.bar_chart(df.iloc[:, [0]], use_container_width=True)

    # Bảng 2: Hiển thị đúng tiêu đề + biểu đồ
    st.subheader(f"2️⃣ {df_raw.iloc[1, 0]}")
    st.bar_chart(df.iloc[:, [1]], use_container_width=True)

    # Bảng 3 (Gộp Câu 3 & 4): Hiển thị tiêu đề + cảnh báo + biểu đồ gộp
    st.subheader("3️⃣ & 4️⃣ Tiêu chí tiêu cực")
    st.warning(f"⚠️ {df_raw.iloc[2, 0]} & {df_raw.iloc[3, 0]}")
    st.bar_chart(df.iloc[:, [2, 3]], use_container_width=True)

    # --- BẢNG CHI TIẾT ---
    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}. Vui lòng kiểm tra file dữ liệu.")
