import streamlit as st
import pandas as pd

# Cấu hình trang
st.set_page_config(layout="wide")
st.title("📊 Hệ thống Theo dõi & Đánh giá Thành viên")

# Link file Excel trực tiếp từ GitHub của bạn
file_url = "https://github.com/nmh21102003-a11y/web-danh-gia-du-an/raw/refs/heads/main/Du_Lieu_Danh_Gia.xlsx"

# Hàm tải dữ liệu với cơ chế cache tự làm mới sau 60 giây
@st.cache_data(ttl=60)
def load_data():
    return pd.read_excel(file_url, sheet_name=None)

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Tuần Đánh Giá:", list(all_sheets.keys()))
    df_raw = all_sheets[selected_sheet]

    # Xử lý dữ liệu
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    
    # Chuyển đổi dữ liệu để vẽ biểu đồ (Thành viên làm index)
    df = df_raw.set_index(col_cau_hoi).T
    df.index.name = "Thành viên"
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    st.header(f"📌 Tuần: {selected_sheet}")
    st.write("---")

    # Hiển thị Bảng 1 (Giữ nguyên)
    st.subheader(f"1️⃣ {df_raw.iloc[0, 0]}")
    st.bar_chart(df.iloc[:, [0]], use_container_width=True)

    # Hiển thị Bảng 2 (Giữ nguyên)
    st.subheader(f"2️⃣ {df_raw.iloc[1, 0]}")
    st.bar_chart(df.iloc[:, [1]], use_container_width=True)

    # Hiển thị Bảng 3 & 4 gộp chung (Giống hình thức bảng 2)
    st.subheader("3️⃣ & 4️⃣ Tổng hợp tiêu chí")
    st.info(f"💡 {df_raw.iloc[2, 0]} + {df_raw.iloc[3, 0]}")
    df_chart_34 = df.iloc[:, [2, 3]]
    df_chart_34.columns = ["Câu 3", "Câu 4"]
    st.bar_chart(df_chart_34, use_container_width=True)

    # Bảng chi tiết
    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_raw, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}. Vui lòng kiểm tra lại đường dẫn file trên GitHub.")
