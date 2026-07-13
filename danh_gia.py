import streamlit as st
import pandas as pd
import altair as alt

# Cấu hình giao diện
st.set_page_config(layout="wide")
st.title("📊 Hệ thống Đánh giá Thành viên")

# Link GitHub
file_url = "https://github.com/nmh21102003-a11y/web-danh-gia-du-an/raw/refs/heads/main/Du_Lieu_Danh_Gia.xlsx"

# Hàm tải dữ liệu
@st.cache_data(ttl=60)
def load_data():
    return pd.read_excel(file_url, sheet_name=None)

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Tuần:", list(all_sheets.keys()))
    df_raw = all_sheets[selected_sheet]
    
    # Làm sạch dữ liệu
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
    names = df_raw.columns[1:].tolist()
    
    # Chuyển dữ liệu sang định dạng long
    df_long = df_raw.melt(id_vars=[df_raw.columns[0]], var_name='Thành viên', value_name='Điểm')
    df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)

    # Hàm vẽ biểu đồ
    def chart(rows, color):
        data = df_long[df_long[df_raw.columns[0]].isin(rows)].groupby('Thành viên', as_index=False)['Điểm'].sum()
        
        c = alt.Chart(data).mark_bar(size=40).encode(
            x=alt.X('Thành viên:N', sort=names, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Điểm:Q', axis=alt.Axis(format="d", tickMinStep=1)), 
            color=alt.value(color)
        ).properties(height=300).interactive()
        st.altair_chart(c, use_container_width=True)

    cows = df_raw.iloc[:, 0].tolist()

    # Hiển thị các mục (Note nằm dưới tiêu đề)
    st.subheader("1️⃣ Tiêu chí 1")
    st.caption(f"**Nội dung:** {cows[0]}")
    chart([cows[0]], '#3498db')
    
    st.subheader("2️⃣ Tiêu chí 2")
    st.caption(f"**Nội dung:** {cows[1]}")
    chart([cows[1]], '#3498db')
    
    st.subheader("3️⃣ Tiêu chí tiêu cực")
    st.caption(f"**Nội dung:** {cows[2]} & {cows[3]}")
    chart([cows[2], cows[3]], '#e74c3c')

    # Bảng chi tiết
    with st.expander("📋 Số liệu chi tiết"):
        st.dataframe(df_raw, use_container_width=True, height=300)

except Exception as e:
    st.error(f"Đang tải dữ liệu, vui lòng đợi hoặc kiểm tra file: {e}")
