import streamlit as st
import pandas as pd
import altair as alt # Thư viện này hỗ trợ đổi màu cực tốt cho biểu đồ

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
    
    def be_gay_ten(ten):
        parts = str(ten).split(' ')
        if len(parts) >= 3: return f"{parts[0]}\n{parts[1]}\n{parts[2]}"
        elif len(parts) == 2: return f"{parts[0]}\n{parts[1]}"
        return ten

    df.index = [be_gay_ten(ten) for ten in df.index]
    df.columns = [f"Câu {i+1}" for i in range(len(df.columns))]
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    df_chart = df_numeric.reset_index()

    # --- 2. GIAO DIỆN ---
    st.header(f"📌 Tuần Đánh Giá: {selected_sheet}")
    st.write("---")

    # Hàm vẽ biểu đồ Cột Xanh (Dữ liệu thường)
    def ve_bieu_do_xanh(tieu_de, noi_dung, col_name):
        st.subheader(tieu_de)
        st.info(f"💡 Tiêu chí: {noi_dung}")
        chart = alt.Chart(df_chart).mark_bar(color='#3498db').encode(
            x=alt.X('Thành viên:N', axis=alt.Axis(labelAngle=0)),
            y=f'{col_name}:Q'
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

    # Hàm vẽ biểu đồ Cột Đỏ (Dữ liệu tiêu cực)
    def ve_bieu_do_do(tieu_de, noi_dung, col_name):
        st.subheader(tieu_de)
        st.warning(f"⚠️ Tiêu chí tiêu cực: {noi_dung}")
        chart = alt.Chart(df_chart).mark_bar(color='#e74c3c').encode(
            x=alt.X('Thành viên:N', axis=alt.Axis(labelAngle=0)),
            y=f'{col_name}:Q'
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

    # CHART 1 & 2 (Xanh)
    ve_bieu_do_xanh("1️⃣ Tiêu chí Câu 1", noi_dung_cau_hoi[0], 'Câu 1')
    ve_bieu_do_xanh("2️⃣ Tiêu chí Câu 2", noi_dung_cau_hoi[1], 'Câu 2')

    # CHART 3 & 4 (Đỏ - Tiêu cực)
    ve_bieu_do_do("3️⃣ Tiêu chí Câu 3", noi_dung_cau_hoi[2], 'Câu 3')
    ve_bieu_do_do("4️⃣ Tiêu chí Câu 4", noi_dung_cau_hoi[3], 'Câu 4')

    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_numeric, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}. Vui lòng kiểm tra file Excel.")
