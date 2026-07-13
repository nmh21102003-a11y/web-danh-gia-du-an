import streamlit as st
import pandas as pd
import altair as alt

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

    # --- XỬ LÝ ĐỂ CỐ ĐỊNH THỨ TỰ & LẤY ĐỦ TÊN ---
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    col_cau_hoi = df_raw.columns[0]
    danh_sach_thanh_vien = df_raw.columns[1:].tolist()
    
    # Chuyển dữ liệu sang dạng dài và đảm bảo mọi thành viên đều có tên trong danh sách
    df_long = df_raw.melt(id_vars=[col_cau_hoi], var_name='Thành viên', value_name='Điểm')
    df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)

    st.header(f"📌 Tuần: {selected_sheet}")
    st.write("---")

    # Hàm vẽ biểu đồ đảm bảo độ to và căn lề đồng nhất
    def ve_bieu_do(cau_hoi_list, tieu_de, mau_sac):
        df_plot = df_long[df_long[col_cau_hoi].isin(cau_hoi_list)]
        
        # Cấu hình biểu đồ
        chart = alt.Chart(df_plot).mark_bar(size=30).encode( # size=30 ép độ to cột cố định
            x=alt.X('Thành viên:N', sort=danh_sach_thanh_vien, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Điểm:Q', axis=alt.Axis(format="d")),
            color=alt.value(mau_sac),
            column=alt.Column(f'{col_cau_hoi}:N', header=alt.Header(title=None)) # Dùng column để cột nằm cạnh nhau
        ).properties(height=300).configure_facet(spacing=20) # Khoảng cách giữa các cột
        
        st.subheader(tieu_de)
        if mau_sac == '#e74c3c': 
            st.warning(f"⚠️ {', '.join(cau_hoi_list)}")
        else:
            st.info(f"💡 {cau_hoi_list[0]}")
            
        st.altair_chart(chart, use_container_width=True)

    danh_sach_cau = df_raw[col_cau_hoi].tolist()

    # Hiển thị
    ve_bieu_do([danh_sach_cau[0]], f"1️⃣ {danh_sach_cau[0]}", '#3498db')
    ve_bieu_do([danh_sach_cau[1]], f"2️⃣ {danh_sach_cau[1]}", '#3498db')
    # Biểu đồ gộp Câu 3 & 4 với màu đỏ và kiểu dáng y hệt
    ve_bieu_do([danh_sach_cau[2], danh_sach_cau[3]], "3️⃣ & 4️⃣ Tiêu chí tiêu cực", '#e74c3c')

    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_raw, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
