import streamlit as st
import pandas as pd

# Cấu hình
st.set_page_config(layout="wide")
st.title("📊 Hệ thống Theo dõi & Đánh giá Thành viên")

# BẠN THAY ĐƯỜNG DẪN DƯỚI ĐÂY BẰNG LINK RAW TRÊN GITHUB CỦA BẠN
file_url = "https://raw.githubusercontent.com/TEN_USER/TEN_REPO/main/Du_Lieu_Danh_Gia.xlsx"

@st.cache_data(ttl=60) # Tự refresh mỗi 60 giây từ server
def load_data():
    return pd.read_excel(file_url, sheet_name=None)

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Tuần Đánh Giá:", list(all_sheets.keys()))
    df_raw = all_sheets[selected_sheet]

    # Xử lý dữ liệu
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    
    # Chuyển đổi dữ liệu để vẽ biểu đồ
    df = df_raw.set_index(col_cau_hoi).T
    df.index.name = "Thành viên"
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    st.header(f"📌 Tuần: {selected_sheet}")
    st.write("---")

    # Hiển thị các bảng (Giữ nguyên định dạng bạn muốn)
    st.subheader(f"1️⃣ {df_raw.iloc[0, 0]}")
    st.bar_chart(df.iloc[:, [0]], use_container_width=True)

    st.subheader(f"2️⃣ {df_raw.iloc[1, 0]}")
    st.bar_chart(df.iloc[:, [1]], use_container_width=True)

    # Bảng 3 (Gộp 3 & 4) - Cột đơn, màu xanh (như bảng 2)
    st.subheader("3️⃣ & 4️⃣ Tổng hợp tiêu cực")
    # Gộp điểm câu 3 và 4
    df_chart_34 = df.iloc[:, [2, 3]]
    df_chart_34.columns = ["Câu 3", "Câu 4"]
    st.bar_chart(df_chart_34, use_container_width=True)

    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_raw, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}. Hãy đảm bảo Link Raw GitHub của bạn công khai và đúng định dạng.")
