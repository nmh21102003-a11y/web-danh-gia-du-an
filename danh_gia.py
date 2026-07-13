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

    # --- 1. XỬ LÝ DỮ LIỆU & BẺ TÊN THÀNH VIÊN ---
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    noi_dung_cau_hoi = df_raw.set_index(col_cau_hoi).index.tolist()
    
    # Xoay bảng
    df = df_raw.set_index(col_cau_hoi).T
    df.index.name = "Thành viên"
    
    # MẸO: Bẻ tên thành viên để ép hiển thị ngang
    def be_gay_ten(ten):
        parts = str(ten).split(' ')
        if len(parts) >= 3:
            return f"{parts[0]}\n{parts[1]}\n{parts[2]}"
        elif len(parts) == 2:
            return f"{parts[0]}\n{parts[1]}"
        return ten

    df.index = [be_gay_ten(ten) for ten in df.index]
    
    # Đổi tên cột ngắn gọn
    df.columns = [f"Câu {i+1}" for i in range(len(df.columns))]
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    # --- 2. GIAO DIỆN ---
    st.header(f"📌 Tuần Đánh Giá: {selected_sheet}")
    st.write("---")

    def ve_bieu_do(tieu_de, noi_dung, du_lieu):
        st.subheader(tieu_de)
        st.info(f"💡 Tiêu chí: {noi_dung}")
        # use_container_width=True giúp biểu đồ trải rộng ra
        st.bar_chart(du_lieu, use_container_width=True)

    # CHART 1, 2, 3
    ve_bieu_do("1️⃣ Tiêu chí Câu 1", noi_dung_cau_hoi[0], df_numeric[['Câu 1']])
    ve_bieu_do("2️⃣ Tiêu chí Câu 2", noi_dung_cau_hoi[1], df_numeric[['Câu 2']])
    ve_bieu_do("3️⃣ Tiêu chí Câu 3 & Câu 4", f"{noi_dung_cau_hoi[2]} & {noi_dung_cau_hoi[3]}", df_numeric[['Câu 3', 'Câu 4']])

    # --- BẢNG DỮ LIỆU ---
    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_numeric, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}. Vui lòng kiểm tra file Excel.")
