import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Hệ thống Theo dõi & Đánh giá Thành viên")

# BƯỚC 1: Sử dụng file_uploader để up file mới lên là web tự nhận
uploaded_file = st.sidebar.file_uploader("Chọn file Excel đánh giá:", type=["xlsx"])

if uploaded_file is not None:
    # Đọc dữ liệu từ file mới up lên
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
    selected_sheet = st.sidebar.selectbox("Tuần Đánh Giá:", list(all_sheets.keys()))
    df_raw = all_sheets[selected_sheet]

    # Xử lý dữ liệu
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    df = df_raw.set_index(col_cau_hoi).T
    df.index.name = "Thành viên"
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    st.header(f"📌 Tuần: {selected_sheet}")
    
    # HIỂN THỊ BẢNG 1 & 2 (Giữ nguyên)
    st.subheader(f"1️⃣ {df_raw.iloc[0, 0]}")
    st.bar_chart(df.iloc[:, [0]], use_container_width=True)

    st.subheader(f"2️⃣ {df_raw.iloc[1, 0]}")
    st.bar_chart(df.iloc[:, [1]], use_container_width=True)

    # HIỂN THỊ BẢNG 3 (Gộp câu 3, 4 vào 1 bảng, màu đỏ, tên câu hỏi rõ ràng)
    st.subheader("3️⃣ & 4️⃣ Tiêu chí tiêu cực")
    st.warning(f"💡 {df_raw.iloc[2, 0]} + {df_raw.iloc[3, 0]}")
    
    # Gộp câu 3 và 4 (index 2 và 3)
    df_chart_34 = df.iloc[:, [2, 3]]
    df_chart_34.columns = ["Câu 3", "Câu 4"]
    st.bar_chart(df_chart_34, use_container_width=True)

    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_raw, use_container_width=True)
else:
    st.info("Vui lòng tải file Excel lên thanh bên trái để bắt đầu.")
