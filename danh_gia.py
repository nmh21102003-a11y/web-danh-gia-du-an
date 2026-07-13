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
    df = all_sheets[selected_sheet].iloc[:, 1:] # Bỏ cột tiêu đề
    df_raw = all_sheets[selected_sheet]
    
    names = df.columns.tolist()
    df_long = df_raw.melt(id_vars=[df_raw.columns[0]], var_name='Thành viên', value_name='Điểm')
    df_long['Điểm'] = pd.to_numeric(df_long['Điểm'], errors='coerce').fillna(0)

    def chart(rows, title, color):
        data = df_long[df_long[df_raw.columns[0]].isin(rows)].groupby('Thành viên', as_index=False)['Điểm'].sum()
        c = alt.Chart(data).mark_bar(size=30).encode(
            x=alt.X('Thành viên:N', sort=names, axis=alt.Axis(labelAngle=0)),
            y='Điểm:Q', color=alt.value(color)
        ).properties(height=300).interactive()
        st.subheader(title)
        st.altair_chart(c, use_container_width=True)

    cows = df_raw.iloc[:, 0].tolist()
    chart([cows[0]], f"1️⃣ {cows[0]}", '#3498db')
    chart([cows[1]], f"2️⃣ {cows[1]}", '#3498db')
    
    st.subheader("3️⃣ & 4️⃣ Tổng hợp tiêu cực")
    st.info(f"👉 {cows[2]}\n\n👉 {cows[3]}")
    chart([cows[2], cows[3]], "", '#e74c3c')

    with st.expander("📋 Số liệu chi tiết"):
        st.dataframe(df_raw, use_container_width=True, height=300)

except Exception as e:
    st.error("Lỗi dữ liệu!")
