import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📊 Hệ thống Theo dõi & Đánh giá Thành viên")

# Link GitHub
file_url = "https://github.com/nmh21102003-a11y/web-danh-gia-du-an/raw/refs/heads/main/Du_Lieu_Danh_Gia.xlsx"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_excel(file_url, sheet_name=None)

# DANH SÁCH TÊN CỐ ĐỊNH (Để thứ tự tên không bao giờ bị nhảy)
fixed_names = ["Nguyễn Tuấn Vinh", "Trần Trang Thảo", "Lưu Hoàng Minh", "Nguyễn Lê Huy", "Mai Việt Dũng", "Trần Quý Giáp", "Đỗ Trung Hiếu", "Hoàng Ngọc Bích", "Lê Danh Toàn", "Đỗ Thành Long"]

try:
    all_sheets = load_data()
    # TỰ ĐỘNG HIỆN LIST CÁC SHEET ĐANG CÓ
    selected_sheet = st.sidebar.selectbox("Chọn Tuần:", list(all_sheets.keys()))
    df = all_sheets[selected_sheet]
    
    # Làm sạch dữ liệu
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')].dropna(how='all')
    col_tieu_chi = df.columns[0]
    
    # Xử lý dữ liệu
    df_long = df.melt(id_vars=[col_tieu_chi], var_name='Thành viên', value_name='Điểm')
    df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)

    def draw_chart(tieu_chi_list, title, color):
        data = df_long[df_long[col_tieu_chi].isin(tieu_chi_list)].groupby('Thành viên', as_index=False)['Điểm'].sum()
        c = alt.Chart(data).mark_bar(size=40).encode(
            x=alt.X('Thành viên:N', sort=fixed_names, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Điểm:Q', axis=alt.Axis(format="d", tickMinStep=1)), 
            color=alt.value(color)
        ).properties(height=300).interactive()
        st.subheader(title)
        st.caption(f"Nội dung: {', '.join(tieu_chi_list)}")
        st.altair_chart(c, use_container_width=True)

    cows = df[col_tieu_chi].unique().tolist()

    # HIỂN THỊ TỰ ĐỘNG THEO SHEET
    if len(cows) > 0: draw_chart([cows[0]], "1️⃣ Tiêu chí 1", '#3498db')
    if len(cows) > 1: draw_chart([cows[1]], "2️⃣ Tiêu chí 2", '#3498db')
    if len(cows) > 2: draw_chart(cows[2:], "3️⃣ & 4️⃣... Các tiêu chí tiêu cực", '#e74c3c')

    with st.expander("📋 Số liệu chi tiết"):
        st.dataframe(df, use_container_width=True, height=300)

except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}")
