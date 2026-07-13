import streamlit as st
import pandas as pd
import plotly.express as px

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
    
    # Xoay bảng để Thành viên nằm ở trục X
    df = df_raw.set_index(col_cau_hoi).T
    df.index.name = "Thành viên"
    
    df.columns = [f"Câu {i+1}" for i in range(len(df.columns))]
    df_numeric = df.apply(pd.to_numeric, errors='coerce').fillna(0)
    df_chart = df_numeric.reset_index()

    # --- 2. GIAO DIỆN VỚI PLOTLY (TÊN NGANG & THANH CUỘN) ---
    st.header(f"📌 Tuần Đánh Giá: {selected_sheet}")
    st.write("---")

    def ve_bieu_do_plotly(tieu_de, noi_dung, columns_to_plot):
        st.subheader(tieu_de)
        st.info(f"💡 Nội dung: {noi_dung}")
        
        # Tạo biểu đồ Plotly
        fig = px.bar(df_chart, x='Thành viên', y=columns_to_plot, 
                     barmode='group', template='plotly_white')
        
        # Ép tên nằm ngang
        fig.update_xaxes(tickangle=0)
        
        # Cấu hình thanh cuộn (nếu có nhiều thành viên)
        fig.update_layout(xaxis=dict(rangeslider=dict(visible=True)))
        
        st.plotly_chart(fig, use_container_width=True)

    # CHART 1 & 2 & 3
    ve_bieu_do_plotly("1️⃣ Tiêu chí Câu 1", noi_dung_cau_hoi[0], ['Câu 1'])
    ve_bieu_do_plotly("2️⃣ Tiêu chí Câu 2", noi_dung_cau_hoi[1], ['Câu 2'])
    ve_bieu_do_plotly("3️⃣ Tiêu chí Câu 3 & Câu 4", f"{noi_dung_cau_hoi[2]} & {noi_dung_cau_hoi[3]}", ['Câu 3', 'Câu 4'])

    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_numeric, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
