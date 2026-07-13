import streamlit as st
import pandas as pd

# Thiết lập giao diện rộng
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

    # --- 1. XỬ LÝ DỮ LIỆU ---
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    
    # Chuyển đổi để lấy các cột dữ liệu theo đúng thứ tự
    df = df_raw.set_index(col_cau_hoi).T
    df.index.name = "Thành viên"
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    # --- 2. GIAO DIỆN ---
    st.header(f"📌 Tuần: {selected_sheet}")
    st.write("---")

    # Mẹo: Đổi tên cột trong DataFrame tạm để hiển thị đẹp hơn
    df_chart = df.copy()
    df_chart.columns = [f"Câu {i+1}" for i in range(len(df_chart.columns))]

    # Hiển thị Câu 1
    st.subheader(f"1️⃣ {df_raw.iloc[0, 0]}")
    st.bar_chart(df_chart[['Câu 1']], use_container_width=True)

    # Hiển thị Câu 2
    st.subheader(f"2️⃣ {df_raw.iloc[1, 0]}")
    st.bar_chart(df_chart[['Câu 2']], use_container_width=True)

    # Hiển thị Câu 3 & 4 gộp chung
    st.subheader("3️⃣ & 4️⃣ Tiêu chí tiêu cực")
    st.warning(f"⚠️ {df_raw.iloc[2, 0]} & {df_raw.iloc[3, 0]}")
    st.bar_chart(df_chart[['Câu 3', 'Câu 4']], use_container_width=True)

    # --- 3. BẢNG CHI TIẾT ---
    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}. Vui lòng kiểm tra file dữ liệu.")
