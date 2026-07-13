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

    # --- XỬ LÝ DỮ LIỆU ĐỂ GIỮ NGUYÊN THỨ TỰ ---
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    # Lấy danh sách tên theo đúng cột trong Excel
    danh_sach_thanh_vien = df_raw.columns[1:].tolist()
    
    # Định dạng dữ liệu dạng dài (long format) cho Altair
    df_long = df_raw.melt(id_vars=[col_cau_hoi], var_name='Thành viên', value_name='Điểm')
    df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)

    st.header(f"📌 Tuần: {selected_sheet}")
    st.write("---")

    # Hàm vẽ biểu đồ với Altair (Cho phép ép tên nằm ngang và giữ thứ tự)
    def ve_bieu_do_altair(cau_hoi, mau_sac):
        df_plot = df_long[df_long[col_cau_hoi] == cau_hoi]
        
        chart = alt.Chart(df_plot).mark_bar(color=mau_sac).encode(
            x=alt.X('Thành viên:N', sort=danh_sach_thanh_vien, axis=alt.Axis(labelAngle=0)), # labelAngle=0 ép nằm ngang
            y='Điểm:Q'
        ).properties(width=800, height=300)
        
        st.subheader(f"Tiêu chí: {cau_hoi}")
        st.altair_chart(chart, use_container_width=True)

    # Lấy danh sách các câu hỏi
    danh_sach_cau = df_raw[col_cau_hoi].tolist()

    # Vẽ biểu đồ
    ve_bieu_do_altair(danh_sach_cau[0], '#3498db') # Câu 1 (Xanh)
    ve_bieu_do_altair(danh_sach_cau[1], '#3498db') # Câu 2 (Xanh)
    
    # Câu 3 & 4 (Đỏ)
    ve_bieu_do_altair(danh_sach_cau[2], '#e74c3c')
    ve_bieu_do_altair(danh_sach_cau[3], '#e74c3c')

    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_raw, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
