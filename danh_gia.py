import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Hệ thống Theo dõi Tiến độ & Đánh giá Horizon")

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
    
    df = df_raw.set_index(col_cau_hoi).T
    df.index.name = "Thành viên"
    
    # Bẻ tên nằm ngang
    def be_gay_ten(ten):
        parts = str(ten).split(' ')
        if len(parts) >= 3: return f"{parts[0]}\n{parts[1]}\n{parts[2]}"
        elif len(parts) == 2: return f"{parts[0]}\n{parts[1]}"
        return ten
    df.index = [be_gay_ten(ten) for ten in df.index]
    
    df.columns = [f"Câu {i+1}" for i in range(len(df.columns))]
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    # --- 2. GIAO DIỆN ---
    st.header(f"📌 Tuần: {selected_sheet}")
    st.write("---")

    # Câu 1 & 2: Dùng bar_chart bình thường
    st.subheader("1️⃣ Tiêu chí Câu 1")
    st.info(f"💡 {noi_dung_cau_hoi[0]}")
    st.bar_chart(df_numeric[['Câu 1']])

    st.subheader("2️⃣ Tiêu chí Câu 2")
    st.info(f"💡 {noi_dung_cau_hoi[1]}")
    st.bar_chart(df_numeric[['Câu 2']])

    # Câu 3 & 4: Dùng bar_chart, và nó sẽ tự hiển thị màu khác cho bạn
    st.subheader("3️⃣ Tiêu chí Câu 3 & Câu 4")
    st.warning(f"⚠️ {noi_dung_cau_hoi[2]} & {noi_dung_cau_hoi[3]}")
    st.bar_chart(df_numeric[['Câu 3', 'Câu 4']])

    # --- BẢNG DỮ LIỆU ---
    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_numeric, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
