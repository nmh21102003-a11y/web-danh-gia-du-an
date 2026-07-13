import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📊 Hệ thống Đánh giá Hiệu suất Horizon")

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
    danh_sach_thanh_vien = df_raw.columns[1:].tolist()
    
    df_long = df_raw.melt(id_vars=[col_cau_hoi], var_name='Thành viên', value_name='Điểm')
    df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)

    st.header(f"📌 Tuần: {selected_sheet}")
    st.write("---")

    # Hàm vẽ biểu đồ thường (Câu 1, 2)
    def ve_bieu_do_don(cau_hoi, mau_sac):
        df_plot = df_long[df_long[col_cau_hoi] == cau_hoi]
        chart = alt.Chart(df_plot).mark_bar(color=mau_sac).encode(
            x=alt.X('Thành viên:N', sort=danh_sach_thanh_vien, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Điểm:Q', axis=alt.Axis(format="d")) 
        ).properties(width=1000, height=300).interactive()
        
        st.subheader(f"Tiêu chí: {cau_hoi}")
        st.altair_chart(chart, use_container_width=False)

    # Hàm vẽ biểu đồ gộp (Câu 3 + 4)
    def ve_bieu_do_gop(cau_hoi_3, cau_hoi_4):
        df_plot = df_long[df_long[col_cau_hoi].isin([cau_hoi_3, cau_hoi_4])]
        
        chart = alt.Chart(df_plot).mark_bar().encode(
            x=alt.X('Thành viên:N', sort=danh_sach_thanh_vien, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Điểm:Q', axis=alt.Axis(format="d")),
            color=alt.Color(f'{col_cau_hoi}:N', scale=alt.Scale(scheme='set1')), # Tự đổi màu
            column=f'{col_cau_hoi}:N' # Tách cột theo tên câu hỏi
        ).properties(width=450, height=300).interactive()
        
        st.subheader("3️⃣ & 4️⃣ Tiêu chí tiêu cực")
        st.warning(f"⚠️ {cau_hoi_3} & {cau_hoi_4}")
        st.altair_chart(chart, use_container_width=False)

    danh_sach_cau = df_raw[col_cau_hoi].tolist()

    # Hiển thị
    ve_bieu_do_don(danh_sach_cau[0], '#3498db') # Câu 1
    ve_bieu_do_don(danh_sach_cau[1], '#3498db') # Câu 2
    ve_bieu_do_gop(danh_sach_cau[2], danh_sach_cau[3]) # Gộp 3 & 4

    st.write("---")
    with st.expander("📋 Xem Bảng Số Liệu Chi Tiết"):
        st.dataframe(df_raw, use_container_width=True)

except Exception as e:
    st.error(f"Lỗi: {e}")
