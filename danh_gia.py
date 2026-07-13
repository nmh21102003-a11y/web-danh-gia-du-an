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

    # XỬ LÝ DỮ LIỆU
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    
    # Chuyển dữ liệu: Thành viên làm cột (index), Câu hỏi làm dòng
    df = df_raw.set_index(col_cau_hoi).T
    df.index.name = "Thành viên"
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    st.header(f"📌 Tuần: {selected_sheet}")
    st.write("---")

    # Hiển thị biểu đồ 1
    st.subheader(f"1️⃣ {df_raw.iloc[0, 0]}")
    st.bar_chart(df.iloc[:, [0]], use_container_width=True)

    # Hiển thị biểu đồ 2
    st.subheader(f"2️⃣ {df_raw.iloc[1, 0]}")
    st.bar_chart(df.iloc[:, [1]], use_container_width=True)

    # Hiển thị biểu đồ 3 (Gộp Câu 3 & 4)
    # Vì dùng chung st.bar_chart, nó sẽ tự động đặt cột cạnh nhau và căn lề y hệt 2 cái trên
    st.subheader("3️⃣ & 4️⃣ Các tiêu chí tiêu cực")
    st.warning(f"⚠️ {df_raw.iloc[2, 0]} & {df_raw.iloc[3, 0]}")
    st.bar_chart(df.iloc[:, [2, 3]], use_container_width=True)

    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
