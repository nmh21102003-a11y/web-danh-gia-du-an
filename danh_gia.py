import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📊 Hệ thống Theo dõi & Đánh giá Thành viên")

# Link GitHub của bạn
file_url = "https://github.com/nmh21102003-a11y/web-danh-gia-du-an/raw/refs/heads/main/Du_Lieu_Danh_Gia.xlsx"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_excel(file_url, sheet_name=None)

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Tuần Đánh Giá:", list(all_sheets.keys()))
    df_raw = all_sheets[selected_sheet]

    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    danh_sach_thanh_vien = df_raw.columns[1:].tolist()

    # Chuyển dữ liệu sang dạng dài để vẽ bằng Altair
    df_long = df_raw.melt(id_vars=[col_cau_hoi], var_name='Thành viên', value_name='Điểm')
    df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)

    st.header(f"📌 Tuần: {selected_sheet}")
    st.write("---")

    # Hàm vẽ biểu đồ CỐ ĐỊNH định dạng để bảng 1, 2, 3 giống hệt nhau
    def ve_bieu_do(cau_hoi_list, tieu_de, mau_sac):
        # Lọc dữ liệu: Nếu gộp thì cộng điểm, nếu không thì lấy giá trị
        df_plot = df_long[df_long[col_cau_hoi].isin(cau_hoi_list)].groupby('Thành viên', as_index=False)['Điểm'].sum()
        
        # Vẽ biểu đồ với thông số KHÓA CỨNG
        chart = alt.Chart(df_plot).mark_bar(size=40).encode(
            x=alt.X('Thành viên:N', sort=danh_sach_thanh_vien, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Điểm:Q', axis=alt.Axis(format="d")),
            color=alt.value(mau_sac)
        ).properties(width=800, height=300)
        
        st.subheader(tieu_de)
        st.altair_chart(chart, use_container_width=True)

    danh_sach_cau = df_raw[col_cau_hoi].tolist()

    # HIỂN THỊ ĐÚNG CẤU TRÚC
    # Bảng 1
    ve_bieu_do([danh_sach_cau[0]], f"1️⃣ {danh_sach_cau[0]}", '#3498db')
    # Bảng 2
    ve_bieu_do([danh_sach_cau[1]], f"2️⃣ {danh_sach_cau[1]}", '#3498db')
    # Bảng 3 (Gộp câu 3 & 4) - Vẫn dùng hàm ve_bieu_do này để giữ y hệt hình thức bảng 1 & 2
    ve_bieu_do([danh_sach_cau[2], danh_sach_cau[3]], f"3️⃣ & 4️⃣ {danh_sach_cau[2]} + {danh_sach_cau[3]}", '#e74c3c')

    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_raw, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
