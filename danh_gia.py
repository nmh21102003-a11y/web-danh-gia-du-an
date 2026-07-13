import streamlit as st
import pandas as pd
import altair as alt

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

    # --- XỬ LÝ DỮ LIỆU ---
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    noi_dung_cau_hoi = df_raw.set_index(col_cau_hoi).index.tolist()
    
    df = df_raw.set_index(col_cau_hoi).T
    df.index.name = "Thành viên"
    
    # Bẻ tên thành viên để nằm ngang
    def be_gay_ten(ten):
        parts = str(ten).split(' ')
        if len(parts) >= 3: return f"{parts[0]}\n{parts[1]}\n{parts[2]}"
        elif len(parts) == 2: return f"{parts[0]}\n{parts[1]}"
        return ten
    df.index = [be_gay_ten(ten) for ten in df.index]
    
    df.columns = [f"Câu {i+1}" for i in range(len(df.columns))]
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    df_chart = df_numeric.reset_index()

    st.header(f"📌 Tuần: {selected_sheet}")
    st.write("---")

    # Hàm vẽ cột Xanh (Câu 1, 2)
    def ve_bieu_do_xanh(tieu_de, noi_dung, col):
        st.subheader(tieu_de)
        st.info(f"💡 {noi_dung}")
        st.bar_chart(df_numeric[[col]])

    # CHART 1 & 2
    ve_bieu_do_xanh("1️⃣ Tiêu chí Câu 1", noi_dung_cau_hoi[0], "Câu 1")
    ve_bieu_do_xanh("2️⃣ Tiêu chí Câu 2", noi_dung_cau_hoi[1], "Câu 2")

    # CHART 3 (Gộp Câu 3, 4 màu Đỏ)
    st.subheader("3️⃣ Tiêu chí Câu 3 & Câu 4")
    st.warning(f"⚠️ {noi_dung_cau_hoi[2]} & {noi_dung_cau_hoi[3]}")
    
    # Dùng Altair để gộp và đổi màu Đỏ
    df_melt = df_chart.melt(id_vars=['Thành viên'], value_vars=['Câu 3', 'Câu 4'], var_name='Câu', value_name='Điểm')
    chart = alt.Chart(df_melt).mark_bar(color='#e74c3c').encode(
        x=alt.X('Thành viên:N', axis=alt.Axis(labelAngle=0)),
        y='Điểm:Q',
        column='Câu:N'
    )
    st.altair_chart(chart, use_container_width=True)

    with st.expander("📋 Xem Bảng Số Liệu"):
        st.dataframe(df_numeric, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
