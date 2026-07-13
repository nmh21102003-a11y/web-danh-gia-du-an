import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("📊 Hệ thống Đánh giá Thành viên")

file_url = "https://github.com/nmh21102003-a11y/web-danh-gia-du-an/raw/refs/heads/main/Du_Lieu_Danh_Gia.xlsx"

@st.cache_data(ttl=60)
def load_data():
    return pd.read_excel(file_url, sheet_name=None)

try:
    all_sheets = load_data()
    selected_sheet = st.sidebar.selectbox("Tuần:", list(all_sheets.keys()))
    df_raw = all_sheets[selected_sheet]
    df = df_raw.iloc[:, 1:]
    names = df.columns.tolist()
    
    df_long = df_raw.melt(id_vars=[df_raw.columns[0]], var_name='Thành viên', value_name='Điểm')
    df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)

    def chart(rows, color):
        data = df_long[df_long[df_raw.columns[0]].isin(rows)].groupby('Thành viên', as_index=False)['Điểm'].sum()
        c = alt.Chart(data).mark_bar(size=30).encode(
            x=alt.X('Thành viên:N', sort=names, axis=alt.Axis(labelAngle=0)),
            y='Điểm:Q', color=alt.value(color)
        ).properties(height=300).interactive()
        st.altair_chart(c, use_container_width=True)

    cows = df_raw.iloc[:, 0].tolist()

    # Bảng 1
    st.subheader("1️⃣ Tiêu chí 1")
    chart([cows[0]], '#3498db')
    st.caption(f"Note: {cows[0]}")
    
    # Bảng 2
    st.subheader("2️⃣ Tiêu chí 2")
    chart([cows[1]], '#3498db')
    st.caption(f"Note: {cows[1]}")
    
    # Bảng 3 (Gộp 3 & 4)
    st.subheader("3️⃣ Tiêu chí tiêu cực")
    chart([cows[2], cows[3]], '#e74c3c')
    st.caption(f"Note: {cows[2]} & {cows[3]}")

    with st.expander("📋 Số liệu chi tiết"):
        st.dataframe(df_raw, use_container_width=True, height=300)

except Exception:
    st.error("Lỗi dữ liệu!")
