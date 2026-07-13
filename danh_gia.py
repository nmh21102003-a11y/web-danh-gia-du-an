import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Bảng Điều Khiển Đánh Giá Chi Tiết")

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
    noi_dung_cau_hoi = df_raw.set_index(col_cau_hoi).index.tolist()
    
    # Xoay bảng để Thành viên nằm ở trục X (ngang)
    df = df_raw.set_index(col_cau_hoi).T
    df.index.name = "Thành viên"
    
    # Đặt tên cột ngắn gọn để tránh biểu đồ bị rối
    df.columns = [f"Câu {i+1}" for i in range(len(df.columns))]
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    # --- 2. GIAO DIỆN ---
    st.header(f"📌 Tuần Đánh Giá: {selected_sheet}")
    st.write("---")

    # Hàm hiển thị biểu đồ
    def ve_bieu_do(tieu_de, noi_dung, du_lieu):
        st.subheader(tieu_de)
        st.info(f"💡 Tiêu chí: {noi_dung}")
        # Lệnh bar_chart mặc định của Streamlit sẽ tự động để tên nằm ngang
        st.bar_chart(du_lieu)

    # CHART 1
    ve_bieu_do("1️⃣ Tiêu chí Câu 1", noi_dung_cau_hoi[0], df_numeric[['Câu 1']])

    # CHART 2
    ve_bieu_do("2️⃣ Tiêu chí Câu 2", noi_dung_cau_hoi[1], df_numeric[['Câu 2']])

    # CHART 3
    ve_bieu_do("3️⃣ Tiêu chí Câu 3 & Câu 4", f"{noi_dung_cau_hoi[2]} & {noi_dung_cau_hoi[3]}", df_numeric[['Câu 3', 'Câu 4']])

    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_numeric, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}. Vui lòng kiểm tra file Excel.")
